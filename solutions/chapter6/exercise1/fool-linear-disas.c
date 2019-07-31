/* ---------------------------------------------------------------------------
 * fool-linear-disas.c
 * 
 * Written by Manuel Gebele (m.gebele‹ατ›tuta.io)
 * This code is licensed under the MIT License (MIT). 
 * 
 * Chapter 6, Exercise 1
 *
 * Sample session:
 * $ gcc -masm=intel -o fool-linear-disas fool-linear-disas.c
 * $ objdump -d -M intel --section .text fool-linear-disas
 * ...
 * 0000000000400528 <main>:
 * 400528:	55                   	push   rbp
 * 400529:	48 89 e5             	mov    rbp,rsp
 * 40052c:	b8 00 00 00 00       	mov    eax,0x0
 * 400531:	e8 aa 00 00 00       	call   4005e0 <hidden_function>
 * 400536:	b8 00 00 00 00       	mov    eax,0x0
 * 40053b:	5d                   	pop    rbp
 * 40053c:	c3                   	ret    
 * 40053d:	0f 1f 00             	nop    DWORD PTR [rax]
 * ...
 * $ strip fool-linear-disas
 * $ objdump -d -M intel --section .text fool-linear-disas
 * * ...
 * 400526:	48 ba 55 48 89 e5 b8 	movabs rdx,0xb8e5894855
 * 40052d:	00 00 00 
 * 400530:	00 e8                	add    al,ch
 * 400532:	aa                   	stos   BYTE PTR es:[rdi],al
 * 400533:	00 00                	add    BYTE PTR [rax],al
 * 400535:	00 b8 00 00 00 00    	add    BYTE PTR [rax+0x0],bh
 * 40053b:	5d                   	pop    rbp
 * 40053c:	c3                   	ret    
 * 40053d:	0f 1f 00             	nop    DWORD PTR [rax]
 * ...
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
