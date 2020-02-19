from SymbolTable import SymbolTable
from VMWriter import VMWriter

class CompilationUnit_P2:
    
    def check_subroutine_call(self):
        tolken = self.get_tolken()
        subroutine_call = self.check_next_tolken() in [".", "("]
        self.reverse_tolken(tolken)
        return subroutine_call

    def check_array(self):
        tolken = self.get_tolken()
        array = self.check_next_tolken() == "["
        self.reverse_tolken(tolken)
        return array

    def check_classVarDec(self):
        #static|field
        p = self.check_next_tolken()
        if(p == "static" or p == "field"): return True
        return False        
        
    def check_subroutineDec(self):
        #constructor|function|method
        p = self.check_next_tolken()
        if(p == "constructor" or p == "function" or p == "method"): return True
        return False
        
    def check_statement(self):
        #let|if|while|do|return
        p = self.check_next_tolken()
        if(p == "let" 
           or p == "if" 
           or p == "while" 
           or p == "do" 
           or p == "return"): return True
        return False
        

    def check_op(self):
        #+-*/&|<>=
        p = self.check_next_tolken()
        if(p in ["+", 
                 "-", 
                 "*", 
                 "/", 
                 "&", 
                 "|", 
                 "<", 
                 ">", 
                 "="]): return True
        return False       

  
    def check_unary_op(self):
        #~-
        p = self.check_next_tolken()
        if(p == "~" or p== "-"): return True
        return False
  
    def check_next_tolken(self):
        return self.check_next_tolken_info()[0]

    def check_next_tolken_type(self):
        return self.check_next_tolken_info()[1]

    def check_next_tolken_info(self):
        tolken_info = self.get_tolken_info()
        self.reverse_tolken_info(tolken_info)
        return tolken_info

    def get_tolken(self):
#        print("test self get tolken info:" ,self.get_tolken_info())
        tolken_info = self.get_tolken_info()[0]
#        print("testing tolken_info", tolken_info)
        return tolken_info

    def get_tolken_info(self):
        if self.buffer:
#            return ["buffer", "buffer"]
#            print("testing buffer:", self.buffer)
            return self.buffer.pop(0)
        else:
            return self.get_next_tolken()

    def reverse_tolken(self, tolken):
        self.reverse_tolken_info((tolken, "UNKNOWN"))

    def reverse_tolken_info(self, tolken):
#        print("inserting buffer:", tolken)
        self.buffer.insert(0, tolken)
#
    def get_next_tolken(self):                   
        
        keyword = self.tolkenizer[self.tolken_count][0]
        tolken_type = self.tolkenizer[self.tolken_count][1]
#        print(self.tolken_count, "\t|", keyword, "\t|", tolken_type)
        self.tolken_count += 1  
        
        return(keyword, tolken_type)
        
    dict_kind = {
            "ARG": "ARG",
            "STATIC": "STATIC",
            "VAR": "LOCAL",
            "FIELD": "THIS"
            }

    dict_arithmetic = {
            "+": "ADD",
            "-": "SUB",
            "=": "EQ",
            ">": "GT",
            "<": "LT",
            "&": "AND",
            "|": "OR"
            }

    dict_unary = {
            "-": "NEG",
            "~": "NOT"
            }

    index_tag = -1
    while_tag = -1

    def __init__(self, vm_writer, tolkens):
        self.vm_writer = vm_writer
        self.tolkenizer = tolkens
        self.tolken_count = 0
        self.symbol_table = SymbolTable()
        self.buffer = []
        
        self.process()

    def process(self):
        #class, className, "{"
        self.get_tolken() 
        self.class_name = self.get_tolken() 
        self.get_tolken() 
        
        while self.check_classVarDec():
            self.process_classVarDec() 
        while self.check_subroutineDec():
            self.process_subroutine() 
        self.vm_writer.close()

    def process_classVarDec(self):
        #static or field
        #type
        #varName
        kind = self.get_tolken() 
        type = self.get_tolken() 
        name = self.get_tolken() 

        self.symbol_table.populate_table(name, type, kind.upper())        
        while self.check_next_tolken() != ";": 
            #continue until you hit end of ("," varName)
            self.get_tolken() 
            name = self.get_tolken() 
            self.symbol_table.populate_table(name, type, kind.upper())

        #";"
        self.get_tolken() 

    def process_subroutine(self):
        #constructor or function or method
        #void or type
        #subroutineName
        subroutine_kind = self.get_tolken() 
        self.get_tolken()
        subroutine_name = self.get_tolken()  
        self.symbol_table.start_subroutine()

        if subroutine_kind == "method": self.symbol_table.populate_table("instance", self.class_name, "ARG")

        #(parameterList){
        self.get_tolken() 
        self.process_parameterList()
        self.get_tolken() 
        self.get_tolken() 

        while "var" == self.check_next_tolken():
            #varDec*
            self.process_varDec() 
            
        function_name = self.class_name + "." + subroutine_name
        num_locals = self.symbol_table.get_symboltable_count("VAR")
        self.vm_writer.vm_write_function(function_name, num_locals)

        if subroutine_kind == "constructor":
            #get k number of fields, push constant, allocate memory
            #then pop into THIS
            num_fields = self.symbol_table.get_symboltable_count("FIELD")
            self.vm_writer.vm_write_push("CONST", num_fields)
            self.vm_writer.vm_write_call("Memory.alloc", 1)
            self.vm_writer.vm_write_pop("POINTER", 0)
        elif subroutine_kind == "method":
            #this is argument 0 in every method
            #pop into location THIS
            self.vm_writer.vm_write_push("ARG", 0)
            self.vm_writer.vm_write_pop("POINTER", 0)

        self.process_statements() # statements
        self.get_tolken() # "}"

  
    def process_parameterList(self):
        if ")" != self.check_next_tolken():    
            #type
            #varName
            type = self.get_tolken() 
            name = self.get_tolken() 
            self.symbol_table.populate_table(name, type, "ARG")

        while ")" != self.check_next_tolken():
            self.get_tolken() 
            #type
            #varName
            type = self.get_tolken() 
            name = self.get_tolken() 
            self.symbol_table.populate_table(name, type, "ARG")

    def process_varDec(self):        
        #var
        #type
        #varName
        self.get_tolken() 
        type = self.get_tolken() 
        name = self.get_tolken() 

        self.symbol_table.populate_table(name, type, "VAR")

        while self.check_next_tolken() != ";":             
            #";"
            #varName
            self.get_tolken() 
            name = self.get_tolken() 
            self.symbol_table.populate_table(name, type, "VAR")

        self.get_tolken() # ";"

    def process_statements(self):
        while self.check_statement():
            tolken = self.get_tolken()
#            print("TESTING tolken", tolken)

            if "let" == tolken: self.process_let()
            elif "if" == tolken: self.process_if()
            elif "while" == tolken: self.process_while()
            elif "do" == tolken: self.process_do()
            elif "return" == tolken: self.process_return()

    def process_do(self):
        self.process_subroutine_call()
        self.vm_writer.vm_write_pop("TEMP", 0)
        self.get_tolken() # ";"

    def process_let(self):
        var_name = self.get_tolken() 
        var_kind  = self.dict_kind[self.symbol_table.get_kind(var_name)]
        var_index = self.symbol_table.get_index(var_name)

        if "[" == self.check_next_tolken(): 
            #checking inside array
            self.get_tolken() 
            self.process_expression() 
            self.get_tolken() 
            self.vm_writer.vm_write_push(var_kind, var_index)
            #translate to vm
            self.vm_writer.vm_write_arithmetic("ADD")
            self.vm_writer.vm_write_pop("TEMP", 0)            
            #get expression
            self.get_tolken() 
            self.process_expression()
            self.get_tolken() 
            
            self.vm_writer.vm_write_push("TEMP", 0)
            self.vm_writer.vm_write_pop("POINTER", 1)
            self.vm_writer.vm_write_pop("THAT", 0)
        else: 
            self.get_tolken() 
            self.process_expression() 
            self.get_tolken() 
            self.vm_writer.vm_write_pop(var_kind, var_index)


    def process_while(self):
        self.while_tag += 1
        while_tag = self.while_tag
        self.vm_writer.vm_write_label("WHILE" + str(while_tag) + "\n")    

        #(expression)
        self.get_tolken() 
        self.process_expression() 
        self.vm_writer.vm_write_arithmetic("NOT") 
        self.get_tolken() 
        self.get_tolken() 
        self.vm_writer.vm_write_if("WHILE_END" + str(while_tag) +"\n")
        
        #statements        
        self.process_statements() 
        self.vm_writer.vm_write_goto("WHILE" + str(while_tag) + "\n")
        self.vm_writer.vm_write_label("WHILE_END" + str(while_tag) + "\n")
        self.get_tolken()


    def process_return(self):
        if self.check_next_tolken() != ";":
            self.process_expression()
        else:
            self.vm_writer.vm_write_push("CONST", 0)

        self.vm_writer.vm_write_return()
        self.get_tolken()

    def process_if(self):
        self.index_tag += 1
        index_tag = self.index_tag

        #(expression)
        self.get_tolken()
        self.process_expression()
        self.get_tolken()        
        self.get_tolken() 

        self.vm_writer.vm_write_if("IF_TRUE" + str(index_tag) + "\n")
        self.vm_writer.vm_write_goto("IF_FALSE" + str(index_tag) + "\n")
        self.vm_writer.vm_write_label("IF_TRUE" + str(index_tag) + "\n")
        
        self.process_statements() # statements      
        self.vm_writer.vm_write_goto("IF_END" + str(index_tag) + "\n")
        self.get_tolken() 
        self.vm_writer.vm_write_label("IF_FALSE" + str(index_tag) + "\n")
        
        #(else {statements})?
        if self.check_next_tolken() == "else": 
            self.get_tolken() 
            self.get_tolken() 
            self.process_statements() 
            self.get_tolken() 
        self.vm_writer.vm_write_label("IF_END" + str(index_tag) + "\n")

    def process_expression(self):
        self.process_term() 

        #(op term)*
        while self.check_op(): 
            op = self.get_tolken() 
            self.process_term() 
            if op in self.dict_arithmetic.keys():
                self.vm_writer.vm_write_arithmetic(self.dict_arithmetic[op])
            elif op == "*":
                self.vm_writer.vm_write_call("Math.multiply", 2)
            elif op == "/":
                self.vm_writer.vm_write_call("Math.divide", 2)

    def process_term(self):
        if self.check_unary_op():
            #unaryOP
            #term
            unary_op = self.get_tolken()
            self.process_term()
            self.vm_writer.vm_write_arithmetic(self.dict_unary[unary_op])
            
            #check for (expression)
        elif "(" == self.check_next_tolken():
            self.get_tolken()
            self.process_expression() 
            self.get_tolken()
        elif self.check_next_tolken_type() == "INT_CONST":
            self.vm_writer.vm_write_push("CONST", self.get_tolken())
        elif self.check_next_tolken_type() == "STRING_CONST": 
            self.process_string()
        elif self.check_next_tolken_type() == "KEYWORD": 
            self.process_keyword()
        
        #we know it's a var/subroutine
        else: 
            if self.check_array():
                array_var = self.get_tolken() 
                
                #[expression]
                self.get_tolken()
                self.process_expression()
                self.get_tolken()
                array_kind = self.symbol_table.get_kind(array_var)
                array_index = self.symbol_table.get_index(array_var)
                self.vm_writer.vm_write_push(self.dict_kind[array_kind], array_index)

                self.vm_writer.vm_write_arithmetic("ADD")
                self.vm_writer.vm_write_pop("POINTER", 1)
                self.vm_writer.vm_write_push("THAT", 0)
            elif self.check_subroutine_call():
                self.process_subroutine_call()
            else:
                var = self.get_tolken()
#                print("TESTING-----------", var)
                var_kind = self.dict_kind[self.symbol_table.get_kind(var)]
                var_index = self.symbol_table.get_index(var)
                self.vm_writer.vm_write_push(var_kind, var_index)

    def process_keyword(self):
        keyword = self.get_tolken()
        if keyword == "this":
            self.vm_writer.vm_write_push("POINTER", 0)
        else:
            self.vm_writer.vm_write_push("CONST", 0)
            if keyword == "true":
                self.vm_writer.vm_write_arithmetic("NOT")

    def process_expressionList(self):
        number_args = 0
        if ")" != self.check_next_tolken():
            number_args += 1
            self.process_expression()

        while ")" != self.check_next_tolken():
            number_args += 1
            self.get_tolken() # ","
            self.process_expression()

        return number_args




    def process_subroutine_call(self):
        #subroutineName or className or varName
        identifier = self.get_tolken() 
        function_name = identifier
        number_args = 0

        if "." == self.check_next_tolken():
            self.get_tolken()
            subroutine_name = self.get_tolken()
            type = self.symbol_table.get_type(identifier)

            if type != "NONE":
                instance_kind = self.symbol_table.get_kind(identifier)
                instance_index = self.symbol_table.get_index(identifier)   
                self.vm_writer.vm_write_push(self.dict_kind[instance_kind], instance_index)
                function_name = type + "." + subroutine_name
                number_args += 1
            
            #class
            else: 
                class_name = identifier
                function_name = class_name + "." + subroutine_name
        elif "(" == self.check_next_tolken():
            subroutine_name = identifier
            function_name = self.class_name + "." + subroutine_name
            number_args += 1
            self.vm_writer.vm_write_push("POINTER", 0)

        #(expressionList)
        self.get_tolken()
        number_args += self.process_expressionList()
        self.get_tolken()
        self.vm_writer.vm_write_call(function_name, number_args)

    def process_string(self):
        string = self.get_tolken()
        self.vm_writer.vm_write_push("CONST", len(string))
        self.vm_writer.vm_write_call("String.new", 1)
        for char in string:
            self.vm_writer.vm_write_push("CONST", ord(char))
            self.vm_writer.vm_write_call("String.appendChar", 2)

   
    