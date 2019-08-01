# Confusing objdump

Write a program that confuses objdump such that it interprets data as code,
or vice versa. You’ll probably need to use some inline assembly to
achieve this (for instance, using gcc’s asm keyword).

## Solution

fool-linear-disas.c

## Sample Session

```
$ gcc -masm=intel -o fool-linear-disas fool-linear-disas.c
$ objdump -d -M intel --section .text fool-linear-disas
[...]
0000000000400528 <main>:
400528:	55                   	push   rbp
400529:	48 89 e5             	mov    rbp,rsp
40052c:	b8 00 00 00 00       	mov    eax,0x0
400531:	e8 aa 00 00 00       	call   4005e0 <hidden_function>
400536:	b8 00 00 00 00       	mov    eax,0x0
40053b:	5d                   	pop    rbp
40053c:	c3                   	ret    
40053d:	0f 1f 00             	nop    DWORD PTR [rax]
[...]
$ strip fool-linear-disas
$ objdump -d -M intel --section .text fool-linear-disas
[...]
400526:	48 ba 55 48 89 e5 b8 	movabs rdx,0xb8e5894855
40052d:	00 00 00 
400530:	00 e8                	add    al,ch
400532:	aa                   	stos   BYTE PTR es:[rdi],al
400533:	00 00                	add    BYTE PTR [rax],al
400535:	00 b8 00 00 00 00    	add    BYTE PTR [rax+0x0],bh
40053b:	5d                   	pop    rbp
40053c:	c3                   	ret    
40053d:	0f 1f 00             	nop    DWORD PTR [rax]
[...]
```
