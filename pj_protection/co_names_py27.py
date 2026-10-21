# -*- coding: utf-8 -*-
from __future__ import print_function

import argparse
import marshal
import os
import sys
import types
from itertools import cycle, izip


PY27_MAGIC = '\x03\xf3\x0d\x0a'
PYC_HEADER_SIZE = 8
PREFIX = '\x01\x09 \x07\x06'
KEY = '\x06$'
SLOT_COUNT = 107


def _marker_index(value):
    if not isinstance(value, str) or len(value) < 10 or not value.startswith(PREFIX):
        return None
    return ord(value[5])


def _collect_object(value, markers):
    if isinstance(value, types.CodeType):
        _collect_code(value, markers)
        return
    if isinstance(value, (tuple, list, set, frozenset)):
        for item in value:
            _collect_object(item, markers)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            _collect_object(key, markers)
            _collect_object(item, markers)
        return
    index = _marker_index(value)
    if index is None:
        return
    previous = markers.get(index)
    if previous is not None and previous != value:
        raise RuntimeError('Template contains different markers for slot %d' % index)
    markers[index] = value


def _collect_code(code, markers):
    _collect_object(code.co_consts, markers)
    _collect_object(code.co_names, markers)
    _collect_object(code.co_varnames, markers)
    _collect_object(code.co_freevars, markers)
    _collect_object(code.co_cellvars, markers)
    _collect_object(code.co_name, markers)


def _xor_chunk(data):
    return ''.join(chr(ord(left) ^ ord(right))
                   for left, right in izip(data, cycle(KEY)))


def _replace_object(value, replacements):
    if isinstance(value, types.CodeType):
        return _replace_code(value, replacements)
    index = _marker_index(value)
    if index is not None:
        try:
            return replacements[index]
        except KeyError:
            raise RuntimeError('Missing replacement for marker slot %d' % index)
    if isinstance(value, tuple):
        return tuple(_replace_object(item, replacements) for item in value)
    if isinstance(value, list):
        return [_replace_object(item, replacements) for item in value]
    if isinstance(value, set):
        return set(_replace_object(item, replacements) for item in value)
    if isinstance(value, frozenset):
        return frozenset(_replace_object(item, replacements) for item in value)
    if isinstance(value, dict):
        return dict((_replace_object(key, replacements),
                     _replace_object(item, replacements))
                    for key, item in value.items())
    return value


def _replace_code(code, replacements):
    return types.CodeType(
        code.co_argcount,
        code.co_nlocals,
        code.co_stacksize,
        code.co_flags,
        code.co_code,
        _replace_object(code.co_consts, replacements),
        _replace_object(code.co_names, replacements),
        _replace_object(code.co_varnames, replacements),
        code.co_filename,
        _replace_object(code.co_name, replacements),
        code.co_firstlineno,
        code.co_lnotab,
        _replace_object(code.co_freevars, replacements),
        _replace_object(code.co_cellvars, replacements),
    )


def _read_pyc(path):
    with open(path, 'rb') as stream:
        raw = stream.read()
    if len(raw) <= PYC_HEADER_SIZE:
        raise RuntimeError('PYC is missing or too small: %s' % path)
    if raw[:4] != PY27_MAGIC:
        raise RuntimeError('Not a Python 2.7 PYC: %s' % path)
    try:
        code = marshal.loads(raw[PYC_HEADER_SIZE:])
    except Exception as error:
        raise RuntimeError('Cannot load PYC %s: %s' % (path, error))
    if not isinstance(code, types.CodeType):
        raise RuntimeError('Top-level marshal object is not code: %s' % path)
    return raw, code


def _load_template(path):
    raw, code = _read_pyc(path)
    markers = {}
    _collect_code(code, markers)
    expected = range(SLOT_COUNT)
    if sorted(markers) != expected:
        missing = sorted(set(expected) - set(markers))
        extra = sorted(set(markers) - set(expected))
        raise RuntimeError('Invalid carrier marker set; missing=%r extra=%r' %
                           (missing, extra))
    return raw[:PYC_HEADER_SIZE], code, markers


def _decode_carrier(code):
    markers = {}
    _collect_code(code, markers)
    if sorted(markers) != range(SLOT_COUNT):
        raise RuntimeError('Packed carrier does not contain all marker slots')
    parts = dict((index, markers[index][6:-4]) for index in range(SLOT_COUNT))
    blob = ''.join(_xor_chunk(value) for _, value in parts.items())[::-1]
    try:
        return marshal.loads(blob)
    except Exception as error:
        raise RuntimeError('Packed carrier payload is invalid: %s' % error)


def _pack_code(template_code, template_markers, payload):
    reversed_blob = marshal.dumps(payload)[::-1]
    order = [index for index, _ in
             dict((index, None) for index in range(SLOT_COUNT)).items()]
    replacements = {}
    for position, index in enumerate(order):
        start = position * len(reversed_blob) // SLOT_COUNT
        end = (position + 1) * len(reversed_blob) // SLOT_COUNT
        encrypted = _xor_chunk(reversed_blob[start:end])
        replacements[index] = (PREFIX + chr(index) + encrypted +
                               template_markers[index][-4:])
    packed = _replace_code(template_code, replacements)
    decoded = _decode_carrier(packed)
    if marshal.dumps(decoded) != marshal.dumps(payload):
        raise RuntimeError('Carrier round-trip verification failed')
    return packed


def pack_file(path, template_header, template_code, template_markers):
    original, payload = _read_pyc(path)
    packed_code = _pack_code(template_code, template_markers, payload)
    serialized = marshal.dumps(packed_code)
    persisted_code = marshal.loads(serialized)
    persisted_payload = _decode_carrier(persisted_code)
    if marshal.dumps(persisted_payload) != marshal.dumps(payload):
        raise RuntimeError('Serialized carrier round-trip verification failed')
    protected = template_header + serialized
    if protected == original:
        raise RuntimeError('Carrier did not modify PYC: %s' % path)
    try:
        with open(path, 'wb') as stream:
            stream.write(protected)
            stream.flush()
            os.fsync(stream.fileno())
    except Exception:
        with open(path, 'wb') as stream:
            stream.write(original)
        raise
    print('co_names protected: %s (%d -> %d bytes)' %
          (path, len(original), len(protected)))


def main():
    parser = argparse.ArgumentParser(
        description='Wrap Python 2.7 PYC files in a player_rankings-style carrier.')
    parser.add_argument('--template', required=True, help='Original carrier PYC')
    parser.add_argument('targets', nargs='+', help='PYC files to protect in place')
    args = parser.parse_args()

    header, template_code, markers = _load_template(args.template)
    for target in args.targets:
        pack_file(os.path.abspath(target), header, template_code, markers)
    return 0


if __name__ == '__main__':
    sys.exit(main())

