import typing


class Parser:
    """Encapsulates access to the input code. Reads an assembly program
    by reading each command line-by-line, parses the current command,
    and provides convenient access to the commands components (fields
    and symbols). In addition, removes all white space and comments.
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """Opens the input file and gets ready to parse it.

        Args:
            input_file (typing.TextIO): input file.
        """
        # A good place to start is to read all the lines of the input:
        self.input_lines = input_file.read().splitlines()
        self.current_index = 0
        self.current_label_index = 0;
        self.current_command = None
        self.do_not_process_command = False

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        # Your code goes here!
        if self.current_index < len(self.input_lines):
            return True
        else:
            return False

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current command.
        Should be called only if has_more_commands() is true.
        """
        line = self.input_lines[self.current_index]
        line = line.split("//")[0].strip()
        line = line.replace(" ", "")
        self.current_command = line
        self.current_index += 1

        if self.current_command:
            self.do_not_process_command = False
        elif not self.current_command:
            self.do_not_process_command = True

        if (self.command_type() == "C_COMMAND" and self.do_not_process_command == False) or (self.command_type() == "A_COMMAND"):
            self.current_label_index += 1
        

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current command:
            "A_COMMAND" for @Xxx where Xxx is either a symbol or a decimal number
            "C_COMMAND" for dest=comp;jump
            "L_COMMAND" (actually, pseudo-command) for (Xxx) where Xxx is a symbol
        """
        if self.current_command.startswith("@"):
            return "A_COMMAND"
        elif (self.current_command.startswith("(") and
              self.current_command.endswith(")")):
            return "L_COMMAND"
        else:
            return "C_COMMAND"

    def symbol(self) -> str:
        """
        Returns:
            str: the symbol or decimal Xxx of the current command @Xxx or
            (Xxx). Should be called only when command_type() is "A_COMMAND" or 
            "L_COMMAND".
        """
        len_symbol = len(self.current_command)
        if self.command_type() == "L_COMMAND":
            return self.current_command[1:len_symbol-1]
        else:
            return self.current_command[1:len_symbol]

    def dest(self) -> str:
        """
        Returns:
            str: the dest mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """

        if "=" in self.current_command:  
            dest_sign = self.current_command.find("=")
            return self.current_command[0:dest_sign]
        else:  
            return ""  

    
    def comp(self) -> str:
        if "=" in self.current_command:
            dest_sign = self.current_command.find("=")
            comp_sign = self.current_command.find(";")
            if comp_sign == -1:
                return self.current_command[dest_sign+1:]
            return self.current_command[dest_sign+1:comp_sign]
        else:
            comp_sign = self.current_command.find(";")
            if comp_sign == -1:
                return self.current_command
            return self.current_command[:comp_sign]

    def jump(self) -> str:
        """
        Returns:
            str: the jump mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        parts = self.current_command.split(";")
        if len(parts) == 2 and parts[1].strip():
                return parts[1].strip()
        return ""

    def get_label_index(self) -> int:
        """
        Returns:
            int: the index to put as an address of a new label
        """
        return self.current_label_index
    
    def get_do_not_process(self) -> bool:
        """
        Returns:
            bool: true if the command shouldnt be proccessed, false otherwise.
        """
        return self.do_not_process_command
