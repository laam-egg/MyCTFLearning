section .data
	greeting                 db     "Welcome !", 0xA
	greeting_len             equ    $ - greeting
	prompt                   db     "Please enter your name: "
	prompt_len               equ    $ - prompt
	echo_name_1              db     "Hello "
	echo_name_1_len          equ    $ - echo_name_1
	echo_name_2              db     "!", 0xA
	echo_name_2_len          equ    $ - echo_name_2
	general_errmsg           db     "An error occurred.", 0xA
	general_errmsg_len       equ    $ - general_errmsg

section .bss
	name                    resb   256
	name_len                resd   1

section .text
	global _start;

_start:
	mov eax, 4                   ; sys_write
	mov ebx, 1                   ; stdout
	mov ecx, greeting            ; char const*
	mov edx, greeting_len        ; size_t
	int 0x80                     ; call kernel

	mov eax, 4                   ; sys_write
	mov ebx, 1                   ; stdout
	mov ecx, prompt              ; char const*
	mov edx, prompt_len          ; size_t
	int 0x80

	push 0x99 ; for checking the stack after calling get_string
	; calling get_string
	push ebp
	mov ebp, esp
	push _start_done_get_name
	push name
	jmp get_string
_start_done_get_name:
	mov [name_len], eax          ; return value of get_string

	; Check if the stack has not been damaged
	pop edx
	cmp edx, 0x99
	jne general_error
	
	mov eax, 4                   ; sys_write
	mov ebx, 1                   ; stdout
	mov ecx, echo_name_1         ; char const*
	mov edx, echo_name_1_len     ; size_t
	int 0x80                     ; call kernel

	mov eax, 4                   ; sys_write
	mov ebx, 1                   ; stdout
	mov ecx, name                ; char*
	mov edx, [name_len]          ; size_t
	int 0x80                     ; call kernel

	mov eax, 4                   ; sys_write
	mov ebx, 1                   ; stdout
	mov ecx, echo_name_2         ; char const*
	mov edx, echo_name_2_len     ; size_t
	int 0x80                     ; call kernel    

_end:
	mov eax, 1                   ; sys_exit
	mov ebx, 0                   ; exit code
	int 0x80                     ; call kernel

general_error:
	mov eax, 4                   ; sys_write
	mov ebx, 1                   ; stdout
	mov ecx, general_errmsg      ; char const*
	mov edx, general_errmsg_len  ; size_t
	int 0x80                     ; call kernel
	jmp _end

; How to use get_string
;	push ebp
;	mov ebp, esp
; 	push after_get_string
;	push buffer
;	jmp get_string
; after_get_string:
; 	; ecx holds the char* buffer, eax holds the size

get_string: ; ebp => eip => char* buffer
	mov eax, 3                   ; sys_read
	mov ebx, 0                   ; stdin
	pop ecx                      ; char* buffer
	mov edx, 256                 ; size_t
	int 0x80                     ; call kernel
	
	; Number of bytes read is in eax. Just leave it intact.

	cmp eax, 0
	je get_string_dont_delete_last_newline

	mov edx, name
	add edx, eax
	sub edx, 1
	cmp byte [edx], 0xA
	jne get_string_dont_delete_last_newline
	sub eax, 1

get_string_dont_delete_last_newline:
	pop edx
	pop ebp
	jmp edx
