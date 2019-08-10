#!/usr/bin/env python3
# ----------------------------------------------------------------------------
# patchman.py
#
# Written by Manuel Gebele (m.gebele‹ατ›tuta.io)
# This code is licensed under the MIT License (MIT). 
# ----------------------------------------------------------------------------
import sys
import json
from enum import Enum
from argparse import ArgumentParser, SUPPRESS

PatchType = Enum('PatchType', 'replace offset')

def read_patches_at_path(patches_path):
    with open(patches_path) as json_file:
        data = json.load(json_file)
    patches = data['patches']
    return patches

def get_patch_type(patch):
    if 'offset' not in patch:
        return PatchType.replace
    return PatchType.offset

def apply_patch_by_search_and_replace(patch, bin_bytes):
    orig_bytes, patched_bytes = (
        bytearray.fromhex(patch['orig_bytes']),
        bytearray.fromhex(patch['patched_bytes'])
    )

    idx = bin_bytes.find(orig_bytes)
    if idx != -1:
        print('[patchman::dbg] Applying patch 0x%s at offset %s'
            % (patched_bytes.hex(), hex(idx)))
        bin_bytes = bin_bytes.replace(orig_bytes, patched_bytes)
    else:
        print('[patchman::err] Couldn\'t find byte sequence (0x%s). '
              'Skipping patch...' % orig_bytes.hex())

    return bin_bytes

def apply_patch_by_offset(patch, bin_bytes):
    patch_offset, patched_bytes = (
        int(patch['offset'], 16),
        bytearray.fromhex(patch['patched_bytes']),
    )

    patch_len = len(patched_bytes)
    slice_end = patch_offset + patch_len
    
    orig_bytes = bin_bytes[patch_offset:slice_end].hex()
    patch['orig_bytes'] = orig_bytes

    return apply_patch_by_search_and_replace(patch, bin_bytes)

def apply_patch(patch, bin_bytes):
    patch_type = get_patch_type(patch)
    if patch_type == PatchType.replace:
        bin_bytes = apply_patch_by_search_and_replace(patch, bin_bytes)
    else:
        bin_bytes = apply_patch_by_offset(patch, bin_bytes)
    return bin_bytes

def open_binary(args):
    bin_path = args.binary
    bin_file = open(bin_path, 'r+b')
    bin_bytes = bin_file.read()
    bin_file.seek(0)

    return (bin_file, bin_bytes)

def apply_patches_at_path(args):
    bin_file, bin_bytes = open_binary(args)

    patches = read_patches_at_path(args.patches_path)
    for patch in patches:
        bin_bytes = apply_patch(patch, bin_bytes)

    bin_file.write(bin_bytes)
    bin_file.close()

def apply_patch_from_cmdline(args):
    bin_file, bin_bytes = open_binary(args)

    patch = dict()
    if args.replace_patch_info:
        patch['orig_bytes'], patch['patched_bytes'] = args.replace_patch_info
    else:
        patch['offset'], patch['patched_bytes'] = args.offset_patch_info

    bin_bytes = apply_patch(patch, bin_bytes)

    bin_file.write(bin_bytes)
    bin_file.close()

def parse_args():
    parser = ArgumentParser(
        description='A bare-metal binary modification tool',
        add_help=False
    )

    parser.add_argument('binary', help='binary to patch')
    parser.add_argument('-h', action='help', default=SUPPRESS,
        help='show this help message and exit')
    parser.add_argument('-v',
        action='version', version='1.0')

    arg_group = parser.add_argument_group(
        'patching arguments',
        'one of the arguments -r -o -f is required'
    )

    me_group = arg_group.add_mutually_exclusive_group(required=True)
    me_group.add_argument('-r',
        nargs=2, metavar=('ORIG', 'PATCH'), dest='replace_patch_info',
        help='replaces ORIG bytes with PATCH bytes')
    me_group.add_argument('-o',
        nargs=2, metavar=('OFFS', 'PATCH'), dest='offset_patch_info',
        help='replaces the bytes starting at offset OFFS with PATCH bytes')
    me_group.add_argument('-f',
        metavar='PATH', dest='patches_path',
        help='reads the patch definitions from the JSON file at path PATH')

    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    if args.replace_patch_info or args.offset_patch_info:
        apply_patch_from_cmdline(args)
    else:
        apply_patches_at_path(args)

# Entry point

main()
