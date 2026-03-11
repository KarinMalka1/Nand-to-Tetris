"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
from JackTokenizer import JackTokenizer


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    def __init__(self, input_stream: "JackTokenizer", output_stream) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        self.output = output_stream
        self.tokenizer = input_stream
        self.indentation_level = 0


    def compile_class(self) -> None:
        """Compiles a complete class."""
        static_field = {"static", "field"}
        subroutine_declaration = {"constructor", "function", "method"}
        self.tokenizer.advance()
        #class:
        self.open_indentation("class")
        self.write_token(self.tokenizer.keyword().lower(), self.tokenizer.token_type().lower())
        self.tokenizer.advance()

        #class name:
        self.write_token(self.tokenizer.identifier(), self.tokenizer.token_type().lower())
        self.tokenizer.advance()
        
        # {:
        self.write_token(self.tokenizer.symbol(), self.tokenizer.token_type().lower())

        while self.tokenizer.has_more_tokens():
            self.tokenizer.advance()
            if self.tokenizer.token_type() == "KEYWORD" and self.tokenizer.keyword().lower() in static_field:
                self.compile_class_var_dec()
            else:
                break

        while self.tokenizer.has_more_tokens():
            if self.tokenizer.token_type() == "KEYWORD" and self.tokenizer.keyword().lower() in subroutine_declaration:
                self.compile_subroutine()
                self.tokenizer.advance()
            else:
                break

        #'}':
        self.write_token("}", self.tokenizer.token_type().lower())

        self.close_indentation("class")


    def compile_class_var_dec(self) -> None:
        """
        Compiles a static or field variable declaration.
        Grammar: ('static' | 'field') type varName (',' varName)* ';'
        """
        self.open_indentation("classVarDec")
        #field or static:
        self.write_token(self.tokenizer.keyword().lower(), self.tokenizer.token_type().lower())

        #type of the variable:
        self.tokenizer.advance()
        if self.tokenizer.token_type() == "KEYWORD":
            self.write_token(self.tokenizer.keyword().lower(), self.tokenizer.token_type().lower())
        else:
            self.write_token(self.tokenizer.identifier(), self.tokenizer.token_type().lower())

        #var name:
        self.tokenizer.advance()
        self.write_token(self.tokenizer.identifier(), self.tokenizer.token_type().lower())

        #any additional vars in the same line:
        while self.tokenizer.has_more_tokens():
            self.tokenizer.advance()
            if self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == ",":
                self.write_token(",", self.tokenizer.token_type().lower())
                self.tokenizer.advance()
                self.write_token(self.tokenizer.identifier(), self.tokenizer.token_type().lower())
            else:
                break

        # ";":
        self.write_token(";", self.tokenizer.token_type().lower())
        self.close_indentation("classVarDec")


    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        self.open_indentation("subroutineDec")
        self.write_token(self.tokenizer.keyword().lower(), self.tokenizer.token_type().lower())
        #void or type:
        self.tokenizer.advance()
        if self.tokenizer.token_type() == "KEYWORD":
            self.write_token(self.tokenizer.keyword().lower(), self.tokenizer.token_type().lower())
        else:
            self.write_token(self.tokenizer.identifier(), self.tokenizer.token_type().lower())
        
        #subroutine name:
        self.tokenizer.advance()
        self.write_token(self.tokenizer.identifier(), self.tokenizer.token_type().lower())

        # (:
        self.tokenizer.advance()
        self.write_token(self.tokenizer.symbol(), self.tokenizer.token_type().lower())

        #parameter list: 
        self.tokenizer.advance()
        self.compile_parameter_list()

        # ):
        self.write_token(self.tokenizer.symbol(), self.tokenizer.token_type().lower())

        #the subroutine body:
        self.tokenizer.advance()
        self.subroutine_body()

        self.close_indentation("subroutineDec")

    def subroutine_body(self) -> None:
        self.open_indentation("subroutineBody")
        #{:
        self.write_token(self.tokenizer.symbol(), self.tokenizer.token_type().lower())
        #var declarations: 
        while self.tokenizer.has_more_tokens():
            self.tokenizer.advance()
            if self.tokenizer.token_type() == "KEYWORD" and self.tokenizer.keyword().lower() == "var":
                self.compile_var_dec()
            else:
                break
        #statements:
        self.compile_statements()
        #}:
        self.write_token(self.tokenizer.symbol(), self.tokenizer.token_type().lower())

        self.close_indentation("subroutineBody")
    
    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        self.open_indentation("parameterList")

        #if empty:
        if self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == ")":
            self.close_indentation("parameterList")
            return
        #param type of the first param:
        if self.tokenizer.token_type() == "KEYWORD":
            self.write_token(self.tokenizer.keyword().lower(), self.tokenizer.token_type().lower())
        else:
            self.write_token(self.tokenizer.identifier(), self.tokenizer.token_type().lower())
        #first param name: 
        self.tokenizer.advance()
        self.write_token(self.tokenizer.identifier(), self.tokenizer.token_type().lower())

        while self.tokenizer.has_more_tokens():
            self.tokenizer.advance()
            if self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == ",":
                self.write_token(self.tokenizer.symbol(), self.tokenizer.token_type().lower())
                self.tokenizer.advance()
                if self.tokenizer.token_type() == "KEYWORD":
                    self.write_token(self.tokenizer.keyword().lower(), self.tokenizer.token_type().lower())
                else:
                    self.write_token(self.tokenizer.identifier(), self.tokenizer.token_type().lower())
                self.tokenizer.advance()
                self.write_token(self.tokenizer.identifier(), self.tokenizer.token_type().lower())
            else:
                break

        self.close_indentation("parameterList")
        

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""

        self.open_indentation("varDec")

        #var:
        self.write_token(self.tokenizer.keyword().lower(), self.tokenizer.token_type().lower())

        #var type:
        self.tokenizer.advance()
        if self.tokenizer.token_type() == "KEYWORD":
            self.write_token(self.tokenizer.keyword().lower(), self.tokenizer.token_type().lower())
        else:
            self.write_token(self.tokenizer.identifier(), self.tokenizer.token_type().lower())

        #var name:
        self.tokenizer.advance()
        self.write_token(self.tokenizer.identifier(), self.tokenizer.token_type().lower())

        #any additional variables in the same line:
        while self.tokenizer.has_more_tokens():
            self.tokenizer.advance()
            if self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == ",":
                self.write_token(self.tokenizer.symbol(), self.tokenizer.token_type().lower())
                self.tokenizer.advance()
                self.write_token(self.tokenizer.identifier(), self.tokenizer.token_type().lower())
            else:
                break

        #;:
        self.write_token(self.tokenizer.symbol(), self.tokenizer.token_type().lower())

        self.close_indentation("varDec")

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """

        self.open_indentation("statements")

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

        self.close_indentation("statements")

    def compile_do(self) -> None:
        """Compiles a do statement."""

        self.open_indentation("doStatement")

        #do:
        self.write_token(self.tokenizer.keyword().lower(), self.tokenizer.token_type().lower())

        #function name, or class name, or var name:
        self.tokenizer.advance()
        self.write_token(self.tokenizer.identifier(), self.tokenizer.token_type().lower())

        #if the function is working on a class or var:
        self.tokenizer.advance()
        if self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == ".":
            self.write_token(self.tokenizer.symbol(), self.tokenizer.token_type().lower())
            self.tokenizer.advance()
            self.write_token(self.tokenizer.identifier(), self.tokenizer.token_type().lower())
            self.tokenizer.advance() 
        
        #(:
        self.write_token(self.tokenizer.symbol(), self.tokenizer.token_type().lower())

        #params:
        self.tokenizer.advance()
        self.compile_expression_list()

        #):
        self.write_token(self.tokenizer.symbol(), self.tokenizer.token_type().lower())

        #;:
        self.tokenizer.advance()
        self.write_token(self.tokenizer.symbol(), self.tokenizer.token_type().lower())

        self.tokenizer.advance() 

        self.close_indentation("doStatement")

    def compile_let(self) -> None:
        """Compiles a let statement."""

        self.open_indentation("letStatement")

        #let:
        self.write_token(self.tokenizer.keyword().lower(), self.tokenizer.token_type().lower())

        #var name:
        self.tokenizer.advance()
        self.write_token(self.tokenizer.identifier(), self.tokenizer.token_type().lower())

        #if it is an array:
        self.tokenizer.advance()
        if self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == "[":
            self.write_token(self.tokenizer.symbol(), self.tokenizer.token_type().lower())
            self.tokenizer.advance()
            self.compile_expression()
            self.write_token(self.tokenizer.symbol(), self.tokenizer.token_type().lower())
            self.tokenizer.advance()

        #=:
        self.write_token(self.tokenizer.symbol(), self.tokenizer.token_type().lower())

        self.tokenizer.advance()
        self.compile_expression()

        #;:
        self.write_token(self.tokenizer.symbol(), self.tokenizer.token_type().lower())

        self.tokenizer.advance()           

        self.close_indentation("letStatement")

    def compile_while(self) -> None:
        """Compiles a while statement."""

        self.open_indentation("whileStatement")

        #while:
        self.write_token(self.tokenizer.keyword().lower(), self.tokenizer.token_type().lower())

        #(:
        self.tokenizer.advance()
        self.write_token(self.tokenizer.symbol(), self.tokenizer.token_type().lower())

        self.tokenizer.advance()
        self.compile_expression()


        #):
        self.write_token(self.tokenizer.symbol(), self.tokenizer.token_type().lower())

        #{:
        self.tokenizer.advance()
        self.write_token(self.tokenizer.symbol(), self.tokenizer.token_type().lower())

        self.tokenizer.advance()
        self.compile_statements()

        #}:
        self.write_token(self.tokenizer.symbol(), self.tokenizer.token_type().lower())

        self.tokenizer.advance() 

        self.close_indentation("whileStatement")

    def compile_return(self) -> None:
        """Compiles a return statement."""

        self.open_indentation("returnStatement")

        #return:
        self.write_token(self.tokenizer.keyword().lower(), self.tokenizer.token_type().lower())

        #expression after return:
        self.tokenizer.advance()
        if self.tokenizer.token_type() != "SYMBOL" or self.tokenizer.symbol() != ";":
            self.compile_expression()

        #;:
        self.write_token(self.tokenizer.symbol(), self.tokenizer.token_type().lower())

        self.tokenizer.advance() 

        self.close_indentation("returnStatement")

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""

        self.open_indentation("ifStatement")

        #if:
        self.write_token(self.tokenizer.keyword().lower(), self.tokenizer.token_type().lower())

        #(:
        self.tokenizer.advance()
        self.write_token(self.tokenizer.symbol(), self.tokenizer.token_type().lower())

        self.tokenizer.advance()
        self.compile_expression()

        #):
        self.write_token(self.tokenizer.symbol(), self.tokenizer.token_type().lower())

        #{:
        self.tokenizer.advance()
        self.write_token(self.tokenizer.symbol(), self.tokenizer.token_type().lower())

        self.tokenizer.advance()
        self.compile_statements()

        #}:
        self.write_token(self.tokenizer.symbol(), self.tokenizer.token_type().lower())

        #if there is an else block:
        self.tokenizer.advance()
        if self.tokenizer.token_type() == "KEYWORD" and self.tokenizer.keyword().lower() == "else":
            self.write_token(self.tokenizer.keyword().lower(), self.tokenizer.token_type().lower())
            self.tokenizer.advance()
            self.write_token(self.tokenizer.symbol(), self.tokenizer.token_type().lower())
            self.tokenizer.advance()
            self.compile_statements() 
            self.write_token(self.tokenizer.symbol(), self.tokenizer.token_type().lower())
            self.tokenizer.advance()

        self.close_indentation("ifStatement")

    def compile_expression(self) -> None:
        """Compiles an expression."""

        operators = {"+", "-", "*", "/", "&", "|", "<", ">", "="}
        self.open_indentation("expression")

        #the first term:
        self.compile_term()

        while self.tokenizer.has_more_tokens():
            if self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() in operators:
                self.write_token(self.tokenizer.symbol(), self.tokenizer.token_type().lower())
                self.tokenizer.advance()
                self.compile_term()
            else:
                break

        self.close_indentation("expression")

    def compile_term(self) -> None:
        """Compiles a term. 
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """
        keyword_constant = {"true", "false", "null", "this"}
        unary_op = {"-", "~","^","#"}
        self.open_indentation("term")

        if self.tokenizer.token_type() == "INT_CONST":
            self.write_token(str(self.tokenizer.int_val()), "integerConstant")
            self.tokenizer.advance()

        elif self.tokenizer.token_type() == "STRING_CONST":
            self.write_token(self.tokenizer.string_val(), "stringConstant")
            self.tokenizer.advance()

        elif self.tokenizer.token_type() == "KEYWORD" and self.tokenizer.keyword().lower() in keyword_constant:
            self.write_token(self.tokenizer.keyword().lower(), self.tokenizer.token_type().lower())
            self.tokenizer.advance()

        elif self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() in unary_op:
            self.write_token(self.tokenizer.symbol(), self.tokenizer.token_type().lower())
            self.tokenizer.advance()
            self.compile_term()

        elif self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == "(":
            self.write_token(self.tokenizer.symbol(), self.tokenizer.token_type().lower())
            self.tokenizer.advance()
            self.compile_expression()
            self.write_token(self.tokenizer.symbol(), self.tokenizer.token_type().lower())
            self.tokenizer.advance()

        else:  
            self.write_token(self.tokenizer.identifier(), self.tokenizer.token_type().lower())
            self.tokenizer.advance()
            #checks for array:
            if self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == "[":
                self.write_token(self.tokenizer.symbol(), self.tokenizer.token_type().lower())
                self.tokenizer.advance()
                self.compile_expression()
                self.write_token(self.tokenizer.symbol(), self.tokenizer.token_type().lower())
                self.tokenizer.advance()
            #checks for function call:
            elif self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() in ["(", "."]:
                if self.tokenizer.symbol() == ".":
                    self.write_token(self.tokenizer.symbol(), self.tokenizer.token_type().lower())
                    self.tokenizer.advance()
                    self.write_token(self.tokenizer.identifier(), self.tokenizer.token_type().lower())       
                    self.tokenizer.advance()                                                             
                self.write_token(self.tokenizer.symbol(), self.tokenizer.token_type().lower())
                self.tokenizer.advance()
                self.compile_expression_list()
                self.write_token(self.tokenizer.symbol(), self.tokenizer.token_type().lower())
                self.tokenizer.advance()

        self.close_indentation("term")

    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""

        self.open_indentation("expressionList")

        #if empty:
        if self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == ")":
            self.close_indentation("expressionList")
            return

        #first expression:
        self.compile_expression()

        #any additional:
        while self.tokenizer.has_more_tokens():
            if self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == ",":
                self.write_token(self.tokenizer.symbol(), self.tokenizer.token_type().lower())
                self.tokenizer.advance()
                self.compile_expression()
            else:
                break

        self.close_indentation("expressionList")

    def write_token(self, name: str, type: str) -> None:
        name = name.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "")   
        self.output.write("\t" * self.indentation_level + "<" + type + "> " + name + " </" + type + ">" + "\n")


    def open_indentation(self, name: str) -> None:
        self.output.write("\t" * self.indentation_level + "<" + name + ">" + "\n")
        self.indentation_level += 1

    def close_indentation(self, name: str) -> None:
        self.indentation_level -= 1  
        self.output.write("\t" * self.indentation_level + "</" + name + ">" + "\n") 
