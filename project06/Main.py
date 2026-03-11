import os
import sys
import typing
from SymbolTable import SymbolTable
from Parser import Parser
from Code import Code


def assemble_file(
        input_file: typing.TextIO, output_file: typing.TextIO) -> None:
    """Assembles a single file.

    Args:
        input_file (typing.TextIO): the file to assemble.
        output_file (typing.TextIO): writes all output to this file.
    """
    pre_run__parser = Parser(input_file)
    symbol_table = SymbolTable()

    #first run (loop labels):
    
    while pre_run__parser.has_more_commands(): 
        pre_run__parser.advance()
        if pre_run__parser.command_type() == "L_COMMAND":
            symbol_table.add_entry(pre_run__parser.symbol(), pre_run__parser.get_label_index()) 
    
    #main run:
    input_file.seek(0)
    main_run_parser = Parser(input_file)
    variable_counter = 16

    while main_run_parser.has_more_commands(): 

        main_run_parser.advance()

        #if the line is empty after cutting the comments and white spaces:
        if main_run_parser.get_do_not_process() == True:
            continue
        if main_run_parser.command_type() == "C_COMMAND":
            output_file.write("111" + Code.comp(main_run_parser.comp()) + Code.dest(main_run_parser.dest()) + Code.jump(main_run_parser.jump()) +"\n")
            continue
        if main_run_parser.command_type() == "L_COMMAND":
            continue
        
        #if we got here, we are dealing with an A instruction:
        symbol = main_run_parser.symbol()
        if symbol.isdigit():
            address = int(symbol)
        else:
            if symbol_table.contains(symbol):
                address = symbol_table.get_address(symbol)
            else:
                symbol_table.add_entry(symbol, variable_counter)
                address = variable_counter
                variable_counter += 1
        binary_address = format(address, '015b')
        output_file.write("0" + binary_address + "\n")
        


if "__main__" == __name__:
    # Parses the input path and calls assemble_file on each input file.
    # This opens both the input and the output files!
    # Both are closed automatically when the code finishes running.
    # If the output file does not exist, it is created automatically in the
    # correct path, using the correct filename.
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: Assembler <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_assemble = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
    else:
        files_to_assemble = [argument_path]
    for input_path in files_to_assemble:
        filename, extension = os.path.splitext(input_path)
        if extension.lower() != ".asm":
            continue
        output_path = filename + ".hack"
        with open(input_path, 'r') as input_file, \
                open(output_path, 'w') as output_file:
            assemble_file(input_file, output_file)



