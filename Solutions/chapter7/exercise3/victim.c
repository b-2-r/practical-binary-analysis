/* ---------------------------------------------------------------------------
 * victim.c
 * 
 * Written by Manuel Gebele (m.gebele‹ατ›tuta.io)
 * 
 * Chapter 7, Exercise 3
 * 
 * Preconditions/Dependencies:
 * Refer to elf-parasite.s
 * 
 * Sample session:
 * $ gcc -o victim victim.c
 * ---------------------------------------------------------------------------
 */
#include <stdio.h>
#include <stdlib.h>

int
main(int argc, char *argv[])
{
    printf("I'm a victim!\n");

    exit(EXIT_SUCCESS);
}
