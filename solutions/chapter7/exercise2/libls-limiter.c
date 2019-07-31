/* ---------------------------------------------------------------------------
 * libls-limiter.c
 * 
 * Written by Manuel Gebele (m.gebele‹ατ›tuta.io)
 * 
 * Chapter 7, Exercise 2
 * 
 * Sample session:
 * gcc -o libls-limiter.so -fPIC -shared -D_GNU_SOURCE libls-limiter.c -ldl
 * LD_PRELOAD=`pwd`/libls-limiter.so ls ~/Desktop
 * LD_PRELOAD=`pwd`/libls-limiter.so ls ~/.bashrc
 * LD_PRELOAD=`pwd`/libls-limiter.so ls /usr/share
 * LD_PRELOAD=`pwd`/libls-limiter.so ls /etc/passwd
 * ---------------------------------------------------------------------------
 */
#include <stdio.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <errno.h>
#include <string.h>
#include <dlfcn.h>

// I have choosen to hijack an early entry point to implement
// "access control". This allows us to control both cases,
// directory and file accesses. Functions like opendir() and
// readdir() only allow to control directory accesses.
int (* orig_xstat)(int, const char *, struct stat *);

int
refers_to_home_dir(char *path)
{
    // NOTE: In a real world scenario we should also consider
    // getpwuid/getpwuid_r to get the users home directory.
    char *hpath = getenv("HOME");
    if (NULL == hpath) {
        // Be liberal...
        return 1;
    }

    if (strncmp(path, hpath, strlen(hpath)) == 0) {
        return 1;
    }

    return 0;
}

int
__xstat(int ver, const char * path, struct stat * stat_buf)
{
    printf("[*] Intercepted __xstat()\n");

    if (NULL == orig_xstat) {
        orig_xstat = dlsym(RTLD_NEXT, "__xstat");
    }

    char *rpath = realpath(path, NULL);
    if (!refers_to_home_dir(rpath)) {
        errno = EACCES; // Set errno manually.
        free(rpath);
        return -1;
    }
    
    free(rpath);
    
    return orig_xstat(ver, path, stat_buf);
}
