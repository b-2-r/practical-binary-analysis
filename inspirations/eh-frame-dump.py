# ----------------------------------------------------------------------------
# eh-frame-dump.py
# Written by Manuel Gebele (m.gebele‹ατ›tuta.io)
#
# Dumps the content of the eh_frame section.
# ----------------------------------------------------------------------------
import sys

import elftools.elf.elffile as elffile
import elftools.dwarf.callframe as callframe

def get_dwarf_info(elf):
    if not elf.has_dwarf_info():
        print('[*] File has no DWARF info')
        return None
    # Beside a debug info section we also
    # need a eh_frame section.
    dwarfinfo = elf.get_dwarf_info()
    if not dwarfinfo.has_EH_CFI():
        print('[*] File has no eh_frame section')
        return None
    return dwarfinfo

def dump_fde(fde):
    startAddress = fde['initial_location']
    endAddress = fde['initial_location'] + fde['address_range']

    print('[*] Found function boundary 0x%x..0x%x'
        % (startAddress, endAddress))

def print_dwarfinfo(dwarfinfo):
    for entry in dwarfinfo.EH_CFI_entries():
        if isinstance(entry, callframe.FDE):
            dump_fde(entry)

try:
    filename = sys.argv[1]
except IndexError:
    print('usage: ' + sys.argv[0] + ' <ELF-binary>')
    sys.exit(1)
 
with open(filename, 'rb') as f:
    elf = elffile.ELFFile(f)
    
    dwarfinfo = get_dwarf_info(elf)
    if dwarfinfo:
        print_dwarfinfo(dwarfinfo)
        
