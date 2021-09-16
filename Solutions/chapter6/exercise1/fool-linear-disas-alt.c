#include <stdio.h>
int main(){
int x = 0;
if(x == 1)
	/*
	   Disassembly of the string "Hello"
	*/
 {
	__asm__ __volatile__(
	"rex.W\n\t"
	"gs insb (%dx),%es:(%rdi)\n\t"
	"insb   (%dx),%es:(%rdi)\n\t"
	"outsl  %ds:(%rsi),(%dx)\n\t"
	"add    %al,(%rax)\n\t"
	);
 }
char *buf = (char*)0x00400542;
   printf("%s\n", buf);
   return 0;
}

