/* ---------------------------------------------------------------------------
 * fool-linear-disas.c
 * 
 * Written by Manuel Gebele (m.gebele‹ατ›tuta.io)
 * This code is licensed under the MIT License (MIT).
 * ---------------------------------------------------------------------------
 */
#include <stdio.h>

void hidden_function();

/*
 * This will eat most of the main functions instructions.
 * (also the call instruction to 'hidden_function')
 */
asm(
  ".text\n\t"
  ".byte 0x48, 0xba"
);

int
main()
{
  hidden_function();

  return 0;
}

asm(
  ".section .rodata\n"
  "string:\n\t"
  ".string \"[*] hidden_function called!\"\n"
  /*
   * Put this function into the .rodata section so that it will
   * not be shown in objdump's default disassembly output.
   */
  "hidden_function:\n\t"
  "push rbp\n\t"
  "mov rbp, rsp\n\t"
  "mov rdi, offset string\n\t"
  "pop rbp\n\t"
  "jmp puts"
);
