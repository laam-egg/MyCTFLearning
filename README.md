# Useful links

1. x86 Registers - Meaning and History - <https://keleshev.com/eax-x86-register-meaning-and-history/>
2. x86 64-bit C Calling Convention - <https://aaronbloomfield.github.io/pdr/book/x86-64bit-ccc-chapter.pdf>
3. Intro to x86 Assembly - <https://www.youtube.com/playlist?list=PLmxT2pVYo5LB5EzTPZGfFN0c2GDiSXgQe>
4. Nightmare - An Intro to Binary Exploitation - <https://guyinatuxedo.github.io/index.html>
5. Linux x86 32-bit System Call Table - <https://syscalls32.paolostivanin.com/> (Note that **return value is in EAX**)
6. Linux x86 64-bit System Call Table - <https://blog.rchapman.org/posts/Linux_System_Call_Table_for_x86_64/> (Note that **return value is in RAX**)
7. x64 Assembly Cheat Sheet - <https://cs.brown.edu/courses/cs033/docs/guides/x64_cheatsheet.pdf>

# Summary: NASM and ld
 - Compile x86 32-bit executable:
	nasm -f elf32 asm.asm -o build/asm.o
	ld -m elf_i386 build/asm.o -o build/asm

 - Compile x86 64-bit executable:
	nasm -f elf64 asm64.asm -o build/asm64.o
	ld -m elf_x86_64 build/asm64.o -o build/asm64

 - To run the executables:
	./build/asm
	./build/asm64

# Summary: Linux Kernel Calling Convention (x86 64-bit)
Residence of System call code:
	rax
Residence of Parameters:
				rdi		rsi		rdx		r10	r8	r9
Some system call codes:
	 0  sys_read		int fd		char*		size_t
	 1  sys_write		int fd		char const*	size_t
	60  sys_exit		int

# Summary: Linux Kernel Calling Convention (x86 32-bit)
Residence of System call code:
	eax
Residence of Parameters:
				ebx		ecx		edx		esi	edi
	 1  sys_exit		int
	 3  sys_read		int fd		char*		size_t
	 4  sys_write		int fd		char const*	size_t

# Summary: File Descriptor (fd) codes
	 0  stdin
	 1  stdout
	 2  stderr

# Summary: C Calling Convention (x86 64-bit)
## About volatile and non-volatile registers

Certain registers are designated to either store temporary or long-lived
values. Specifically, volatile registers (aka caller-saved registers) mean
to store temporary values that might not be preserved across calls. Thus:
1. If the caller needs the values in these registers, it must push the
values onto the stack (for later use) BEFORE calling a function (hence
the name "called-saved").
2. The callee may manipulate those registers freely.
3. When the callee returns, if step 1 is done before (thus the caller needs
the old values), pop the values off of the stack and save them back to their
original residential registers. 

Caller-saved registers in x86 64-bit are:
	r10	r11	Registers containing function parameters (below)

In contrast to volatile registers, non-volatile registers (aka callee-saved
registers) mean to store long-lived values that must be preserved across
calls, i.e. the top-level caller can use those registers freely without
worrying them being modified. In case of the callee, it must push the content
of those registers onto the stack, and pop them back to the corresponding
registers to store their original values to fit the caller's assumption that
those registers are not changed (hence the name "callee-saved"). To conclude:
1. The caller may manipulate those registers freely.
2. If the callee needs to use these registers, it must first push the content
of these registers onto the stack (for caller's use later) BEFORE manipulating
those registers.
3. Right before the callee returns, if step 2 is done previously (i.e. the
callee has manipulated the non-volatile registers), the callee  must pop the
values off of the stack and save them back to their original residential
registers.

Callee-saved registers in x86 64-bit are:
	rbx	rbp	r12-r15

## Residence of Parameters and Return Value:
 - Residence of Parameters:
	rdi	rsi	rdx	rcx	r8	r9	More parameters are pushed onto the stack in 
							REVERSE order (push last parameter first)

 - Residence of Return Value:
	rax

## Callee's Local Variables
 - If the callee needs to allocate local variables, it may use registers or
allocate the variables on the stack. It may push-per-variable or reserve the
stack before initializing the variables' values. For example, reserving a
local long (8 bytes in x64 mode) and a local float (4 bytes) means reserving
12 bytes in total, so we widen the stack by moving the Stack Pointer 12 bytes
off:
	sub rsp, 12
 - Remember to deallocate local variables on the stack, if any, before issuing
a RET instruction. The easiest way to do this is to set RSP to the original
value before allocating local variables.
