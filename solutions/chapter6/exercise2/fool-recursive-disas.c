/*
 * fool-recursive-disas.c
 * 
 * Written by Manuel Gebele (m.gebele‹ατ›tuta.io)
 * This code is licensed under the MIT License (MIT). 
 * 
 * Chapter 6, Exercise 2
 * 
 * All samples were tested against radare2 (r2).
 * 
 * Sample session:
 * $ gcc -masm=intel -o fool-recursive-disas fool-recursive-disas.c
 * $ r2 fool-recursive-disas
 * 
 * Display global callgraph:
 * [0x00400480]> agC
 *  
 * Display function callgraph:
 * [0x00400480]> agc @ [addr]
 * 
 * Disassemble function (recursive):
 * [0x00400480]> pdf @ [addr]
 * 
 * Print disassembly (recursive):
 * [0x00400480]> pdr @ [addr]
 */
#include <stdio.h>

char tail_call_string[24] = "[*] Tail call confusing";

asm(
    ".data\n"
    "indirect_call_string:\n\t"
    ".string \"[*] Indirect call confusing\"\n"
    "indirect_jump_string:\n\t"
    ".string \"[*] Indirect jump confusing\"\n"
    "exit_string:\n\t"
    ".string \"[*] exit() confusing (noreturn)\"\n"
    "abort_string:\n\t"
    ".string \"[*] abort() confusing (noreturn)\""
);

#pragma GCC push_options
#pragma GCC optimize("02")

/*
 * The optimization produces a jump instruction rather than
 * a call instruction (due to tail-call optimization).
 * This has the effect that the jump to 'puts()' does not
 * appear in any callgraph.
 */
void
fool_via_auto_tail_call()
{
    puts(tail_call_string);
}

#pragma GCC pop_options

/*
 * The same as above (this time using a 'manual' tail-call).
 */
asm(
    "fool_via_manual_tail_call:\n\t"
    "push rbp\n\t"
    "mov rbp, rsp\n\t"
    "mov rdi, offset tail_call_string\n\t"
    "pop rbp\n\t"
    "jmp puts"
);

/*
 * The indirect call to the address-taken function (puts()),
 * does not appear in any callgraph.
 */
void
fool_via_indirect_call()
{
    asm(
        "mov rdi, offset indirect_call_string\n\t"
        "mov rbx, offset puts\n\t"
        "call rbx"
    );
}

/*
 * Causes r2 to incompletely disassemble the function. 
 * 
 * Also note that neither the indirect jump, nor the call
 * to 'puts()' appears in any callgraph.
 */
void
fool_via_indirect_jump()
{
    asm(
        "mov rdi, offset hidden\n\t"
        "jmp rdi\n"
        "hidden:\n\t"
        "mov rdi, offset indirect_jump_string\n\t"
        "call puts"
    );
}

/*
 * exit() and abort() are well-known library functions that will
 * never return. We define our own version of each function with
 * exact the same signature but in contrast to the original
 * versions, both of our functions will return. While disassembling,
 * r2 wrongly assumes that each call refers to the corresponding
 * library version instead of our custom one. Because it is not
 * safe to assume that there are instructions following a
 * nonreturning call, r2 stops disassembling after reaching
 * 'call exit'/'call abort'. Like the indirect jump shown above,
 * this causes r2 to incompletely disassemble 'fool_via_exit()'
 * and 'fool_via_abort()'. In addition the call to 'puts()' is also
 * missed in both callgraphs (global and local).
 */
void exit(int status)   { /* nop */ }
void abort(void)        { /* nop */ }

void
fool_via_exit()
{
    asm(
        "mov edi, 1\n\t"
        "call exit\n\t"
        "mov rdi, offset exit_string\n\t"
        "call puts"
    );
}

void
fool_via_abort()
{
    asm(
        "mov edi, 1\n\t"
        "call abort\n\t"
        "mov rdi, offset abort_string\n\t"
        "call puts"
    );
}

void
fool_via_noreturn()
{
    fool_via_exit();
    fool_via_abort();
}

int
main(int argc, char *argv[])
{
    fool_via_auto_tail_call();
    
    asm(
        /* "mov eax, 0\n\t" */
        "call fool_via_manual_tail_call"
    );

    fool_via_indirect_call();
    fool_via_indirect_jump();
    fool_via_noreturn();

    return 0;
}
