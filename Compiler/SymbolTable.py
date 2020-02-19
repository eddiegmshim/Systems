#Start with project 10, and extend the syntax analyzer such that whenever
#an identifier is encountered, output name, category (var, argument, static, field, class, subroutine)
#if the category is var, argument, static, or field, get the running index
#check whether an identifier is being defined or being used 
class SymbolTable:
    static_scope = {}
    frequency_table = {"STATIC":0, "FIELD":0, "ARG":0,"VAR":0}

    def __init__(self):
        self.frequency_table["FIELD"] = 0
        self.subroutine_scope = {}
        self.field_scope = {}
    
    def print(self):
        print("frequency table:", self.frequency_table)
        print("subroutine_scope:", self.subroutine_scope)
        
    def get_kind(self, name):
        if name in self.subroutine_scope.keys(): return self.subroutine_scope[name][1]
        elif name in self.field_scope.keys(): return self.field_scope[name][1]
        elif name in self.static_scope.keys(): return self.static_scope[name][1]
        else: return "NONE"

    def get_type(self, name):
        if name in self.subroutine_scope.keys(): return self.subroutine_scope[name][0]
        elif name in self.field_scope.keys(): return self.field_scope[name][0]
        elif name in self.static_scope.keys(): return self.static_scope[name][0]
        else: return "NONE"

    def get_index(self, name):
        if name in self.subroutine_scope.keys(): return self.subroutine_scope[name][2]
        elif name in self.field_scope.keys(): return self.field_scope[name][2]
        elif name in self.static_scope.keys(): return self.static_scope[name][2]
        else: return"NONE"        

    def start_subroutine(self):
        self.subroutine_scope = {} 
        self.frequency_table["ARG"] = 0
        self.frequency_table["VAR"] = 0

    def populate_table(self, name, type, kind):
#        print("before update:", name, "|", type, "|", kind)
#        self.print()
        if kind == "ARG":
            number = self.frequency_table["ARG"]
            self.frequency_table["ARG"] += 1
            self.subroutine_scope[name] = (type, kind, number)
        elif kind == "VAR":
            number = self.frequency_table["VAR"]
            self.frequency_table["VAR"] += 1
            self.subroutine_scope[name] = (type, kind, number)           
        elif kind == "STATIC":
            number = self.frequency_table["STATIC"]
            self.frequency_table["STATIC"] += 1
            self.static_scope[name] = (type, kind, number)
        elif kind == "FIELD":
            number = self.frequency_table["FIELD"]
            self.frequency_table["FIELD"] += 1
            self.field_scope[name] = (type, kind, number)
#        print("after update:")
#        self.print()

    def get_symboltable_count(self, kind):
        return self.frequency_table[kind]

