from __future__ import annotations

import hashlib
import os
import pathlib
import re
import shutil
import subprocess
import tempfile
import zipfile
from typing import Dict, List, Optional


_PJ_HOME = pathlib.Path(os.environ.get(
    'PJORION_HOME', r'D:\_Vasyl\Program Files\PjOrion_1.3.5_11.08.2019'))
_PJ_EXE = _PJ_HOME / 'PjOrion.exe'
_PJ_DLL = _PJ_EXE.parent / 'python27.dll'
_PY27_MAGIC = b'\x03\xf3\x0d\x0a'
_EXPECTED_SHA = 'aecca1ade73418b37e27669d8b4caba386bbc860ea7ed73d7f1aa6e7920738aa'
_EXPECTED_SHAS = (_EXPECTED_SHA, 'c2fa97f5d1f5f82c575e246faef4cff7c59a42ff4257d6097339060de8b32454', '8f854fea20918504f2ab8868fafd2fe24724343418cb6eaf2bf94fb6c68d2136', 'aae3fda83b89388e58bc2f6e3231ccbedfb3c354b5b82661a2202a6ef9d957f0', '0001a8bfd677ea00263dc65f40df51a91a610fbd720c658f5360cd84e7e501e6')
_EXPECTED_DLL_SHA = '2eeacd23488872abf4d7d17ce8705fd445f6537b33aa9e6768da96bf15666825'


def _log(logger, message: str, *args) -> None:
    if logger is not None:
        logger.info(message, *args)


def _ensure_exe() -> pathlib.Path:
    if not _PJ_EXE.is_file():
        raise RuntimeError('PjOrion.exe not found: %s' % _PJ_EXE)
    digest = hashlib.sha256(_PJ_EXE.read_bytes()).hexdigest()
    if digest not in _EXPECTED_SHAS:
        raise RuntimeError('PjOrion.exe hash mismatch: %s' % digest)
    if not _PJ_DLL.is_file():
        raise RuntimeError('PjOrion python27.dll not found: %s' % _PJ_DLL)
    dll_digest = hashlib.sha256(_PJ_DLL.read_bytes()).hexdigest()
    if dll_digest != _EXPECTED_DLL_SHA:
        raise RuntimeError('PjOrion python27.dll hash mismatch: %s' % dll_digest)
    return _PJ_EXE


def _stage_runtime(exe: pathlib.Path):
    stage_root = pathlib.Path(tempfile.mkdtemp(prefix='moepj_runtime_'))
    stage_dir = stage_root / 'runtime'
    shutil.copytree(str(exe.parent), str(stage_dir))
    staged_exe = stage_dir / exe.name
    ini_path = stage_dir / 'PjOrion.ini'
    if ini_path.is_file():
        ini_text = ini_path.read_text(encoding='utf-8', errors='replace')
        ini_text, count = re.subn(
            r'(?m)^CheckWebUpdate=.*$', 'CheckWebUpdate=0', ini_text, count=1)
        if count != 1:
            shutil.rmtree(str(stage_root), ignore_errors=True)
            raise RuntimeError('PjOrion.ini CheckWebUpdate option was not found')
        ini_path.write_text(ini_text, encoding='utf-8', newline='\r\n')
    if ' ' in str(staged_exe):
        shutil.rmtree(str(stage_root), ignore_errors=True)
        raise RuntimeError('PjOrion runtime path contains spaces: %s' % staged_exe)
    return staged_exe, stage_root


def _run(exe: pathlib.Path, switch: str, target: str, timeout: int) -> str:
    # PjOrion parses the raw Windows command line and expects the value to be
    # quoted even when the staged file name itself contains no spaces.
    command = '"%s" %s="%s" /exit' % (exe, switch, target)
    try:
        completed = subprocess.run(
            command,
            cwd=str(exe.parent),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        output = exc.stdout or exc.stderr or ''
        if isinstance(output, bytes):
            output = output.decode('utf-8', errors='replace')
        raise RuntimeError(
            'PjOrion %s timed out after %s seconds for %s. '
            'Close any PjOrion dialog/window and retry.\n%s' %
            (switch, timeout, target, output)) from exc
    if completed.returncode != 0:
        raise RuntimeError('PjOrion %s failed for %s (exit %s)\n%s' %
                           (switch, target, completed.returncode, completed.stdout or ''))
    return completed.stdout or ''


def _check_pyc(path: pathlib.Path) -> None:
    if not path.is_file() or path.stat().st_size <= 8:
        raise RuntimeError('Protected PYC missing or too small: %s' % path)
    magic = path.read_bytes()[:4]
    if magic != _PY27_MAGIC:
        raise RuntimeError('Unexpected Python bytecode magic for %s: %r' % (path, magic))


def protect_source(source: pathlib.Path, source_text: Optional[str] = None,
                   exe: Optional[pathlib.Path] = None, timeout: int = 900,
                   logger=None, use_protect_layer: bool = True) -> pathlib.Path:
    runtime_root = None
    if exe is None:
        exe, runtime_root = _stage_runtime(_ensure_exe())
    source = pathlib.Path(source).resolve()
    output = source.with_suffix('.pyc')
    work_source = exe.parent / 'input' / source.name
    work_source.parent.mkdir(parents=True, exist_ok=True)
    work_output = work_source.with_suffix('.pyc')
    try:
        if work_source.is_file():
            work_source.unlink()
        if work_output.is_file():
            work_output.unlink()
        if source_text is None:
            shutil.copy2(str(source), str(work_source))
        else:
            work_source.write_text(source_text, encoding='utf-8', newline='\n')
        obfuscate_output = _run(exe, '--obfuscate-bytecode-file', str(work_source), timeout)
        try:
            _check_pyc(work_output)
        except RuntimeError as exc:
            raise RuntimeError('%s\n%s' % (exc, obfuscate_output))
        if use_protect_layer:
            obfuscated_digest = hashlib.sha256(work_output.read_bytes()).digest()
            protect_output = _run(exe, '--protect-bytecode-file', str(work_output), timeout)
            try:
                _check_pyc(work_output)
            except RuntimeError as exc:
                raise RuntimeError('%s\n%s' % (exc, protect_output))
            if hashlib.sha256(work_output.read_bytes()).digest() == obfuscated_digest:
                raise RuntimeError('PjOrion protect-bytecode did not modify %s' % work_output.name)
        shutil.copy2(str(work_output), str(output))
    finally:
        if runtime_root is not None:
            shutil.rmtree(str(runtime_root), ignore_errors=True)
    _check_pyc(output)
    operation = 'protected' if use_protect_layer else 'bytecode-obfuscated'
    _log(logger, 'PjOrion %s: %s (%d bytes)', operation, source, output.stat().st_size)
    return output


def cleanup_bytecode(root: pathlib.Path) -> None:
    for path in pathlib.Path(root).rglob('*.pyc'):
        try:
            path.unlink()
        except OSError:
            pass


def protect_tree(root: pathlib.Path, overrides: Optional[Dict[pathlib.Path, str]] = None,
                 timeout: int = 900, logger=None,
                 use_protect_layer: bool = True) -> List[pathlib.Path]:
    root = pathlib.Path(root).resolve()
    sources = sorted(root.rglob('*.py'))
    if not sources:
        raise RuntimeError('No Python sources found under %s' % root)
    cleanup_bytecode(root)
    exe, runtime_root = _stage_runtime(_ensure_exe())
    normalized = {pathlib.Path(path).resolve(): text for path, text in (overrides or {}).items()}
    _log(logger, 'PjOrion runtime: %s', exe)
    work_root = exe.parent / 'input'
    work_root.mkdir()
    produced = []
    staged_sources = {}
    try:
        # One flat input folder avoids relying on PjOrion's subfolder traversal.
        # Unique temporary names also prevent collisions between package __init__ files.
        for index, source in enumerate(sources):
            staged_source = work_root / ('module_%04d.py' % index)
            staged_sources[source] = staged_source
            text = normalized.get(source.resolve())
            if text is None:
                shutil.copy2(source, staged_source)
            else:
                staged_source.write_text(text, encoding='utf-8', newline='\n')
        _log(logger, 'PjOrion --obfuscate-bytecode-folder: %d sources', len(sources))
        operation_output = _run(exe, '--obfuscate-bytecode-folder', str(work_root), timeout)
        for source in sources:
            staged_output = staged_sources[source].with_suffix('.pyc')
            try:
                _check_pyc(staged_output)
            except RuntimeError as exc:
                raise RuntimeError('%s\n%s' % (exc, operation_output)) from exc
            output = source.with_suffix('.pyc')
            shutil.copy2(staged_output, output)
            produced.append(output)
            _log(logger, 'PjOrion bytecode-obfuscated: %s (%d bytes)',
                 source.relative_to(root), output.stat().st_size)
    finally:
        shutil.rmtree(str(runtime_root), ignore_errors=True)
    if len(produced) != len(sources):
        raise RuntimeError('Not every Python source was protected')
    if use_protect_layer:
        return protect_bytecode_tree(produced, timeout=timeout, logger=logger)
    return produced


def protect_bytecode_tree(paths: List[pathlib.Path], timeout: int = 900,
                          logger=None) -> List[pathlib.Path]:
    """Apply only the outer PjOrion protect layer to existing Python 2.7 PYC files."""
    targets = sorted({pathlib.Path(path).resolve() for path in paths})
    if not targets:
        raise RuntimeError('No PYC files were supplied to PjOrion protect layer')

    exe, runtime_root = _stage_runtime(_ensure_exe())
    _log(logger, 'PjOrion outer protect runtime: %s', exe)
    work_root = exe.parent / 'input'
    work_root.mkdir()
    originals = {}
    staged_outputs = {}
    try:
        for index, target in enumerate(targets):
            _check_pyc(target)
            originals[target] = target.read_bytes()
            work_output = work_root / ('module_%04d.pyc' % index)
            staged_outputs[target] = work_output
            shutil.copy2(target, work_output)
        _log(logger, 'PjOrion --protect-bytecode-folder: %d files', len(targets))
        protect_output = _run(exe, '--protect-bytecode-folder', str(work_root), timeout)
        for target in targets:
            work_output = staged_outputs[target]
            try:
                _check_pyc(work_output)
            except RuntimeError as exc:
                raise RuntimeError('%s\n%s' % (exc, protect_output))

            protected = work_output.read_bytes()
            original = originals[target]
            if hashlib.sha256(protected).digest() == hashlib.sha256(original).digest():
                raise RuntimeError(
                    'PjOrion protect-bytecode did not modify %s' % target)
            shutil.copy2(str(work_output), str(target))
            _check_pyc(target)
            _log(logger, 'PjOrion outer-protected: %s (%d -> %d bytes)',
                 target, len(original), target.stat().st_size)
    finally:
        shutil.rmtree(str(runtime_root), ignore_errors=True)
    return targets


def audit_archive(archive_path: pathlib.Path, python_root: pathlib.Path,
                  protected_files: List[pathlib.Path]) -> None:
    """Verify that the archive contains the exact final outer-protected bytecode."""
    archive_path = pathlib.Path(archive_path)
    python_root = pathlib.Path(python_root).resolve()
    expected = {}
    for source in protected_files:
        source = pathlib.Path(source).resolve()
        _check_pyc(source)
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
        leaked_sources = sorted(
            name for name in names
            if name.startswith('res/scripts/client/') and
            name.endswith(('.pyc', '.pyo')) and name not in expected)
        if leaked_sources:
            raise RuntimeError('Protected archive contains unregistered bytecode: %s' %
                               ', '.join(leaked_sources))
        leaked_sources = sorted(
            name for name in names
            if name.startswith('res/scripts/client/') and name.endswith('.py'))
        if leaked_sources:
            raise RuntimeError('Protected archive contains Python sources: %s' %
                               ', '.join(leaked_sources))
        for name, source in sorted(expected.items()):
            archived = archive.read(name)
            _check_pyc_bytes(archived, name)
            if hashlib.sha256(archived).digest() != hashlib.sha256(
                    source.read_bytes()).digest():
                raise RuntimeError(
                    'Archived bytecode differs from final protected file: %s' % name)


def _check_pyc_bytes(raw: bytes, label: str) -> None:
    if len(raw) <= 8:
        raise RuntimeError('PYC is missing or too small: %s' % label)
    if raw[:4] != _PY27_MAGIC:
        raise RuntimeError('Unexpected Python bytecode magic for %s: %r' %
                           (label, raw[:4]))

