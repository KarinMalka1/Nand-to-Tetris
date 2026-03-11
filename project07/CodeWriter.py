import typing
import os

class CodeWriter:
    """Translates VM commands into Hack assembly code."""

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """
        self.file_name = None
        self.output = output_stream
        self.label_counter = 0

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
        
        new_file_name, extension = os.path.splitext(os.path.basename(filename))
        self.file_name = new_file_name

    def write_arithmetic(self, command: str) -> None:
        """Writes assembly code that is the translation of the given 
        arithmetic command. For the commands eq, lt, gt, you should correctly
        compare between all numbers our computer supports, and we define the
        value "true" to be -1, and "false" to be 0.

        Args:
            command (str): an arithmetic command.
        """

        binary_commands = {
            "add": "M = D + M",
            "sub": "M = M - D",
            "and": "M = D & M",
            "or":  "M = D|M"
        }

        unary_commands = {
            "neg": "M = -M",
            "not": "M = !M",
            "shiftleft": "M = M<<",   
            "shiftright": "M = M>>"
        }
        comparison_commands = {
            "eq": "JEQ",
            "lt": "JLT",
            "gt": "JGT"
        }

        if command in binary_commands:
            self.output.write("//" + command + "\n")
            self.output.write("@SP" + "\n" + "M = M - 1" + "\n" + "A = M" +"\n" + "D = M" + "\n") 
            self.output.write("@SP" + "\n" + "M = M - 1" + "\n" + "A = M" + "\n")       
            self.output.write(binary_commands[command] + "\n")
            self.output.write("@SP" + "\n" + "M = M + 1" + "\n")

        elif command in unary_commands:
            self.output.write("//" + command + "\n")
            self.output.write("@SP" + "\n" + "A = M - 1" + "\n")
            self.output.write(unary_commands[command] + "\n")

        elif command in {"eq", "lt", "gt"}:
            self.output.write("//" + command + "\n")

            self.label_counter += 1
            label_activate = "LABEL_START" + str(self.label_counter)
            label_end = "LABEL_END" + str(self.label_counter)

            comparison_command = comparison_commands[command]

            self.output.write("@SP" + "\n" + "M = M - 1" + "\n" + "A = M" +"\n" + "D = M" + "\n") 
            self.output.write("@SP" + "\n" + "M = M - 1" + "\n" + "A = M" + "\n" + "D = M - D" + "\n")    #gets the result of subtraction between the two values

            self.output.write("@" + label_activate + "\n")
            self.output.write("D;" + comparison_command + "\n")

            self.output.write("@SP" + "\n" + "A = M"  + "\n" + "M = 0" + "\n")   

            self.output.write("@" + label_end + "\n")
            self.output.write("0;JMP" + "\n")

            self.output.write("(" + label_activate + ")" + "\n")    #the label contenst starts here
            self.output.write("@SP" + "\n" + "A = M" + "\n" + "M = -1" + "\n")        #puts true in the stack 

            self.output.write("(" + label_end + ")" + "\n")
            self.output.write("@SP" + "\n" + "M = M + 1" + "\n")           #after putting some value in the stack, we incrememnt the sp


       

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

        self.output.write("//" + command + " " + segment + " " + str(index) + "\n")

        identical_implementation_segments_map = {
            "local": "LCL",
            "argument": "ARG",
            "this": "THIS",
            "that": "THAT"
        }
        if command == "C_PUSH" :
            if segment == "constant": 
                self.output.write("@" + str(index) + "\n" + "D = A" + "\n")
                self.output.write("@SP" + "\n" + "A = M" + "\n" + "M = D" + "\n")
                self.output.write("@SP" + "\n" + "M = M + 1" + "\n")

            elif segment in identical_implementation_segments_map:
                self.output.write("@" + str(index) + "\n" + "D = A" + "\n")
                self.output.write("@" + identical_implementation_segments_map[segment]  + "\n" + "A = M + D" + "\n" + "D = M" + "\n")
                self.output.write("@SP" + "\n" + "A = M" + "\n" + "M = D" + "\n")
                self.output.write("@SP" + "\n" + "M = M + 1" + "\n")
            
            elif segment == "static":
                static_name = self.file_name + "." + str(index)
                self.output.write("@" + static_name + "\n" + "D = M" + "\n")
                self.output.write("@SP" + "\n" + "A = M" + "\n" + "M = D" + "\n")
                self.output.write("@SP" + "\n" + "M = M + 1" + "\n")
            
            elif segment == "temp":
                addr = 5 + index
                self.output.write("@" + str(addr) + "\n" + "D = M" + "\n")
                self.output.write("@SP" + "\n" + "A = M" + "\n" + "M = D" + "\n")
                self.output.write("@SP" + "\n" + "M = M + 1" + "\n")
            
            elif segment == "pointer":
                self.output.write("@R" + str(3 + index) + "\n" + "D = M" + "\n")
                self.output.write("@SP" + "\n" + "A = M" + "\n" + "M = D" + "\n")
                self.output.write("@SP" + "\n" + "M = M + 1" + "\n")

        if command == "C_POP":
            if segment in identical_implementation_segments_map:
                self.output.write("@" + str(index) + "\n" + "D = A" + "\n")
                self.output.write("@" + identical_implementation_segments_map[segment] + "\n" + "D = M + D" + "\n" + "@R13" + "\n" + "M = D" + "\n")
                self.output.write("@SP" + "\n" + "M = M - 1" + "\n" + "A = M" + "\n" + "D = M" + "\n")
                self.output.write("@R13" + "\n" + "A = M" + "\n" + "M = D" + "\n")

            elif segment == "static":
                static_name = self.file_name + "." + str(index)
                self.output.write("@SP" + "\n" + "M = M - 1" + "\n" + "A = M" + "\n" + "D = M" + "\n")
                self.output.write("@" + static_name + "\n" + "M = D" + "\n")

            elif segment == "temp":
                addr = 5 + index
                self.output.write("@" + str(addr) + "\n" + "D = A" + "\n" + "@R13" + "\n" + "M = D" + "\n")
                self.output.write("@SP" + "\n" + "M = M - 1" + "\n" + "A = M" + "\n" + "D = M" + "\n")
                self.output.write("@R13" + "\n" + "A = M" + "\n" + "M = D" + "\n")
            
            elif segment == "pointer":
                    self.output.write("@R" + str(3 + index) + "\n" + "D = A" + "\n" + "@R13" + "\n" "M = D" + "\n")
                    self.output.write("@SP" + "\n" + "M = M - 1" + "\n" + "A = M" + "\n" + "D = M" + "\n")
                    self.output.write("@R13" + "\n" + "A = M" + "\n" + "M = D" + "\n")
                # !!!!!!!!!!!!!!!!!! to save all the magic numbers as constants 


                

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
