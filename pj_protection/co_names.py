from __future__ import annotations

import hashlib
import pathlib
import subprocess
import tempfile
import zipfile
from typing import Iterable, List

from .carrier_template import load_template


_HERE = pathlib.Path(__file__).resolve().parent
_WORKER = _HERE / 'co_names_py27.py'
_PY27_MAGIC = b'\x03\xf3\x0d\x0a'
_MARKER_PREFIX = b'\x01\x09 \x07\x06'
_MAX_COMMAND_CHARS = 24000


def _log(logger, message: str, *args) -> None:
    if logger is not None:
        logger.info(message, *args)


def _check_python(python_executable: pathlib.Path) -> None:
    if not python_executable.is_file():
        raise RuntimeError('Python 2.7 executable not found: %s' % python_executable)
    completed = subprocess.run(
        [str(python_executable), '-c',
         "import sys; sys.stdout.write('%d.%d' % sys.version_info[:2])"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding='ascii',
        errors='replace',
        timeout=30,
    )
    if completed.returncode != 0 or completed.stdout.strip() != '2.7':
        raise RuntimeError('Configured interpreter is not Python 2.7: %s (%s)' %
                           (python_executable, completed.stdout.strip()))


def _check_pyc(path: pathlib.Path) -> None:
    if not path.is_file() or path.stat().st_size <= 8:
        raise RuntimeError('PYC is missing or too small: %s' % path)
    if path.read_bytes()[:4] != _PY27_MAGIC:
        raise RuntimeError('Unexpected Python bytecode magic: %s' % path)


def _batches(paths: List[pathlib.Path]) -> Iterable[List[pathlib.Path]]:
    batch: List[pathlib.Path] = []
    size = 0
    for path in paths:
        item_size = len(str(path)) + 3
        if batch and size + item_size > _MAX_COMMAND_CHARS:
            yield batch
            batch = []
            size = 0
        batch.append(path)
        size += item_size
    if batch:
        yield batch


def protect_tree(paths: Iterable[pathlib.Path],
                 python_executable: pathlib.Path | str, timeout: int = 300,
                 logger=None) -> List[pathlib.Path]:
    python_executable = pathlib.Path(python_executable).resolve()
    targets = sorted({pathlib.Path(path).resolve() for path in paths})
    if not targets:
        raise RuntimeError('No PYC files were supplied to co_names protection')
    if not _WORKER.is_file():
        raise RuntimeError('Python 2.7 co_names worker not found: %s' % _WORKER)
    _check_python(python_executable)

    before = {}
    for target in targets:
        _check_pyc(target)
        before[target] = hashlib.sha256(target.read_bytes()).digest()

    with tempfile.TemporaryDirectory(prefix='pj_co_names_') as temp_root:
        template = pathlib.Path(temp_root) / 'carrier.pyc'
        template.write_bytes(load_template())
        _check_pyc(template)
        for batch in _batches(targets):
            command = [str(python_executable), str(_WORKER),
                       '--template', str(template)] + [str(path) for path in batch]
            completed = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=timeout,
            )
            if completed.returncode != 0:
                raise RuntimeError('co_names protection failed (exit %s)\n%s' %
                                   (completed.returncode, completed.stdout or ''))
            if completed.stdout:
                for line in completed.stdout.splitlines():
                    _log(logger, '%s', line)

    for target in targets:
        _check_pyc(target)
        raw = target.read_bytes()
        if hashlib.sha256(raw).digest() == before[target]:
            raise RuntimeError('co_names protection did not modify %s' % target)
        if raw.count(_MARKER_PREFIX) < 107:
            raise RuntimeError('co_names marker set is missing from %s' % target)
    _log(logger, 'co_names protection verified: %d files', len(targets))
    return targets


def audit_archive(archive_path: pathlib.Path, python_root: pathlib.Path,
                  protected_files: Iterable[pathlib.Path]) -> None:
    python_root = pathlib.Path(python_root).resolve()
    expected = {}
    for source in protected_files:
        source = pathlib.Path(source).resolve()
        relative = source.relative_to(python_root).as_posix()
        expected['res/scripts/client/' + relative] = source
    if not expected:
        raise RuntimeError('No protected Python files were registered for archive audit')

    with zipfile.ZipFile(str(archive_path), 'r') as archive:
        names = set(archive.namelist())
        missing = sorted(set(expected) - names)
        if missing:
            raise RuntimeError('Protected archive is missing Python bytecode: %s' %
                               ', '.join(missing))
        for name in sorted(expected):
            raw = archive.read(name)
            if raw[:4] != _PY27_MAGIC:
                raise RuntimeError('Archive contains invalid Python 2.7 PYC: %s' % name)
            if raw.count(_MARKER_PREFIX) < 107:
                raise RuntimeError('Archive PYC is not co_names protected: %s' % name)

