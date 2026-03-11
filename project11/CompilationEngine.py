"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
from JackTokenizer import JackTokenizer
from VMWriter import VMWriter
from SymbolTable import SymbolTable


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    def __init__(self, input_stream: "JackTokenizer", vm_writer: "VMWriter", symbol_table: "SymbolTable") -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        self.tokenizer = input_stream
        self.vm_writer = vm_writer
        self.symbol_table = symbol_table
        self.curr_class = None
        self.label_counter = 0

    def compile_class(self) -> None:
        """Compiles a complete class."""
        static_field = {"static", "field"}
        subroutine_declaration = {"constructor", "function", "method"}
        #class:
        self.tokenizer.advance()
        #class name:
        self.tokenizer.advance()
        self.curr_class = self.tokenizer.identifier()
        # {:
        self.tokenizer.advance()
        self.tokenizer.advance()

        while self.tokenizer.has_more_tokens():
            if self.tokenizer.token_type() == "KEYWORD" and self.tokenizer.keyword().lower() in static_field:
                self.compile_class_var_dec()
            else:
                break

        while self.tokenizer.has_more_tokens():
            if self.tokenizer.token_type() == "KEYWORD" and self.tokenizer.keyword().lower() in subroutine_declaration:
                self.compile_subroutine()
            else:
                break

        #'}':
        #self.tokenizer.advance()    #!!!!!!!!!!!!!!! I deleted it, if it should be here we should delete the advance() call in the end of compile_sub_routine() instead.


    def compile_class_var_dec(self) -> None:
        """
        Compiles a static or field variable declaration.
        Grammar: ('static' | 'field') type varName (',' varName)* ';'
        """
        #field or static:
        kind = self.tokenizer.keyword()

        #type of the variable:
        self.tokenizer.advance()
        var_type_name = self.get_type()
        
        #var name:
        self.tokenizer.advance()
        self.symbol_table.define(self.tokenizer.identifier(), var_type_name, kind)

        #any additional vars in the same line:
        while self.tokenizer.has_more_tokens():
            self.tokenizer.advance()
            if self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == ",":
                self.tokenizer.advance()
                self.symbol_table.define(self.tokenizer.identifier(), var_type_name, kind)
            else:
                break

        self.tokenizer.advance()


    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        self.symbol_table.start_subroutine()
        subroutine_type = self.tokenizer.keyword().lower()

        #void or type:
        self.tokenizer.advance()
        return_type_name = self.get_type()                  #!!!!!!!!!!!! not used, may cause problems (maybe with non void subroutines)
        
        #subroutine name:
        self.tokenizer.advance()
        subroutine_name = self.curr_class + "." + self.tokenizer.identifier()

        # (:
        self.tokenizer.advance()

        #parameter list: 
        self.tokenizer.advance()
        param_num = self.compile_parameter_list()

        self.tokenizer.advance()  
        self.tokenizer.advance() 
        
        local_counter = 0
        while self.tokenizer.has_more_tokens():
            if self.tokenizer.token_type() == "KEYWORD" and self.tokenizer.keyword().lower() == "var":
                local_counter += self.compile_var_dec()
            else:
                break
        if subroutine_type == "method":
            self.symbol_table.define("this", self.curr_class, "ARG")
            param_num += 1
        self.vm_writer.write_function(subroutine_name, local_counter)

        #!!!!!!!!!!! all this part should be fine but maybe to check
        if subroutine_type == "constructor":
                fields_number = self.symbol_table.var_count("FIELD")
                self.vm_writer.write_push("CONST", fields_number)
                self.vm_writer.write_call("Memory.alloc", 1)
                self.vm_writer.write_pop("POINTER", 0)
        elif subroutine_type == "method":
                self.vm_writer.write_push("ARG", 0)
                self.vm_writer.write_pop("POINTER", 0)

        self.compile_statements()
        self.tokenizer.advance()  

    
    def compile_parameter_list(self) -> int:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        param_number = 0
        if self.tokenizer.symbol() != ")":
            param_type = self.get_type()
            self.tokenizer.advance()

            param_number += 1
            self.symbol_table.define(self.tokenizer.identifier(), param_type, "ARG")

            self.tokenizer.advance()

            while self.tokenizer.symbol() == ",":
                self.tokenizer.advance()

                param_type = self.get_type()
                self.tokenizer.advance()

                param_number += 1
                self.symbol_table.define(self.tokenizer.identifier(), param_type, "ARG")

                self.tokenizer.advance()

        return param_number
        

    def compile_var_dec(self) -> int:
        """Compiles a var declaration."""
        vars_number = 1
        #var type:
        self.tokenizer.advance()
        var_type = self.get_type()

        #var name:
        self.tokenizer.advance()
        self.symbol_table.define(self.tokenizer.identifier(), var_type, "VAR")

        self.tokenizer.advance()

        #any additional variables in the same line:
        while self.tokenizer.symbol() == ",":
            vars_number += 1
            self.tokenizer.advance()

            self.symbol_table.define(self.tokenizer.identifier(), var_type, "VAR")
            self.tokenizer.advance()

        self.tokenizer.advance()
        return vars_number

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        while self.tokenizer.has_more_tokens():
            if self.tokenizer.token_type() == "KEYWORD":
                statement_word = self.tokenizer.keyword().lower()

                if statement_word == "let":
                    self.compile_let()
                elif statement_word == "while":
                    self.compile_while()
                elif statement_word == "return":
                    self.compile_return()
                elif statement_word == "if":
                    self.compile_if()
                elif statement_word == "do":
                    self.compile_do()
                else:
                    break  
            else:
                break 

    def compile_do(self) -> None:
        """Compiles a do statement."""
        #function name, or class name, or var name:
        self.tokenizer.advance()
        identifier = self.tokenizer.identifier()

        self.tokenizer.advance()
        self.compile_function_call(identifier)

        self.vm_writer.write_pop("TEMP", 0)  

        self.tokenizer.advance()  

    def compile_function_call(self, name: str = None) -> None:
        arguments_num = 0

        #if the function is working on a class or var:
        if self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == ".":
            self.tokenizer.advance()               #!! till here
            function_name = self.tokenizer.identifier()
            self.tokenizer.advance() 
            if self.symbol_table.kind_of(name) != None:
                self.vm_writer.write_push(self.kind_to_segment(self.symbol_table.kind_of(name)),
                                           self.symbol_table.index_of(name))
                type_name = self.symbol_table.type_of(name)
                function_full_name = type_name + "." + function_name
                arguments_num += 1
            else:
                function_full_name = name + "." + function_name
        else:
            function_full_name = self.curr_class + "." + name
            self.vm_writer.write_push("POINTER", 0)
            arguments_num += 1

        self.tokenizer.advance()
        arguments_num += self.compile_expression_list()
        self.tokenizer.advance()

        self.vm_writer.write_call(function_full_name, arguments_num)

    def compile_let(self) -> None:
        """Compiles a let statement."""
        is_an_array = False

        #var name:
        self.tokenizer.advance()
        var_kind = self.kind_to_segment(self.symbol_table.kind_of(self.tokenizer.identifier()))
        var_index = self.symbol_table.index_of(self.tokenizer.identifier())

        self.tokenizer.advance()

        if self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == "[":
            is_an_array = True
            self.vm_writer.write_push(var_kind, var_index)
            self.tokenizer.advance()
            self.compile_expression()
            #calculates the offset:
            self.vm_writer.write_arithmetic("ADD")
            self.tokenizer.advance()
        #advance to the expression:    
        self.tokenizer.advance()  

        self.compile_expression()

        if is_an_array:
            self.vm_writer.write_pop("TEMP", 0)
            self.vm_writer.write_pop("POINTER", 1)
            self.vm_writer.write_push("TEMP", 0)
            self.vm_writer.write_pop("THAT", 0)
        else:
            self.vm_writer.write_pop(var_kind, var_index)
        
        self.tokenizer.advance()
    #!!!!!!!!!!! to check it:
    def kind_to_segment(self, kind):
        kind_to_segment_map = {
            "STATIC": "STATIC",
            "FIELD": "THIS",
            "ARG": "ARG",
            "VAR": "LOCAL"
        }
        return kind_to_segment_map[kind]

    def compile_while(self) -> None:
        """Compiles a while statement."""
        open_label = "WHILE" + "_" + str(self.label_counter)           #!!!!!!!!!!!!!!!!! maybe its possible to change the names of the labels?
        self.label_counter += 1
        close_label = "WHILE_END" + "_" + str(self.label_counter)

        self.vm_writer.write_label(open_label)

        #(:
        self.tokenizer.advance()
        #expression:
        self.tokenizer.advance()
        self.compile_expression()

        self.vm_writer.write_arithmetic("NOT")
        self.vm_writer.write_if(close_label)

        #{:
        self.tokenizer.advance()
        #while body:
        self.tokenizer.advance()
        self.compile_statements()

        self.vm_writer.write_goto(open_label)
        self.vm_writer.write_label(close_label)

        self.tokenizer.advance() 

    def compile_return(self) -> None:
        """Compiles a return statement."""

        #expression after return:
        self.tokenizer.advance()
        if self.tokenizer.token_type() != "SYMBOL" or self.tokenizer.symbol() != ";":
            self.compile_expression()
        else:
            self.vm_writer.write_push("CONST", 0)
        self.vm_writer.write_return()

        self.tokenizer.advance() 


    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        else_label = "ELSE" + "_" + str(self.label_counter)          #!!! maybe its possible to change the names of the labels also here?
        self.label_counter += 1
        close_label = "IF_END" + "_" + str(self.label_counter)

        #(:
        self.tokenizer.advance()
        #expression:
        self.tokenizer.advance()
        self.compile_expression()

        self.vm_writer.write_arithmetic("NOT")
        self.vm_writer.write_if(else_label)

        #{:
        self.tokenizer.advance()
        #if body:
        self.tokenizer.advance()
        self.compile_statements()

        self.vm_writer.write_goto(close_label)
        self.vm_writer.write_label(else_label)

        #if there is an else block:
        self.tokenizer.advance()
        if self.tokenizer.token_type() == "KEYWORD" and self.tokenizer.keyword().lower() == "else":
            #{:
            self.tokenizer.advance()
            #else body:
            self.tokenizer.advance()
            self.compile_statements() 

            self.tokenizer.advance()
        self.vm_writer.write_label(close_label)

    def compile_expression(self) -> None:
        """Compiles an expression."""

        operators = {"+": "ADD", "-": "SUB", "*": "MULT", "/": "DIVIDE", "&": "AND", "|": "OR", "<": "LT", ">": "GT", "=": "EQ"}

        #the first term:
        self.compile_term()

        while self.tokenizer.has_more_tokens():
            if self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() in operators:
                operator = self.tokenizer.symbol()
                self.tokenizer.advance()
                self.compile_term()
                if operator in ["/", "*"]:
                    if operator == "*":
                        self.vm_writer.write_call("Math.multiply", 2)
                    else:
                        self.vm_writer.write_call("Math.divide", 2)
                else:
                    self.vm_writer.write_arithmetic(operators[operator])
            else:
                break

    def compile_term(self) -> None:
        keyword_constant = {"true", "false", "null", "this"}
        unary_op = {"-", "~","^","#"}

        if self.tokenizer.token_type() == "INT_CONST":
            self.vm_writer.write_push("CONST", self.tokenizer.int_val())
            self.tokenizer.advance()

        elif self.tokenizer.token_type() == "STRING_CONST":
            self.vm_writer.write_push("CONST", len(self.tokenizer.string_val()))
            self.vm_writer.write_call("String.new", 1)
            for char in self.tokenizer.string_val():
                self.vm_writer.write_push("CONST", ord(char))
                self.vm_writer.write_call("String.appendChar", 2)

            self.tokenizer.advance()

        elif self.tokenizer.token_type() == "KEYWORD" and self.tokenizer.keyword().lower() in keyword_constant:
            if self.tokenizer.keyword().lower() == "true":
                self.vm_writer.write_push("CONST", 0)
                self.vm_writer.write_arithmetic("NOT")
            elif self.tokenizer.keyword().lower() == "false":
                self.vm_writer.write_push("CONST", 0)
            elif self.tokenizer.keyword().lower() == "null":
                self.vm_writer.write_push("CONST", 0)
            elif self.tokenizer.keyword().lower() == "this":
                self.vm_writer.write_push("POINTER", 0)

            self.tokenizer.advance()

        elif self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() in unary_op:
            operator = self.tokenizer.symbol()
            self.tokenizer.advance()
            self.compile_term()
            if operator == "-":
                self.vm_writer.write_arithmetic("NEG")
            elif operator == "~":
                self.vm_writer.write_arithmetic("NOT")
            elif operator == "^":
                self.vm_writer.write_arithmetic("SHIFTLEFT")
            elif operator == "#":
                self.vm_writer.write_arithmetic("SHIFTRIGHT")    

        elif self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == "(":
            self.tokenizer.advance()
            self.compile_expression()
            self.tokenizer.advance()  

        else:  
            identifier = self.tokenizer.identifier()
            self.tokenizer.advance()

            if self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == "[":
                self.vm_writer.write_push(self.kind_to_segment(self.symbol_table.kind_of(identifier)),
                                           self.symbol_table.index_of(identifier))
                self.tokenizer.advance()
                self.compile_expression()
                self.vm_writer.write_arithmetic("ADD")
                self.vm_writer.write_pop("POINTER", 1)
                self.vm_writer.write_push("THAT", 0)

                self.tokenizer.advance()  

            elif self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() in ["(", "."]:
                self.compile_function_call(identifier)
            else:
                self.vm_writer.write_push(self.kind_to_segment(self.symbol_table.kind_of(identifier)),
                                           self.symbol_table.index_of(identifier))

    def compile_expression_list(self) -> int:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        expressions_number = 0

        #if empty:
        if self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == ")":
            return expressions_number

        #first expression:
        expressions_number += 1
        self.compile_expression()

        #any additional:
        while self.tokenizer.has_more_tokens():
            if self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == ",":
                self.tokenizer.advance()
                expressions_number += 1
                self.compile_expression()
            else:
                break
        return expressions_number
    
    def get_type(self) -> str:
        if self.tokenizer.token_type() == "KEYWORD":
            return self.tokenizer.keyword().lower()

        return self.tokenizer.identifier()
    
