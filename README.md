# MyCTFLearning

- [MyCTFLearning](#myctflearning)
  - [Useful Links](#useful-links)
  - [NASM and ld](#nasm-and-ld)
  - [Linux Kernel Calling Convention (x86 64-bit)](#linux-kernel-calling-convention-x86-64-bit)
  - [Linux Kernel Calling Convention (x86 32-bit)](#linux-kernel-calling-convention-x86-32-bit)
  - [File Descriptor (fd) codes](#file-descriptor-fd-codes)
  - [C Calling Convention (x86 64-bit)](#c-calling-convention-x86-64-bit)
    - [(64) About volatile and non-volatile registers](#64-about-volatile-and-non-volatile-registers)
    - [(64) Residence of Arguments and Return Value](#64-residence-of-arguments-and-return-value)
    - [(64) Callee's Local Variables](#64-callees-local-variables)
  - [C Calling Convention (x86 32-bit)](#c-calling-convention-x86-32-bit)
    - [(32) Volatile and non-volatile registers](#32-volatile-and-non-volatile-registers)
    - [(32) Residence of Arguments and Return Value](#32-residence-of-arguments-and-return-value)
    - [(32) Callee's Local Variables](#32-callees-local-variables)

## Useful Links

1. x86 Registers - Meaning and History - <https://keleshev.com/eax-x86-register-meaning-and-history/>
2. x86 32-bit C Calling Convention - <https://aaronbloomfield.github.io/pdr/book/x86-32bit-ccc-chapter.pdf>
3. x86 64-bit C Calling Convention - <https://aaronbloomfield.github.io/pdr/book/x86-64bit-ccc-chapter.pdf>
4. Intro to x86 Assembly - <https://www.youtube.com/playlist?list=PLmxT2pVYo5LB5EzTPZGfFN0c2GDiSXgQe>
5. Nightmare - An Intro to Binary Exploitation - <https://guyinatuxedo.github.io/index.html>
6. Linux x86 32-bit System Call Table - <https://syscalls32.paolostivanin.com/> (Note that **return value is in EAX**)
7. Linux x86 64-bit System Call Table - <https://blog.rchapman.org/posts/Linux_System_Call_Table_for_x86_64/> (Note that **return value is in RAX**)
8. x64 Assembly Cheat Sheet - <https://cs.brown.edu/courses/cs033/docs/guides/x64_cheatsheet.pdf>

## NASM and ld

- Compile x86 32-bit executable:

    ```sh
    nasm -f elf32 asm.asm -o build/asm.o
    ld -m elf_i386 build/asm.o -o build/asm
    ```

- Compile x86 64-bit executable:

    ```sh
    nasm -f elf64 asm64.asm -o build/asm64.o
    ld -m elf_x86_64 build/asm64.o -o build/asm64
    ```

- To run the executables:

    ```sh
    ./build/asm
    ./build/asm64
    ```

## Linux Kernel Calling Convention (x86 64-bit)

Residence of values:

| System Call Code ; Return value |          Arguments           |
| :-----------------------------: | :--------------------------: |
|              `rax`              | `rdi, rsi, rdx, r10, r8, r9` |

Some system call codes:

| `rax` | System call  |         `rdi`          |           `rsi`           |           `rdx`           | `r10` | `r8`  | `r9`  |
| ----: | :----------- | :--------------------: | :-----------------------: | :-----------------------: | :---: | :---: | :---: |
|   `0` | `sys_read`   |        `int fd`        |          `char*`          |         `size_t`          |   -   |   -   |   -   |
|   `1` | `sys_write`  |        `int fd`        |       `char const*`       |         `size_t`          |   -   |   -   |   -   |
|  `59` | `sys_execve` | `char const* filename` | `char const* const* argv` | `char const* const* envp` |   -   |   -   |   -   |
|  `60` | `sys_exit`   |         `int`          |             -             |             -             |   -   |   -   |   -   |

## Linux Kernel Calling Convention (x86 32-bit)

Residence of values:

| System Call Code ; Return value |         Arguments         |
| :-----------------------------: | :-----------------------: |
|              `eax`              | `ebx, ecx, edx, esi, edi` |

Some system call codes:

| `eax` | System call  |         `ebx`          |           `ecx`           |           `edx`           | `esi` | `edi` |
| ----: | :----------- | :--------------------: | :-----------------------: | :-----------------------: | :---: | :---: |
|   `1` | `sys_exit`   |         `int`          |             -             |             -             |   -   |   -   |
|   `3` | `sys_read`   |        `int fd`        |          `char*`          |         `size_t`          |   -   |   -   |
|   `4` | `sys_write`  |        `int fd`        |       `char const*`       |         `size_t`          |   -   |   -   |
|  `11` | `sys_execve` | `char const* filename` | `char const* const* argv` | `char const* const* envp` |   -   |   -   |

## File Descriptor (fd) codes

```plain
    0  stdin
    1  stdout
    2  stderr
```

## C Calling Convention (x86 64-bit)

### (64) About volatile and non-volatile registers

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

```plain
    r10 ; r11 ; registers containing function arguments (below)
```

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

```plain
    rbx ; rbp ; r12-r15
```

### (64) Residence of Arguments and Return Value

|              Arguments              | Return value |
| :---------------------------------: | :----------: |
| `rdi, rsi, rdx, rcx, r8, r9`, stack |    `rax`     |

More arguments are pushed onto the stack in REVERSE order (push last argument
first). When the call finishes, the caller must deallocate arguments on the
stack, if any. For example, if the stack contains 2 `int` arguments, which
occupy 8 bytes in total, the code should be:

```asm
; ...
call some_function
add esp, 8
```

### (64) Callee's Local Variables

- If the callee needs to allocate local variables, it may use registers or
    allocate the variables on the stack. It may push-per-variable or reserve the
    stack before initializing the variables' values. For example, reserving a
    local long (8 bytes in x64 mode) and a local float (4 bytes) means reserving
    12 bytes in total, so we widen the stack by moving the Stack Pointer 12 bytes
    downwards:

    ```asm
    sub rsp, 12
    ```

- Remember to deallocate local variables on the stack, if any, before issuing
    a `ret` instruction. The easiest way to do this is to set RSP to the original
    value before allocating local variables. For instance, in correspondence with
    the previous example:

    ```asm
    add rsp, 12
    ```

- Another way to allocate/deallocate variables is mentioned in the
    [C Calling Convention on 32-bit x86](#c-calling-convention-x86-32-bit)
    section below.

## C Calling Convention (x86 32-bit)

### (32) Volatile and non-volatile registers

Caller-saved (volatile) registers are:

```plain
    eax     ecx     edx 
```

Callee-saved (non-volatile) registers are:

```plain
    ebx     edi     esi     ebp     esp 
```

In case of `ebp` - the Base Stack Pointer register and `esp` - the (Top) Stack
Pointer Register, the callee must save them at the very start of the function
body to preserve its caller's original stack frame:

```asm
push ebp
mov ebp, esp
```

Only after that will the callee be eligible to allocate its local variables
on the stack (see below).

### (32) Residence of Arguments and Return Value

- Arguments are pushed onto the stack in REVERSE order (push last argument
    first). The caller must deallocate arguments on the stack, if any (as told
    in [64-bit](#64-residence-of-arguments-and-return-value)).

- Set return value in `eax`.

### (32) Callee's Local Variables

Apart from the way to allocate/deallocate local variables as mentioned in the
[C Calling Convention on 64-bit x86](#c-calling-convention-x86-64-bit) section
above, the following is the standard (?) way on *32-bit x86*:

- First and foremost, the callee must preserve its caller's stack frame, then
    initialize a new, separate stack frame:

    ```asm
    push ebp
    mov ebp, esp    ; (1)
    ```

- Then, the callee is free to allocate local variables:

    ```asm
    sub esp, 12
    ```

- At the end of function body, the callee must restore its caller's original stack
    frame. `add esp, 12` is now not necessary, the code should be:

    ```asm
    mov esp, ebp    ; ebp should not have been altered since (1)
    pop ebp
    ret
    ```
