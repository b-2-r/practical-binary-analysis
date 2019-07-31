#!/usr/bin/env python3
# ----------------------------------------------------------------------------
# anti-fool-r2.py
#
# Written by Manuel Gebele (m.gebele‹ατ›tuta.io)
# This code is licensed under the MIT License (MIT). 
#
# Chapter 6, Exercise 3
#
# Requirements:
# $ pip3 install r2pipe
#
# Sample session:
# $ chmod +x anti-fool-disas.py
# $ ./anti-fool-disas.py
# $ ./anti-fool-disas.py -t <binary>
# ----------------------------------------------------------------------------
import sys
import collections
import argparse
import r2pipe

r2p = None
functions = []
disasm_cache = {}

""" A scaled-down version of r2pipe's JSON encoded function info.
"""
Function = collections.namedtuple('Function', ('name', 'address'))

""" A scaled-down version of r2pipe's JSON encoded section info.
"""
Section = collections.namedtuple('Section', 'name')

""" A scaled-down version of r2pipe's JSON encoded reference info.
"""
Reference = collections.namedtuple('Reference', ('type', 'name', 'address'))

""" A scaled-down version of r2pipe's JSON encoded instruction info.
"""
Instruction = collections.namedtuple('Instruction', ('address', 'disasm'))

def get_functions():
    """ Returns a list of available functions.
    """
    return r2p.cmdj('aflj')

def get_function_disasm(function):
    """ Returns a dict of the function's (recursive) disassembly.
    """
    if function.address not in disasm_cache:
        cmdj = 'pdfj @ ' + function.address
        disasm_cache[function.address] = r2p.cmdj(cmdj)
    return disasm_cache[function.address]

def get_section(offset):
    """ Returns the section to which the offset belongs to.
    """
    cmdj = 'iSj. @ ' + str(offset)
    section = r2p.cmdj(cmdj)
    return Section(section['name'])

def get_noreturns():
    """ Returns a list of well-known noreturns.
    """
    return r2p.cmd('tn')

def get_function_references(function):
    """ Returns a list of available data/code references.
    """
    cmdj = 'axffj @ ' + function.name
    return r2p.cmdj(cmdj)

def excluded_section_names():
    """ Returns a list of excluded section names.
    """
    return ['.plt', '.plt.got']

def interested_in_section(section):
    """ Returns whether this section is of interest.
    """
    return section.name not in excluded_section_names() 

def build_function_info():
    """ Build a scaled-down version of r2pipe's function list.
    """
    for f in get_functions():
        section = get_section(f['offset'])
        if not interested_in_section(section):
            continue
        functions.append(Function(f['name'],
            hex(f['offset'])))

def is_valid_noreturn(noreturn):
    """ Determines whether noreturn is a valid noreturn target.
    """
    noreturns = get_noreturns().split()
    noreturns = ['sym.imp.' + nr for nr in noreturns]
    return noreturn in noreturns

def search_tail_call(function):
    """ Searches for tail calls.
    """
    disasm = get_function_disasm(function)
    op = disasm['ops'][-1]
    if op['type'] != 'jmp':
        return None
    return Instruction(hex(op['offset']), op['disasm'])

def search_instructions(insn_type, function):
    """ Searches for the given instruction type (e.g. call, ujmp, ...).
    """
    disasm = get_function_disasm(function)
    for op in disasm['ops']:
        if op['type'] != insn_type:
            continue
        yield Instruction(hex(op['offset']), op['disasm'])

def search_references(ref_type, function):
    """ Searches for the given reference type (DATA, CODE, or CALL).
    """
    references = get_function_references(function)
    for r in references:
        if r['type'] != ref_type:
            continue
        yield Reference(r['type'], r['name'], hex(r['at']))

def search_address_taken_functions(function):
    """ Searches for functions that have their address taken from
        memory/register.  
    """
    function_names = [f['name'] for f in get_functions()]
    references = search_references('DATA', function)
    for r in references:
        if r.name not in function_names:
            continue
        yield r
        
def search_noreturn_fake(function):
    """ Searches for functions that are potential noreturn fakes.
    """
    disasm = get_function_disasm(function)
    op = disasm['ops'][-1]
    if (op['type'] != 'call'):
        return None
    noreturn = op['disasm'].split()[-1]
    if is_valid_noreturn(noreturn):
        return None
    return Instruction(hex(op['offset']), op['disasm'])

def print_tail_calls():
    """ Prints all tail calls in the binary.
    """
    for f in functions:
        tail_call = search_tail_call(f)
        if tail_call:
            print('Found tail-call in %s at %s (%s)'
                % (f.name,
                   tail_call.address,
                   tail_call.disasm))
        
def print_indirect_calls():
    """ Prints all indirect calls in the binary.
    """
    for f in functions:
        indirect_calls = search_instructions('ucall', f)
        for indirect_call in indirect_calls:
            print('Found indirect call in %s at %s (%s)'
                % (f.name,
                indirect_call.address,
                indirect_call.disasm))

def print_indirect_jumps():
    """ Prints all indirect jumps in the binary.
    """
    for f in functions:
        indirect_jumps = search_instructions('ujmp', f)
        for indirect_jump in indirect_jumps:
            print('Found indirect jump in %s at %s (%s)'
                % (f.name,
                indirect_jump.address,
                indirect_jump.disasm))

def print_address_taken_functions():
    """ Prints all address-taken functions in the binary.
    """
    for f in functions:
        references = search_address_taken_functions(f)
        for reference in references:
            print('Found address-taken function in %s at %s (%s)'
                % (f.name,
                reference.address,
                reference.name))

def print_noreturn_fakes():
    """ Prints all potential noreturn fakes in the binary.
    """
    for f in functions:
        noreturn_fake = search_noreturn_fake(f)
        if noreturn_fake:
            print('Found potential noreturn fake in %s at %s (%s)'
                % (f.name,
                noreturn_fake.address,
                noreturn_fake.disasm))

# __main__

SCRIPT_DESCRIPTION = 'An attempt to improve radare2\'s function detection'
SCRIPT_VERSION = "0.1"

argparser = argparse.ArgumentParser(
    usage='usage: %(prog)s [options] <binary>',
    description=SCRIPT_DESCRIPTION, prog=sys.argv[0])
argparser.add_argument('binary',
    nargs='?', default=None, help='ELF binary to analyse')
argparser.add_argument('-t', '--tail-calls',
    action='store_true', dest='search_tail_calls',
    help='Search for tail-calls')
argparser.add_argument('-c', '--indirect-calls',
    action='store_true', dest='search_indirect_calls',
    help='Search for indirect calls')
argparser.add_argument('-j', '--indirect-jumps',
    action='store_true', dest='search_indirect_jumps',
    help='Search for indirect jumps')
argparser.add_argument('-f', '--address-taken',
    action='store_true', dest='search_address_taken_functions',
    help='Search for address taken functions')
argparser.add_argument('-n', '--noreturn-fakes',
    action='store_true', dest='search_noreturn_fakes',
    help='Search for potential noreturn fakes')
argparser.add_argument('-a', '--all',
    action='store_true', dest='search_all',
    help='Equivalent to: -t -c -j -f -n')
argparser.add_argument('-v', '--version',
    action='version', version=SCRIPT_VERSION)

args = argparser.parse_args()
if not args.binary:
    argparser.print_help()
    sys.exit(0)

r2p = r2pipe.open(args.binary, flags=['-2'])
r2p.cmd('aaa')

build_function_info()

search_all = False
if args.search_all or len(sys.argv) == 2:
    search_all = True

if args.search_tail_calls or search_all:
    print_tail_calls()
if args.search_indirect_calls or search_all:
    print_indirect_calls()
if args.search_indirect_jumps or search_all:
    print_indirect_jumps()
if args.search_address_taken_functions or search_all:
    print_address_taken_functions()
if args.search_noreturn_fakes or search_all:
    print_noreturn_fakes()

r2p.quit()
