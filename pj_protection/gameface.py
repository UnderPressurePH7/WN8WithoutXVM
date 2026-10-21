from __future__ import annotations

import os
import pathlib
import re
import shutil
import subprocess
import tempfile
from typing import List


_HERE = pathlib.Path(__file__).resolve().parent
_OBFUSCATOR_HOME = pathlib.Path(r'D:\_Vasyl\Program Files\javascript-obfuscator')


def minify_html(text: str) -> str:
    text = re.sub(r'<!--(?!\[if)[\s\S]*?-->', '', text)
    text = re.sub(r'>\s+<', '><', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n\s*', '', text)
    return text.strip()


def _javascript_obfuscator_command() -> List[str]:
    node = shutil.which('node') or shutil.which('node.exe')
    homes = []
    configured = os.environ.get('JAVASCRIPT_OBFUSCATOR_HOME')
    if configured:
        homes.append(pathlib.Path(configured))
    homes.extend((_HERE / 'javascript-obfuscator', _OBFUSCATOR_HOME))
    for home in homes:
        launcher = home / 'bin' / 'javascript-obfuscator'
        if launcher.is_file() and (home / 'dist' / 'index.cli.js').is_file() and \
                (home / 'node_modules').is_dir():
            if not node:
                raise RuntimeError('Node.js is required for javascript-obfuscator')
            return [node, str(launcher)]
    direct = shutil.which('javascript-obfuscator') or shutil.which('javascript-obfuscator.cmd')
    if direct:
        return [direct]
    local = pathlib.Path('node_modules') / '.bin' / 'javascript-obfuscator.cmd'
    if local.is_file():
        return [str(local.resolve())]
    raise RuntimeError('A local javascript-obfuscator installation is required; '
                       'set JAVASCRIPT_OBFUSCATOR_HOME to its directory')


def obfuscate_js(path: pathlib.Path) -> None:
    command = _javascript_obfuscator_command()
    fd, tmp_name = tempfile.mkstemp(prefix='moe_js_', suffix='.js')
    os.close(fd)
    output = pathlib.Path(tmp_name)
    try:
        args = command + [
            str(path),
            '--output', str(output),
            '--compact', 'true',
            '--identifier-names-generator', 'hexadecimal',
            '--rename-globals', 'false',
            '--control-flow-flattening', 'false',
            '--dead-code-injection', 'false',
            '--self-defending', 'false',
            '--string-array', 'true',
            '--string-array-encoding', 'base64',
            '--string-array-threshold', '0.80',
            '--string-array-shuffle', 'true',
            '--string-array-rotate', 'true',
            '--transform-object-keys', 'false',
            '--unicode-escape-sequence', 'false',
        ]
        completed = subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=300,
        )
        if completed.returncode != 0 or not output.is_file() or output.stat().st_size == 0:
            raise RuntimeError('javascript-obfuscator failed for %s\n%s' %
                               (path, completed.stdout or ''))
        shutil.copy2(str(output), str(path))
    finally:
        try:
            output.unlink()
        except OSError:
            pass


def obfuscate_text(text: str) -> str:
    fd, tmp_name = tempfile.mkstemp(prefix='moe_source_', suffix='.js')
    os.close(fd)
    source = pathlib.Path(tmp_name)
    try:
        source.write_text(text, encoding='utf-8', newline='')
        obfuscate_js(source)
        return source.read_text(encoding='utf-8')
    finally:
        try:
            source.unlink()
        except OSError:
            pass

