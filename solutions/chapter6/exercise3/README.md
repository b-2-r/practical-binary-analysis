# Improving Function Detection

Write a plugin for your recursive disassembler of choice so that it can
better detect functions such as those the disassembler missed in the
previous exercise. You’ll need a recursive disassembler that you can
write plugins for, such as IDA Pro, Hopper, or Medusa.

## Solution

anti-fool-radare2.py

## Requirements:

```
$ pip3 install r2pipe
```
## Sample session

```
$ chmod +x anti-fool-disas.py
$ ./anti-fool-radare2.py
usage: usage: ./anti-fool-r2.py [options] <binary>

An attempt to improve radare2's function detection

positional arguments:
  binary                ELF binary to analyse

optional arguments:
  -h, --help            show this help message and exit
  -t, --tail-calls      Search for tail-calls
  -c, --indirect-calls  Search for indirect calls
  -j, --indirect-jumps  Search for indirect jumps
  -f, --address-taken   Search for address taken functions
  -n, --noreturn-fakes  Search for potential noreturn fakes
  -a, --all             Equivalent to: -t -c -j -f -n
  -v, --version         show program's version number and exit
$ ./anti-fool-radare2.py --all fool-recursive-disas
Found tail-call in entry.init0 at 0x400571 (jmp sym.register_tm_clones)
Found tail-call in sym.fool_via_auto_tail_call at 0x400580 (jmp sym.imp.puts)
Found tail-call in loc.fool_via_manual_tail_call at 0x400591 (jmp sym.imp.puts)
Found indirect call in entry.init0 at 0x40056e (call rax)
Found indirect call in sym.__libc_csu_init at 0x4006c9 (call qword [r12 + rbx*8])
Found indirect call in sym.fool_via_indirect_call at 0x4005a8 (call rbx)
Found indirect jump in sym.deregister_tm_clones at 0x4004d5 (jmp rax)
Found indirect jump in sym.register_tm_clones at 0x400523 (jmp rax)
Found indirect jump in sym.fool_via_indirect_jump at 0x4005b8 (jmp rdi)
Found address-taken function in entry0 at 0x40048f (sym.__libc_csu_fini)
Found address-taken function in entry0 at 0x400496 (sym.__libc_csu_init)
Found address-taken function in entry0 at 0x40049d (main)
Found address-taken function in sym.fool_via_indirect_call at 0x4005a1 (sym.imp.puts)
Found potential noreturn fake in sym.fool_via_exit at 0x4005e3 (call sym.exit)
Found potential noreturn fake in sym.fool_via_abort at 0x400600 (call sym.abort)
```
