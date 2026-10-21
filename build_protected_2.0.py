from __future__ import annotations

import os
import pathlib
import shutil
import sys
import tempfile
import zipfile

import build
from pj_protection import co_names
from pj_protection import gameface
from pj_protection import python as python_protection


_ROOT = pathlib.Path(__file__).resolve().parent
_PYTHON_ROOT = _ROOT / 'python'
_RESOURCE_ROOT = _ROOT / 'resources' / 'in'
_PJORION_TIMEOUT = 900
_CO_NAMES_TIMEOUT = 300
_staged_python = None
_staged_resources = None
_protected_bytecode = []
_original_copytree = build.copytree
_original_zip_folder = build.zip_folder


def _build_python(config: build.AppConfig) -> None:
    global _protected_bytecode
    if not config.software.python:
        raise RuntimeError('Python 2.7 executable is not configured in build.json')
    co_names._check_python(pathlib.Path(config.software.python).resolve())
    python_protection._ensure_exe()
    outputs = python_protection.protect_tree(
        _staged_python, timeout=_PJORION_TIMEOUT, logger=build.logger,
        use_protect_layer=False)
    outputs = co_names.protect_tree(
        outputs, python_executable=config.software.python,
        timeout=_CO_NAMES_TIMEOUT, logger=build.logger)
    _protected_bytecode = python_protection.protect_bytecode_tree(
        outputs, timeout=_PJORION_TIMEOUT, logger=build.logger)


def _copytree(source, destination, ignore=None):
    source_path = pathlib.Path(source)
    if source_path == pathlib.Path('python'):
        source = str(_staged_python)
    elif source_path == pathlib.Path('resources/in'):
        source = str(_staged_resources)
    return _original_copytree(source, destination, ignore)


def _zip_folder(source, destination, mode='w', compression=None):
    destination = pathlib.Path(destination)
    if destination.suffix.lower() == '.wotmod':
        if not _protected_bytecode:
            raise RuntimeError('Protected Python bytecode was not generated')
        try:
            if compression is None:
                result = _original_zip_folder(source, destination, mode)
            else:
                result = _original_zip_folder(source, destination, mode, compression)
            python_protection.audit_archive(
                destination, _staged_python, _protected_bytecode)
            _audit_javascript_archive(destination)
            build.logger.info('Protected archive verified: %s', destination)
            return result
        except Exception:
            destination.unlink(missing_ok=True)
            raise
    if compression is None:
        return _original_zip_folder(source, destination, mode)
    return _original_zip_folder(source, destination, mode, compression)


def _audit_javascript_archive(path: pathlib.Path) -> None:
    expected = set()
    for source in _staged_resources.rglob('*.js'):
        expected.add('res/' + source.relative_to(_staged_resources).as_posix())
    with zipfile.ZipFile(str(path), 'r') as archive:
        names = set(archive.namelist())
        missing = sorted(expected - names)
        if missing:
            raise RuntimeError('Protected archive is missing JavaScript: %s' %
                               ', '.join(missing))
        for source in _staged_resources.rglob('*.js'):
            archived_name = 'res/' + source.relative_to(_staged_resources).as_posix()
            archived = archive.read(archived_name)
            if archived != source.read_bytes():
                raise RuntimeError('Archived JavaScript differs from obfuscated file: %s' %
                                   archived_name)


def main() -> int:
    global _staged_python, _staged_resources, _protected_bytecode
    original_build_python = build.build_python
    original_copytree = build.copytree
    original_zip_folder = build.zip_folder
    original_directory = pathlib.Path.cwd()
    _protected_bytecode = []
    build.logger = build.setup_logger()
    try:
        os.chdir(_ROOT)
        with tempfile.TemporaryDirectory(prefix='wn8_protected_') as temporary:
            staging = pathlib.Path(temporary)
            _staged_python = staging / 'python'
            shutil.copytree(_PYTHON_ROOT, _staged_python,
                            ignore=shutil.ignore_patterns('*.pyc', '*.pyo', '__pycache__'))
            _staged_resources = staging / 'resources' / 'in'
            if _RESOURCE_ROOT.is_dir():
                shutil.copytree(_RESOURCE_ROOT, _staged_resources)
                for script in sorted(_staged_resources.rglob('*.js')):
                    gameface.obfuscate_js(script)
                    build.logger.info('JavaScript obfuscated: %s',
                                      script.relative_to(_staged_resources))
            build.build_python = _build_python
            build.copytree = _copytree
            build.zip_folder = _zip_folder
            build.main()
    except Exception as exc:
        build.logger.exception('Protected build failed: %s', exc)
        return 1
    finally:
        build.build_python = original_build_python
        build.copytree = original_copytree
        build.zip_folder = original_zip_folder
        _staged_python = None
        _staged_resources = None
        os.chdir(original_directory)
    return 0


if __name__ == '__main__':
    sys.exit(main())
