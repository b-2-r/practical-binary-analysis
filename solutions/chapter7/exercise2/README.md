# Limiting the Scope of ls

Use the LD_PRELOAD technique to modify a copy of /bin/ls such that it will
show directory listings only for paths within your home directory.

## Solution

libls-limiter

## Sample session:

```
$ gcc -o libls-limiter.so -fPIC -shared -D_GNU_SOURCE libls-limiter.c -ldl
$ LD_PRELOAD=`pwd`/libls-limiter.so ls ~/Desktop
[*] Intercepted __xstat()
$ LD_PRELOAD=`pwd`/libls-limiter.so ls ~/.bashrc
[*] Intercepted __xstat()
/home/admin/.bashrc
$ LD_PRELOAD=`pwd`/libls-limiter.so ls /usr/share
[*] Intercepted __xstat()
ls: cannot access '/usr/share': Permission denied
$ LD_PRELOAD=`pwd`/libls-limiter.so ls /etc/passwd
[*] Intercepted __xstat()
ls: cannot access '/etc/passwd': Permission denied
```
