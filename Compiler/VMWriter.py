class VMWriter:
    def __init__(self, output_file):
        self.output = open(output_file, "w")
        
    def close(self):
        self.output.close()

    def write(self, input_write):
        self.output.write(input_write)        

    def vm_write_push(self, segment, index):
        if segment == "CONST": segment = "constant"
        elif segment == "ARG": segment = "argument"
        self.output.write("push " + segment.lower() + " " + str(index) + "\n")

    def vm_write_pop(self, segment, index):
        if segment == "CONST": segment = "constant"
        elif segment == "ARG": segment = "argument"
        self.output.write("pop " + segment.lower() + " " + str(index) + "\n")

    def vm_write_arithmetic(self, command):
        self.output.write(command.lower() + "\n")

    def vm_write_label(self, label):
        self.output.write("label " + label)

    def vm_write_goto(self, input_goto):
        self.output.write("goto " + input_goto)

    def vm_write_if(self, input_ifgoto):
        self.output.write("if-goto " + input_ifgoto)

    def vm_write_call(self, name, num_args):
        self.output.write("call " + name + " " + str(num_args) + "\n")

    def vm_write_function(self, name, num_locals):
        self.output.write("function " + name + " " + str(num_locals) + "\n")

    def vm_write_return(self):
        self.output.write("return\n")

