"""
The main program.

TODO: Disable \\x20 at the middle of the string.
TODO: Add colors.
"""
import cmd
import traceback
import typing
import pyperclip # type: ignore
from utils.hextools import h2d, d2h, h2s_b, h2s_l, s2h

class UserError(RuntimeError):
    pass

def _escape_space(s: str) -> tuple[str, bool]:
    modified_s = s.replace(' ', '\\x20')
    return (modified_s, modified_s != s)

def print_string_insight_from_hex(h: str) -> None:
    codes, string = h2s_l(h)
    string, modified1 = _escape_space(repr(string)[2:-1])
    print(f"= (LITTLE endian) str {string}")
    print(f"   with ascii codes {codes}")

    codes, string = h2s_b(h)
    string, modified2 = _escape_space(repr(string)[2:-1])
    print(f"= (BIG endian)    str {string}")
    print(f"   with ascii codes {codes}")

    if modified1 or modified2:
        print()
        print("NOTE: \\x20 means SPACE character (ASCII 32 or 0x20).")

class SubCommandProcessor(cmd.Cmd):
    def __init__(self, prompt: str, original_cmd_name: str, original_cmd_handler: typing.Callable[[str], typing.Any]):
        super().__init__()
        self.original_cmd_name = original_cmd_name
        self.original_cmd_handler = original_cmd_handler
        self.prompt = prompt
    
    @typing.override
    def cmdloop(self, intro: typing.Any | None = None):
        print(f"Entering special context of command '{self.original_cmd_name}'.")
        print("Input an empty string to quit this context.")
        print()
        return super().cmdloop(intro)

    @typing.override
    def onecmd(self, line: str):
        if len(line) == 0:
            print(f"Exiting special context of command '{self.original_cmd_name}'.")
            return True
        
        try:
            return self.original_cmd_handler(line)
        except (UserError, ValueError, RuntimeError) as e:
            if isinstance(e, UserError) or isinstance(e, ValueError):
                print("*** " + str(e))
            else:
                # display error message
                traceback.print_exception(e)
            return False # don't stop
        finally:
            print()

def call_subshell(prompt: str, s: str, original_cmd_name: str, original_cmd_handler: typing.Callable[[str], typing.Any]):
    if len(s) > 0:
        raise UserError(f"Hey, this command does not take any argument.\nJust type '{original_cmd_name * 2}' and press Enter to start typing your string.")
    subshell = SubCommandProcessor(prompt, original_cmd_name, original_cmd_handler)
    subshell.cmdloop()
    return False

class CommandProcessor(cmd.Cmd):
    prompt = "> "

    @typing.override
    def onecmd(self, line: str):
        if len(line) == 0: return False
        try:
            return super().onecmd(line)
        except RuntimeError as e:
            if isinstance(e, UserError):
                print("*** " + str(e))
            else:
                # display error message
                traceback.print_exception(e)
            return False # don't stop
        except KeyboardInterrupt:
            return True
        finally:
            print()
    
    # def do_help(self, arg: str) -> bool | None:
    #     if len(arg.strip()) != 0:
    #         return super().do_help(arg)
        
    #     print("Documented commands (type help <command name> for more info)")
    #     print("============================================================")
    #     print("EOF, exit, q, quit       Exits the tool.")
    #     print("h, hex                   Inspects a hex value.")
    #     print("d, dec                   Inspects a decimal value.")
    #     print("s, str                   Inspects a string value.")

    def do_exit(self, _):
        """Exits the program. Same as commands 'EOF', 'q' and 'quit'."""
        return True

    def do_EOF(self, _): # pylint: disable=invalid-name
        """Exits the program. Same as commands 'exit', 'q' and 'quit'."""
        return True
    
    def do_q(self, _):
        """Exits the program. Same as commands 'EOF', 'exit' and 'quit'."""
        return True
    
    def do_quit(self, _):
        """Exits the program. Same as commands 'EOF', 'exit' and 'q'."""
        return True
    
    def do_hex(self, h: str):
        """Inspects a hex value, unsigned.

        For example:
            > hex 68732f2f
            = dec 1752379183 
            = (LITTLE endian) str //sh
            with ascii codes [47, 47, 115, 104]
            = (BIG endian)    str hs//
            with ascii codes [104, 115, 47, 47]
        
        If called without argument, opens a command context
        which autofills the 'hex' command for you ; you just
        have to enter the hex value. Try it!

        Note that '0x' characters at the middle of the value
        will be ignored. For example:

            > hex 0x68732f2f0x6e69622f
            = dec 7526411283028599343 
            = (LITTLE endian) str /bin//sh
            with ascii codes [47, 98, 105, 110, 47, 47, 115, 104]
            = (BIG endian)    str hs//nib/
            with ascii codes [104, 115, 47, 47, 110, 105, 98, 47]
        
        This is to speed up your workflow, especially when you
        are using GDB to solve a pwn challenge, and you notice
        several consecutive hex values that, when chained together,
        may represent some text. By copying the values and paste
        them into this tool without having to manually strip off
        all the redundant `0x` characters, you will be faster at
        solving the challenges!
        """
        h = h.strip()
        if len(h) == 0:
            return call_subshell("> hex ", h, 'hex', lambda h: self.do_h(h))
        
        h = h.replace('0x', '')
        if len(h) == 0:
            raise UserError("You must be trolling me.")
        
        if h.startswith('-'):
            raise UserError("This command can only inspect UNSIGNED hex values.")
        
        try:
            d = h2d(h)
            if d < 0:
                raise UserError("This command can only inspect UNSIGNED hex values.")
            
            print(f"= dec {d} ")

            print_string_insight_from_hex(h)
        except ValueError as e:
            raise UserError(str(e))
    
    def do_dec(self, d: str):
        """Inspects a decimal value, unsigned.
        
        For example:

            > dec 1752379183
            = hex 0x68732f2f
            = (LITTLE endian) str //sh
            with ascii codes [47, 47, 115, 104]
            = (BIG endian)    str hs//
            with ascii codes [104, 115, 47, 47]

        If called without argument, opens a command context
        which autofills the 'dec' command for you ; you just
        have to enter the decimal value. Try it!
        """
        if len(d) == 0:
            return call_subshell("> dec ", d, 'dec', lambda d: self.do_d(d))

        try:
            i = int(d, 10)
            if i < 0:
                raise UserError("This command can only inspect UNSIGNED decimal values.")
            
            h = d2h(i)
            print(f"= hex {h}")

            print_string_insight_from_hex(h)
        except ValueError as e:
            raise UserError(str(e))

    def do_str(self, s: str):
        """Inspects a string value.

        For example:

            > str /bin/sh
            LITTLE endian:
                hex = 0x68732f6e69622f
                dec = 29400045130965551
            BIG endian:
                hex = 0x2f62696e2f7368
                dec = 13337528865092456
        
        Note that the leading and trailing spaces, if any, will be stripped.
        In case you want to inspect string values with leading and trailing spaces,
        it is best to open an 'str' command context - see below.

        If called without argument, opens a command context
        which autofills the 'str' command for you ; you just
        have to enter the string value. Try it!
        """
        if len(s) == 0:
            return call_subshell("> str ", s, 'str', lambda s: self.do_s(s))

        dec_little, hex_little, dec_big, hex_big = s2h(s)
        print("LITTLE endian:")
        print(f"    hex = {hex_little}")
        print(f"    dec = {dec_little}")
        print("BIG endian:")
        print(f"    hex = {hex_big}")
        print(f"    dec = {dec_big}")
    
    def do_h(self, h: str):
        """Shorthand for command 'hex'."""
        return self.do_hex(h)

    def do_d(self, d: str):
        """Shorthand for command 'dec'."""
        return self.do_dec(d)

    def do_s(self, s: str):
        """Shorthand for command 'str'."""
        return self.do_str(s)
    
    def do_aslr(self, s: str):
        """Displays Linux command to disable/enable ASLR (Address Space Layout Randomization),
        and if possible, copy this command to clipboard.

        Usage:
        
            > aslr
            echo 0 | sudo tee /proc/sys/kernel/randomize_va_space

            This command has been copied to clipboard for you.

            > aslr 0
            echo 0 | sudo tee /proc/sys/kernel/randomize_va_space

            This command has been copied to clipboard for you.

            > aslr 1
            echo 1 | sudo tee /proc/sys/kernel/randomize_va_space

            > aslr 2
            echo 2 | sudo tee /proc/sys/kernel/randomize_va_space
        
        Note that we don't use sysctl to accomplish these tasks, like:
            $ sudo sysctl kernel.randomize_va_space=0
        since by doing this, the setting is permanent, which might put your system at risk - whereas
        the commands provided by us configure the setting temporarily ; it'll be reset to default after
        a reboot.

        More info: https://askubuntu.com/questions/318315/how-can-i-temporarily-disable-aslr-address-space-layout-randomization
        """

        if s == "":
            s = "0"
        if s not in ["0", "1", "2"]:
            raise UserError(f"Argument not supported: {s}. Type \"help aslr\".")
        cmd = f"echo {s} | sudo tee /proc/sys/kernel/randomize_va_space"
        print(cmd)
        pyperclip.copy(cmd) # type: ignore
        print("")
        print("This command has been copied to clipboard for you.")
        print("If you cannot paste, please copy it manually, or refer to")
        print("some potential clipboard issues here:")
        print("https://pypi.org/project/pyperclip/")

if __name__ == '__main__':

    print("Pwners' Data Converter Interactive")
    print("Type 'help' for usage.")
    print()
    try:
        CommandProcessor().cmdloop()
    except KeyboardInterrupt:
        print()
