"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
C_PUSH = 'C_PUSH'
C_POP = 'C_POP'
C_ARITHMETIC = 'C_ARITHMETIC'


class Parser:
    """
    # Parser
    
    Handles the parsing of a single .vm file, and encapsulates access to the
    input code. It reads VM commands, parses them, and provides convenient 
    access to their components. 
    In addition, it removes all white space and comments.

    ## VM Language Specification

    A .vm file is a stream of characters. If the file represents a
    valid program, it can be translated into a stream of valid assembly 
    commands. VM commands may be separated by an arbitrary number of whitespace
    characters and comments, which are ignored. Comments begin with "//" and
    last until the line's end.
    The different parts of each VM command may also be separated by an arbitrary
    number of non-newline whitespace characters.

    - Arithmetic commands:
      - add, sub, and, or, eq, gt, lt
      - neg, not, shiftleft, shiftright
    - Memory segment manipulation:
      - push <segment> <number>
      - pop <segment that is not constant> <number>
      - <segment> can be any of: argument, local, static, constant, this, that, 
                                 pointer, temp
    - Branching (only relevant for project 8):
      - label <label-name>
      - if-goto <label-name>
      - goto <label-name>
      - <label-name> can be any combination of non-whitespace characters.
    - Functions (only relevant for project 8):
      - call <function-name> <n-args>
      - function <function-name> <n-vars>
      - return
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """Gets ready to parse the input file.

        Args:
            input_file (typing.TextIO): input file.
        """
        input_lines = input_file.read().splitlines()

        self.clean_input_lines = []
        for line in input_lines:
            line = line.strip()  # Remove leading/trailing whitespace
            if not line or line.startswith('//'):  # Skip empty lines and comments
                continue

            # Remove inline comments (if any)
            comment_index = line.find('//')
            if comment_index != -1:
                line = "".join(line[:comment_index].split())

            if line:  # Add non-empty instruction/label to the list
                self.clean_input_lines.append(line)

            if self.clean_input_lines:
                self.current_command_index: int = 0
                self.current_command: str = self.clean_input_lines[self.current_command_index]


    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        return self.current_command_index <= len(self.clean_input_lines) - 1

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current 
        command. Should be called only if has_more_commands() is true. Initially
        there is no current command.
        """
        if self.has_more_commands():
            self.current_command_index += 1
            if self.current_command_index >= len(self.clean_input_lines):
                return
            self.current_command = self.clean_input_lines[self.current_command_index]
        else:
            raise Exception("reached end of file")

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current VM command.
            "C_ARITHMETIC" is returned for all arithmetic commands.
            For other commands, can return:
            "C_PUSH", "C_POP", "C_LABEL", "C_GOTO", "C_IF", "C_FUNCTION",
            "C_RETURN", "C_CALL".
        """
        if self.current_command.startswith('push'):
            return C_PUSH
        elif self.current_command.startswith('pop'):
            return C_POP
        for arithmetic in ['add', 'sub', 'and', 'or', 'eq', 'gt', 'lt', 'neg', 'not', 'shiftleft', 'shiftright']:
            if self.current_command.startswith(arithmetic):
                return C_ARITHMETIC
        

    def arg1(self) -> str:
        """
        Returns:
            str: the first argument of the current command. In case of 
            "C_ARITHMETIC", the command itself (add, sub, etc.) is returned. 
            Should not be called if the current command is "C_RETURN".
        """
        current_command_words = self.current_command.split()
        if self.command_type() == C_PUSH or self.command_type() == C_POP:
            return current_command_words[1]
        elif self.command_type() == C_ARITHMETIC:
            return current_command_words[0]           

    def arg2(self) -> int:
        """
        Returns:
            int: the second argument of the current command. Should be
            called only if the current command is "C_PUSH", "C_POP", 
            "C_FUNCTION" or "C_CALL".
        """
        if self.command_type() == C_PUSH or self.command_type() == C_POP:
            current_command_words = self.current_command.split()
            return current_command_words[2]
            
# test()