# Confusing a Recursive Disassembler

Write another program, this time so that it tricks your favorite recursive
disassembler’s function detection algorithm. There are various ways to do
this. For instance, you could create a tail-called function or a function
that has a switch with multiple return cases. See how far you can go with
confusing the disassembler!

## Solution

fool-recursive-disas.c

## Sample Session

All samples were tested against radare2 (r2).

```
$ gcc -masm=intel -o fool-recursive-disas fool-recursive-disas.c
$ r2 fool-recursive-disas 

Display global callgraph:
[0x00400480]> agC  

Display function callgraph:
[0x00400480]> agc @ [addr] 

Disassemble function (recursive):
[0x00400480]> pdf @ [addr] 

Print disassembly (recursive):
[0x00400480]> pdr @ [addr]
```
