; TO TEST IF THE PROGRAM RUNS CORRECTLY:
; Run it two times, the first time: enter a name and just press Enter.
; The second time, input a name but press CtrlD instead of Enter.
; Verify that the outputs of the program in both cases are the same
; and do not contain any redundant newline characters (except that in
; the latter case, there's no newline in place of CtrlD).
;
; Run it two more times, with the same procedure as above, except that
; the input is empty. Verify that the program still output Hello !,
; without segmentation fault or any other errors.


section .data
	welcome_msg		db	"Welcome.", 0xA
	welcome_msg_len		equ	$ - welcome_msg
	name_prompt		db	"Please enter your name: "
	name_prompt_len		equ	$ - name_prompt
	hello_begin		db	"Hello "
	hello_begin_len		equ	$ - hello_begin
	hello_end		db	"!", 0xA
	hello_end_len		equ	$ - hello_end
	name_max_len		equ	256

section .bss
	name			resb	name_max_len
	name_len		resq	1

section .text
	global _start

_start:
	mov rax, 1			; sys_write
	mov rdi, 1			; stdout
	mov rsi, welcome_msg		; char const*
	mov rdx, welcome_msg_len	; size_t
	syscall				; call kernel

	mov rax, 1			; sys_write
	mov rdi, 1			; stdout
	mov rsi, name_prompt		; char const*
	mov rdx, name_prompt_len	; size_t
	syscall				; call kernel

	push 0x99	; BEFORE CALLING readln	
	mov QWORD rdi, name		; char* buffer
	mov rsi, name_max_len		; size_t maxBytesToRead
	call readln
	mov QWORD [name_len], rax
	pop rax		; AFTER CALLING readln
	cmp rax, 0x99	; CHECK IF THE STACK IS NOT DAMAGED AFTER CALLING SUBROUTINE
	; IF DAMAGED, EXIT WITH ERROR
	mov rdi, -1
	jne general_error
	
	mov rax, 1			; sys_write
	mov rdi, 1			; stdout
	mov rsi, hello_begin		; char const*
	mov rdx, hello_begin_len	; size_t
	syscall				; call kernel

	mov rax, 1			; sys_write
	mov rdi, 1			; stdout
	mov rsi, name			; char const*
	mov rdx, [name_len]		; size_t
	syscall				; call kernel

	mov rax, 1			; sys_write
	mov rdi, 1			; stdout
	mov rsi, hello_end		; char const*
	mov rdx, hello_end_len		; size_t
	syscall				; call kernel

_end:
	mov rax, 60			; sys_exit
	mov rdi, 0			; int
	syscall				; call kernel

readln: ; (char* buffer, size_t maxBytesToRead) => size_t numBytesRead
	mov rax, 0		; sys_read
	mov rdx, rsi		; size_t maxBytesToRead
	mov rsi, rdi		; char* buffer
	mov rdi, 0		; stdin
	syscall			; call kernel

	; Return value of sys_read (i.e. number of bytes read) is in rax.
	cmp rax, 0
	je readln_return
	
	dec rax
	mov rdx, name
	add rdx, rax 		; go to the last char
	cmp byte [rdx], 0xA
	je readln_return	; if last char is newline, return with rax already decremented
	inc rax			; increment rax to restore it to original value so as not to strip any character

readln_return:
	; Didn't touch callee-saved registers.
	ret

general_error: ; (int errorCode) => void
	mov rax, 1		; sys_write
	mov rsi, rdi		; int errorCode
	mov r10, rdi		; save errorCode to r10 too
	add rsi, '0'		; convert it to char
	mov rdi, 1		; stdout
	mov rdx, 1		; size_t
	syscall			; call kernel
	
	mov rax, 60		; sys_exit
	mov rdi, r10		; int errorCode
	syscall			; call kernel

