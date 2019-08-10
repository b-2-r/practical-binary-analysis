# Inspirations

Contains randomly inspired code samples.

## eh-frame-dump.py [Page 131]

Dumps the content of the **eh_frame** section.

### Sample Session

```
$ ./eh-frame-dump.py `which su`
[*] Found function boundary 0x3ad0..0x3afa
[*] Found function boundary 0x2690..0x26a0
[*] Found function boundary 0x3c00..0x3c07
[*] Found function boundary 0x3c10..0x3c4e
[*] Found function boundary 0x29d0..0x2aac
[*] Found function boundary 0x3c50..0x3cab
[*] Found function boundary 0x3cb0..0x42e0
[*] Found function boundary 0x42e0..0x4907
[*] Found function boundary 0x2b00..0x3ac8
[*] Found function boundary 0x4910..0x492e
[...]
```

## libhijk-ps [Page 163]

A basic example which uses **LD_PRELOAD** to hijack readproc and readproctab2 to coax ps to not show a particular process in its process listing.

### Sample session

```
$ gcc -o libhijk-ps.so -fPIC -shared -D_GNU_SOURCE libhijk-ps.c
$ ./victim # the process which should be hidden
$ ps a
  PID TTY      STAT   TIME COMMAND
  864 tty7     Ssl+  36:02 /usr/lib/xorg/Xorg -core :0 [...] 
 1446 tty1     Ss+    0:00 /sbin/agetty --noclear tty1 linux
10053 pts/9    Ss     0:02 -zsh
10202 pts/9    S      0:00 ./victim
10209 pts/9    R+     0:00 ps a
$ LD_PRELOAD=`pwd`/libhijk-ps.so ps a
  PID TTY      STAT   TIME COMMAND
  864 tty7     Ssl+  36:05 /usr/lib/xorg/Xorg -core :0 [...]
 1446 tty1     Ss+    0:00 /sbin/agetty --noclear tty1 linux
10053 pts/9    Ss     0:02 -zsh
10214 pts/9    R+     0:00 ps a
$ ps f # invokes readproctab2
  PID TTY      STAT   TIME COMMAND
10053 pts/9    Ss     0:02 -zsh
10222 pts/9    R+     0:00  \_ ps f
10202 pts/9    S      0:00 ./victim
$ LD_PRELOAD=`pwd`/libhijk-ps.so ps f
  PID TTY      STAT   TIME COMMAND
10053 pts/9    Ss     0:02 -zsh
10225 pts/9    R+     0:00  \_ ps f
```

## patchman [Page 155]

A bare-metal binary modification tool

### Sample session

```
```
