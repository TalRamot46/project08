"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
from Parser import C_PUSH, C_POP, C_ARITHMETIC
import textwrap
LOCAL = 'local'
ARGUMENT = 'argument'
THIS = 'this'
THAT = 'that'
CONSTANT = 'constant'
STATIC = 'static'
POINTER = 'pointer'
TEMP = 'temp'


class CodeWriter:
    """Translates VM commands into Hack assembly code."""

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """
        self.global_id = 0
        self.output_stream = output_stream

    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is 
        started.

        Args:
            filename (str): The name of the VM file.
        """
        # Your code goes here!
        # This function is useful when translating code that handles the
        # static segment. For example, in order to prevent collisions between two
        # .vm files which push/pop to the static segment, one can use the current
        # file's name in the assembly variable's name and thus differentiate between
        # static variables belonging to different files.
        # To avoid problems with Linux/Windows/MacOS differences with regards
        # to filenames and paths, you are advised to parse the filename in
        # the function "translate_file" in Main.py using python's os library,
        # For example, using code similar to:
        # input_filename, input_extension = os.path.splitext(os.path.basename(input_file.name))
        pass

    def write_asm(self, assembly_command: str) -> None:
        assembly_code_no_leading_spaces = ""
        lines = assembly_command.strip().split('\n')
        assembly_code_no_leading_spaces = '\n'.join(line.lstrip() for line in lines)
        self.output_stream.write(assembly_code_no_leading_spaces + "\n\n")

    def write_arithmetic(self, arithmetic_command: str) -> None:
        """Writes assembly code that is the translation of the given 
        arithmetic command. For the commands eq, lt, gt, you should correctly
        compare between all numbers our computer supports, and we define the
        value "true" to be -1, and "false" to be 0.

        Args:
            command (str): an arithmetic command.
        """
        self.global_id += 1
        i = self.global_id
        assembly_command = ""
        if arithmetic_command in ['add', 'and', 'or']:
            sign = {'add': "+", 'and': "&", 'or': "|"}[arithmetic_command]
            assembly_command = \
            f"""// {arithmetic_command}
                // SP--
                @SP
                M=M-1
                // D = SP
                A=M
                D=M
                // SP--
                @SP
                M=M-1
                // D {sign}= SP
                A=M
                D=D{sign}M
                // SP = D
                M=D
                // SP++
                @SP
                M=M+1
                """
        elif arithmetic_command == 'sub':
            assembly_command = \
            f"""// sub
                // SP--
                @SP
                M=M-1
                // D = SP
                A=M
                D=M
                // SP--
                @SP
                M=M-1
                // D -= SP
                A=M
                D=D-M
                // D = -D
                D=-D
                // SP = D
                M=D
                // SP++
                @SP
                M=M+1"""
        elif arithmetic_command in ['eq', 'gt', 'lt']:
            sign = {'eq': "JEQ", 'gt': "JGT", 'lt': "JLT"}[arithmetic_command]
            assembly_command = \
                f"""// {arithmetic_command}
                // SP--
                @SP
                M=M-1
                // D = SP
                A=M
                D=M
                @R14 // *R14 = --SP
                M=D
                @SP
                M=M-1
                A=M
                D=M // D = --SP
                @R13 // R13 = D
                M=D

                // Stack:
                // R13: value1
                // R14: value2
                // SP -> __

                // compare R13(=D for now) and R14
                @D_is_positive{i}
                D;JGT
                @D_is_negative{i}
                D;JLT
                @Same_sign{i}
                0;JMP

                (D_is_positive{i})
                    @R14 // D = R14
                    D=M
                    @Same_sign{i}
                    D;JGT
                    // R13 > 0 & R14 <= 0
                    {f"@True{i}" if arithmetic_command == 'gt' else f"@False{i}"}
                    0;JMP

                (D_is_negative{i})
                    @R14 // D = R14
                    D=M
                    @Same_sign{i}
                    D;JLT
                    // R13 < 0 & R14 >= 0   
                    {f"@True{i}" if arithmetic_command == 'lt' else f"@False{i}"}
                    0;JMP

                (Same_sign{i})
                    @R13 // D = R13
                    D=M
                    @R14 // M = R14
                    D=D-M
                    @True{i}
                    D;{sign}

                (False{i})
                    // False => SP = 0
                    @SP
                    A=M
                    M=0
                    @End{i}
                    0;JMP
                
                (True{i})
                    // SP = -1
                    @SP
                    A=M
                    M=1
                    M=-M

                (End{i})
                    // SP++
                    @SP
                    M=M+1"""

        elif arithmetic_command in ['neg', 'not']:
            sign = {'neg': "-", 'not': "!"}[arithmetic_command]
            assembly_command = \
            f"""// {arithmetic_command}
                // SP--
                @SP
                M=M-1
                // SP = {sign}SP
                A=M
                D=M
                D={sign}D
                M=D
                // SP++
                @SP
                M=M+1
                """
        elif arithmetic_command in ['shiftleft', 'shiftright']:
            if arithmetic_command == 'shiftleft':
                assembly_command = \
                f"""// {arithmetic_command}
                    @SP     // SP--
                    M=M-1
                    A=M     // *SP = *SP + *SP
                    D=M
                    M=D+M 
                    @SP     // SP++
                    M=M+1"""
            elif arithmetic_command == 'shiftright':
                assembly_command = \
                f"""// {arithmetic_command}
                    @2      // R13 = Divisor
                    D=A
                    @R13
                    M=D
                    @SP     // D = *(--SP)
                    M=M-1
                    A=M
                    D=M

                    @CONTINUE{self.global_id}   // Negative Divisor for negative number
                    D;JGT
                    D=-D

                    (CONTINUE{self.global_id} )
                        @R14    // R14 = Quotient
                        M=0

                    (DIVISION_LOOP{self.global_id} )
                        @R13
                        D=D-M
                        @R14
                        M=M+1
                        @DIVISION_LOOP{self.global_id}
                        D;JGT
                        
                        @FINISHED{self.global_id} 
                        D;JEQ
                        @R14    // D < 0 => decrementing quotient 
                        M=M-1


                    (FINISHED{self.global_id} )
                        @SP
                        A=M
                        D=M
                        @DONT_NEGATE_RESULT{self.global_id}
                        D;JGT

                        @R14   // Negate Result
                        D=M
                        D=-D
                        @CONTINUE{self.global_id}
                        0;JMP

                        (DONT_NEGATE_RESULT{self.global_id})
                            @R14    // *SP=Quotient
                            D=M

                        (CONTINUE{self.global_id})
                            @SP     
                            A=M
                            M=D

                            @SP     // SP++
                            M=M+1"""

        self.write_asm(assembly_command)
        self.global_id += 1

       
    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        """Writes assembly code that is the translation of the given 
        command, where command is either C_PUSH or C_POP.

        Args:
            command (str): "C_PUSH" or "C_POP".
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """
        # Your code goes here!
        # Note: each reference to "static i" appearing in the file Xxx.vm should
        # be translated to the assembly symbol "Xxx.i". In the subsequent
        # assembly process, the Hack assembler will allocate these symbolic
        # variables to the RAM, starting at address 16.
        
        assembly_command = ""
        if segment in [LOCAL, ARGUMENT, THIS, THAT]:
            assembly_command = self.write_local_argument_this_that(command, segment, index)
        elif segment == CONSTANT:
            assembly_command = self.write_constant(command, index)
        elif segment == STATIC:
            assembly_command = self.write_static(command, index)
        elif segment == TEMP:
            assembly_command = self.write_temp(command, index)
        elif segment == POINTER:
            assembly_command = self.write_pointer(command, index)
        self.write_asm(assembly_command)

    def write_local_argument_this_that(self, command: str, segment: str, index: int) -> str:
        # VM:       push segment index
        # Logic:    addr = segmentPointer + i
        #           *SP = *addr
        #           SP++
        segment_symbol = {
                LOCAL : 'LCL',
                ARGUMENT: 'ARG',
                THIS: 'THIS',
                THAT: 'THAT'
            }[segment]
        
        assembly_command = ""
        if command == C_PUSH:
            assembly_command = \
            f"""// push {segment} {index}
                // addr = segment_pointer + i
                @{segment_symbol} // D = {segment_symbol}
                D=M
                @{index} // D = {segment_symbol} + i
                D=D+A
                // *SP = *addr
                A=D // D = *addr
                D=M
                @SP // *SP = *addr
                A=M
                M=D
                // SP++
                @SP
                M=M+1"""
            
        elif command == C_POP:
            assembly_command = \
            f"""// pop {segment} {index}  
                // addr = segment_pointer + i
                @{segment_symbol} // D = {segment_symbol}
                D=M
                @{index} // D = {segment_symbol} + i
                D=D+A
                @R13 // *R13=D
                M=D
                // SP--
                @SP
                M=M-1
                A=M
                D=M // D=*SP (to be popped)
                // *addr = D
                @R13
                A=M
                M=D"""
        return assembly_command

    def write_constant(self, command: str, index: int) -> str:
        assembly_command = ""
        if command == C_PUSH:
            assembly_command = \
            f"""// push constant {index}  
                // *SP = {index}
                @{index}
                D=A
                @SP
                A=M
                M=D
                // SP++
                @SP
                M=M+1"""
        return assembly_command

    def write_static(self, command: str, index: str) -> str:
        assembly_command = ""
        if command == C_PUSH:
            assembly_command = \
            f"""// push static {index}
                // addr = segment_pointer + i
                @R16 // D = 16
                D=A
                @{index} // D = 16 + i
                D=D+A
                // *SP = *addr
                A=D // D = *addr
                D=M
                @SP // *SP = *addr
                A=M
                M=D
                // SP++
                @SP
                M=M+1"""
            
        elif command == C_POP:
            assembly_command = \
            f"""// pop static {index}  
                // addr = 16 + i
                @{index} // D = 16 + i
                D=A
                @16
                D=D+A
                @R13 // *R13=D
                M=D
                // SP--
                @SP
                M=M-1
                A=M
                D=M // D=*SP (to be popped)
                // *addr = D
                @R13
                A=M
                M=D"""
        return assembly_command
            
    def write_temp(self, command: str, index: str) -> str:
        assembly_command = ""
        if command == C_PUSH:
            assembly_command = \
            f"""// push temp {index}
                // addr = 5 + i
                @{index} // D = 5 + i
                D=A
                @5
                D=D+A
                // *SP = *addr
                A=D // D = *addr
                D=M
                @SP // *SP = *addr
                A=M
                M=D
                // SP++
                @SP
                M=M+1"""
            
        elif command == C_POP:
            assembly_command = \
            f"""// pop temp {index}  
                // addr = 5 + i
                @{index} // D = 5 + i
                D=A
                @5
                D=D+A
                @R13 // *R13=D
                M=D
                // SP--
                @SP
                M=M-1
                A=M
                D=M // D=*SP (to be popped)
                // *addr = D
                @R13
                A=M
                M=D"""
        return assembly_command

    def write_pointer(self, command: str, index: str) -> str:
        pointer_name = {'0': 'THIS', '1': 'THAT'}[index]
        assembly_command = ""
        if command == C_PUSH:
            assembly_command = \
            f"""// push pointer {index}
                @{pointer_name}
                D=M
                @SP // *SP=D
                A=M
                M=D
                @SP   // SP++
                M=M+1"""
        elif command == C_POP:
            assembly_command = \
            f"""// pop pointer {index}
                @SP   // SP--
                M=M-1
                A=M
                D=M
                @{pointer_name}
                M=D"""
        return assembly_command

##########################################################################################
    def write_label(self, label: str) -> None:
        """Writes assembly code that affects the label command. 
        Let "Xxx.foo" be a function within the file Xxx.vm. The handling of
        each "label bar" command within "Xxx.foo" generates and injects the symbol
        "Xxx.foo$bar" into the assembly code stream.
        When translating "goto bar" and "if-goto bar" commands within "foo",
        the label "Xxx.foo$bar" must be used instead of "bar".

        Args:
            label (str): the label to write.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        pass
    
    def write_goto(self, label: str) -> None:
        """Writes assembly code that affects the goto command.

        Args:
            label (str): the label to go to.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        pass
    
    def write_if(self, label: str) -> None:
        """Writes assembly code that affects the if-goto command. 

        Args:
            label (str): the label to go to.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        pass
    
    def write_function(self, function_name: str, n_vars: int) -> None:
        """Writes assembly code that affects the function command. 
        The handling of each "function Xxx.foo" command within the file Xxx.vm
        generates and injects a symbol "Xxx.foo" into the assembly code stream,
        that labels the entry-point to the function's code.
        In the subsequent assembly process, the assembler translates this 
        symbol into the physical address where the function code starts.

        Args:
            function_name (str): the name of the function.
            n_vars (int): the number of local variables of the function.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "function function_name n_vars" is:
        # (function_name)       // injects a function entry label into the code
        # repeat n_vars times:  // n_vars = number of local variables
        #   push constant 0     // initializes the local variables to 0
        pass
    
    def write_call(self, function_name: str, n_args: int) -> None:
        """Writes assembly code that affects the call command. 
        Let "Xxx.foo" be a function within the file Xxx.vm.
        The handling of each "call" command within Xxx.foo's code generates and
        injects a symbol "Xxx.foo$ret.i" into the assembly code stream, where
        "i" is a running integer (one such symbol is generated for each "call"
        command within "Xxx.foo").
        This symbol is used to mark the return address within the caller's 
        code. In the subsequent assembly process, the assembler translates this
        symbol into the physical memory address of the command immediately
        following the "call" command.

        Args:
            function_name (str): the name of the function to call.
            n_args (int): the number of arguments of the function.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "call function_name n_args" is:
        # push return_address   // generates a label and pushes it to the stack
        # push LCL              // saves LCL of the caller
        # push ARG              // saves ARG of the caller
        # push THIS             // saves THIS of the caller
        # push THAT             // saves THAT of the caller
        # ARG = SP-5-n_args     // repositions ARG
        # LCL = SP              // repositions LCL
        # goto function_name    // transfers control to the callee
        # (return_address)      // injects the return address label into the code
        pass
    
    def write_return(self) -> None:
        """Writes assembly code that affects the return command."""
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "return" is:
        # frame = LCL                   // frame is a temporary variable
        # return_address = *(frame-5)   // puts the return address in a temp var
        # *ARG = pop()                  // repositions the return value for the caller
        # SP = ARG + 1                  // repositions SP for the caller
        # THAT = *(frame-1)             // restores THAT for the caller
        # THIS = *(frame-2)             // restores THIS for the caller
        # ARG = *(frame-3)              // restores ARG for the caller
        # LCL = *(frame-4)              // restores LCL for the caller
        # goto return_address           // go to the return address
        pass

