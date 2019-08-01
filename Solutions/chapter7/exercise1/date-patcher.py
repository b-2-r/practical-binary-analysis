# ----------------------------------------------------------------------------
# date-patcher.py
#
# Written by Manuel Gebele (m.gebele‹ατ›tuta.io)
# This code is licensed under the MIT License (MIT). 
# ----------------------------------------------------------------------------
import os
import shutil
import subprocess

# The 24 byte default format string '%a %b %e %H:%M:%S %Z %Y'.
FORMAT_STRING_BYTES = (
    b'\x25\x61\x20\x25\x62\x20'
    b'\x25\x65\x20\x25\x48\x3a'
    b'\x25\x4d\x3a\x25\x53\x20'
    b'\x25\x5a\x20\x25\x59\x00'
)

# The modified default format string padded with 0 bytes '%H:%M:%S'.
MODIFIED_FORMAT_STRING_BYTES = (
    b'\x25\x48\x3A\x25\x4D\x3A'
    b'\x25\x53\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\x00'
)

# The 'mov edi, 0x2006c' instruction.
NL_LANGINFO_ITEM_BYTES = b'\xbf\x6c\x00\x02\x00'

# The modified mov instruction (mov edi, 0xffffffff).
MODIFIED_NL_LANGINFO_ITEM_BYTES = b'\xbf\xff\xff\xff\xff'

def date_path():
    which_output = subprocess.check_output(['which', 'date'])
    date_path = which_output.decode('utf-8').strip()
    return date_path

def date_mod_path():
    file_abs_path = os.path.abspath(__file__)
    file_dir_path = os.path.dirname(file_abs_path)
    date_mod_path = file_dir_path + "/date-modified"
    return date_mod_path

def make_date_copy():
    dp = date_path()
    dmp = date_mod_path()
    shutil.copy(dp, dmp)

def apply_format_string_patch(date_bytes):
    """ Changes the default format string from '%a %b %e %H:%M:%S %Z %Y'
        to '%H:%M:%S'.
    """
    idx = date_bytes.find(FORMAT_STRING_BYTES)
    if -1 == idx:
        print("[*] Default format string not found")
        exit(1)
    
    print("[*] Applying format string patch at offset " + str(hex(idx)))
    date_bytes = date_bytes.replace(FORMAT_STRING_BYTES,
                                    MODIFIED_FORMAT_STRING_BYTES, 1)
    
    return date_bytes

def apply_nl_langinfo_item_patch(date_bytes):
    """ Changes the 'mov edi, 0x2006c' instruction to 'mov edi, 0xffffffff'
        to effectively change the default format string. date only uses the
        default format string in case nl_langinfo returns an empty string.
        To trigger this fallback case we need to change nl_langinfo's item
        argument to -1 (0xffffffff).
    """
    idx = date_bytes.find(NL_LANGINFO_ITEM_BYTES)
    if -1 == idx:
        print("[*] nl_langinfo() item move instruction not found")
        exit(1)

    print("[*] Applying nl_langinfo item patch at offset " + str(hex(idx)))
    date_bytes = date_bytes.replace(NL_LANGINFO_ITEM_BYTES,
                                    MODIFIED_NL_LANGINFO_ITEM_BYTES, 1)
    
    return date_bytes

def apply_patches():
    make_date_copy()

    dmp = date_mod_path()
    date_file = open(dmp, 'r+b')

    date_bytes = date_file.read()
    date_file.seek(0)

    date_bytes = apply_format_string_patch(date_bytes)
    date_bytes = apply_nl_langinfo_item_patch(date_bytes)

    # Write modifications to disk.
    date_file.write(date_bytes)

    date_file.close()

apply_patches()

print("[*] Done applying patches")
