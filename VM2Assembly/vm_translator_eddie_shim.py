#Project 8 VM Translator pt2
#Eddie Shim
#Due 11/13/19
import sys
import os


#constructor: opens the output file/stream and gets ready to write into it
def main():
#    file_path1 = sys.argv[1]    
#    file_path1 = "C:/Users/eddie/Documents/MSCS/Intro to Computer Systems/shimEddieProject8/StaticsTest/"
#    file_path1 = "C:/Users/eddie/Documents/MSCS/Intro to Computer Systems/shimEddieProject8/FunctionCalls/FibonacciElement/"
    file_path1 = "C:/Users/eddie/Documents/MSCS/Intro to Computer Systems/shimEddieProject8/FunctionCalls/StaticsTest/"
    
    vm_files = []    
    for files_in in os.listdir(file_path1):
        if(".vm" in files_in):            
            vm_files.append(files_in)
    
    file_name = file_path1.split("/")[-2] + ".vm"
    print(file_name)
    
    text, output = "", ""
    text_all = ""
    
    if("Sys.vm" in vm_files):
        output = initialize()
        for vm_path in vm_files:
            text = stringParser(file_path1 + vm_path)
            text_all += text
            output += vm2assembly(text,vm_path)    
    else:
        text = stringParser(file_path1 + vm_files[0])
        output += vm2assembly(text,file_name.replace(".vm",""))    
    print(vm_files)
    
    output += ("(_1)\n"      #add infinite loop at end
               "@_1\n"
               "0;JMP")

    
    writeFile = open(file_path1 + "combined.txt", "w")
    writeFile.write(output)
    writeFile.close()
        
    filePathOut = file_path1 + file_name.replace(".vm",".asm")
    print("Writing translated file into:", filePathOut)
    writeFile = open(filePathOut, "w")
    writeFile.write(output)
    writeFile.close()      
    
def initialize():
    init =("@256\n" 
          "D=A\n" 
          "@SP\n" 
          "M=D\n" +
          translate_call("Sys.init0", 0) + #+
          "//initialization\n\n")    
    return(init)
    
def vm2assembly(input, file_name):   
    command_dict = create_command_dict()
    var_counter = 0
    output = ""
    
    for command in input.split("\n"):    
        
        if len(command) == 0:
           output += "" 
        
        #these commands are just hard coded lookups
        elif(command in command_dict):
            output += command_dict[command]
            
        #these commands require dynamic variables to ensure uniqueness of variables
        elif(command in ("gt", "lt", "eq")):
            var_counter += 1
            output += dynamic_command(command,var_counter)
            
        #push/pop commands with segment index
        elif("push" in command or "pop" in command):
            var_counter += 1
            output += translate_push_or_pop(command, file_name)
        
        elif("label" in command):
            output += translate_label(command)
            
        elif("goto" in command and "if-goto" not in command):
            output += translate_goto(command)
        
        elif("if-goto" in command):
            output += translate_if_goto(command)
            
        elif("function" in command):
            output += translate_function(command)    
        
        elif("return" in command):
            output += translate_return(command)
            
        elif("call" in command):
            var_counter += 1
            output += translate_call(command, var_counter)        
            
        else:
            output += "ERROR IN PROCESSING COMMAND:" + command
            
        output += "//" + command + "\n\n"


    return output

def translate_return(command):
    output = ("@LCL\n"      #FRAME = LCL
              "D=M\n"
              "@FRAME\n"
              "M=D\n"

              "@FRAME\n" #RET = *(FRAME- 5) 
              "D=M\n"       
              "@5\n"
              "A=D-A\n"
              "D=M\n"
              "@RET\n"
              "M=D\n"

              "@SP\n"       #*ARG = pop()
              "A=M-1\n"
              "D=M\n"
              "@ARG\n"
              "A=M\n"
              "M=D\n"              

              "D=A+1\n"     #SP = ARG + 1
              "@SP\n"
              "M=D\n"

              "@FRAME\n"    #THAT = *(FRAME - 1)
              "D=M\n"
              "@1\n"
              "A=D-A\n"
              "D=M\n"
              "@THAT\n"
              "M=D\n"

              "@FRAME\n"    #THIS = *(FRAME - 2)
              "D=M\n"
              "@2\n"
              "A=D-A\n"
              "D=M\n"
              "@THIS\n"
              "M=D\n"
              
              "@FRAME\n"    #ARG = *(FRAME - 3)
              "D=M\n"
              "@3\n"
              "A=D-A\n"
              "D=M\n"
              "@ARG\n"
              "M=D\n"
              
              "@FRAME\n"    #LCL = *(FRAME - 4)
              "D=M\n"
              "@4\n"
              "A=D-A\n"
              "D=M\n"
              "@LCL\n"
              "M=D\n"

              "@RET\n"      #goto RET
              "A=M\n"
              "0;JMP\n"                          
              )


    return output

def translate_function(command):
    input = command.replace("function","")
    splitter_index = get_indexof_num(input)    
    input_f = input[0:splitter_index]
    input_k = input[splitter_index:len(input)]
    output = "(" + input_f + ")\n" #(f)
    
    #push 0, repeat k times
    for index in range(0, int(input_k)):
        output += ("@SP\n" 
               "A=M\n"    
               "M=0\n"
               "A=A+1\n"
               "D=A\n"
               "@SP\n"
               "M=D\n")
    return output               
    

def translate_call(command, var_counter):
    input = command.replace("call","")
    splitter_index = get_indexof_num(input)    
    input_f = input[0:splitter_index]
    input_n = input[splitter_index:len(input)]
    
    push_general_command = ("@SP\n"
                            "A=M\n"
                            "M=D\n"
                            "@SP\n"
                            "M=M+1\n")    
    
    output = ("@SP\n" #put stack pointer location into R13
              "D=M\n"
              "@R13\n"
              "M=D\n"
              
              "@RET." + str(var_counter) + "\n" #push return-address
              "D=A\n" +
              push_general_command +
              
              "@LCL\n"  #push LCL
              "D=M\n" +
              push_general_command +      
              
              "@ARG\n" #push ARG
              "D=M\n" +
              push_general_command +
              
              "@THIS\n" #push THIS
              "D=M\n" +
              push_general_command +
              
              "@THAT\n" #push THAT
              "D=M\n" +
              push_general_command +
              
              "@R13\n" #ARG = SP - n - 5    
              "D=M\n"
              "@" + input_n + "\n"
              "D=D-A\n"
              "@ARG\n"
              "M=D\n"
              
              "@SP\n" #LCL = SP
              "D=M\n"
              "@LCL\n"
              "M=D\n"
              
              "@" + input_f + "\n" #goto f
              "0;JMP\n"
              "(RET." + str(var_counter) + ")\n" #(return-address)
              )    
    return output

def translate_if_goto(command):
    input = command.replace("if-goto", "")
    output = ("@SP\n"
              "AM=M-1\n"
              "D=M\n"
              "@" + input + "\n"
              "D;JNE\n")
    return output

def translate_goto(command):
    input = command.replace("goto", "")
    output = ("@" + input + "\n"
              "0;JMP\n")
    return output

def translate_label(command):
    input = command.replace("label","")
    output = "(" + input + ")" + "\n"
    return output    
    

def create_command_dict():
    command_dict = {}
    command_dict["sub"] = ("@SP\n"   
                "AM=M-1\n" 
                "D=M\n" 
                "A=A-1\n" 
                "M=M-D\n")
    command_dict["add"] = ("@SP\n" 
                "AM=M-1\n"
                "D=M\n"
                "A=A-1\n"
                "M=M+D\n")
    command_dict["neg"]=("@SP\n"
                "A=M-1\n"
                "M=-M\n")
    command_dict["not"] = ("@SP\n"
                "A=M-1\n"
                "M=!M\n")
    command_dict["or"] = ("@SP\n"
                "AM=M-1\n"
                "D=M\n"
                "A=A-1\n"
                "M=D|M\n")
    command_dict["and"] = ("@SP\n"
                "AM=M-1\n"
                "D=M\n"
                "A=A-1\n"
                "M=D&M\n")  
    return command_dict  
    
def dynamic_command(command, var_counter):    
    if(command == "gt"):
        output = ("@SP\n"
                  "AM=M-1\n"
                  "D=M\n"
                  "A=A-1\n"
                  "D=M-D\n"
                  "@GT.TRUE" + str(var_counter) + "\n"
                  "D;JGT\n"
                  "@SP\n"
                  "A=M-1\n"
                  "M=0\n"
                  "@GT.CONTINUE" + str(var_counter) + "\n"
                  "0;JMP\n"
                  "(GT.TRUE" + str(var_counter) +")\n"
                  "@SP\n"
                  "A=M-1\n"
                  "M=-1\n"
                  "(GT.CONTINUE" + str(var_counter) + ")\n")
    elif(command == "lt"):
        output = ("@SP\n"
                  "AM=M-1\n"
                  "D=M\n"
                  "A=A-1\n"
                  "D=M-D\n"
                  "@LT.TRUE" + str(var_counter) + "\n"
                  "D;JLT\n"
                  "@SP\n"
                  "A=M-1\n"
                  "M=0\n"
                  "@LT.CONTINUE" + str(var_counter) + "\n"
                  "0;JMP\n"
                  "(LT.TRUE" + str(var_counter) +")\n"
                  "@SP\n"
                  "A=M-1\n"
                  "M=-1\n"
                  "(LT.CONTINUE" + str(var_counter) + ")\n")    
    elif(command == "eq"):
        output = ("@SP\n"
                  "AM=M-1\n"
                  "D=M\n"
                  "A=A-1\n"
                  "D=M-D\n"
                  "@EQ.TRUE" + str(var_counter) + "\n"
                  "D;JEQ\n"
                  "@SP\n"
                  "A=M-1\n"
                  "M=0\n"
                  "@EQ.CONTINUE" + str(var_counter) + "\n"
                  "0;JMP\n"
                  "(EQ.TRUE" + str(var_counter) +")\n"
                  "@SP\n"
                  "A=M-1\n"
                  "M=-1\n"
                  "(EQ.CONTINUE" + str(var_counter) + ")\n")        
    
    return output      
        
def translate_push_or_pop(command, file_name):
    output = ""
    push_general_command = ("@SP\n"
                            "A=M\n"
                            "M=D\n"
                            "@SP\n"
                            "M=M+1\n")
    pop_general_command = ("@R13\n"
                           "M=D\n"
                           "@SP\n"
                           "AM=M-1\n"
                           "D=M\n"
                           "@R13\n"
                           "A=M\n"
                           "M=D\n")                      
    if("push" in command):
        if("constant" in command):    
            input = command.replace("pushconstant","")
            output = ("@"  + str(input) + "\n"
                      "D=A\n" +
                      push_general_command)
        elif("local" in command):
            input = command.replace("pushlocal","")
            output = ("@LCL\n"
                      "D=M\n"
                      "@" + str(input) + "\n"
                      "A=D+A\n"
                      "D=M\n" +
                      push_general_command)
        elif("static" in command):
            input = command.replace("pushstatic","")
            output = ("@" + file_name + "." + str(input) + "\n"
                      "D=M\n" +
                      push_general_command)              
        elif("argument" in command):
            input = command.replace("pushargument","")
            output = ("@ARG\n"
                      "D=M\n"
                      "@" + str(input) + "\n"
                      "A=D+A\n"
                      "D=M\n" +
                      push_general_command)
        elif("this" in command):
            input = command.replace("pushthis","")
            output = ("@THIS\n"
                      "D=M\n"
                      "@" + str(input) + "\n"
                      "A=D+A\n"
                      "D=M\n" +
                      push_general_command)
        elif("that" in command):
            input = command.replace("pushthat","")
            output = ("@THAT\n"
                      "D=M\n"
                      "@" + str(input) + "\n"
                      "A=D+A\n"
                      "D=M\n" +
                      push_general_command)            
        elif("pointer" in command):
            input = command.replace("pushpointer","")
            if int(input) == 0:
                output = ("@THIS\n"
                          "D=M\n" +
                          push_general_command)
            else:
                output = ("@THAT\n"
                          "D=M\n" +
                          push_general_command)                  
        elif("temp" in command):
            input = command.replace("pushtemp","")
            output = ("@R5\n"
                      "D=A\n"
                      "@" + str(input) + "\n"
                      "A=D+A\n"
                      "D=M\n" +
                      push_general_command)
        else:
            output = "ERROR IN PUSH COMMAND"
    elif("pop" in command):
        if("argument" in command):
            input = command.replace("popargument","")
            output = ("@ARG\n"
                      "D=M\n"
                      "@" + str(input) + "\n"
                      "D=D+A\n" +
                      pop_general_command)
        elif("temp" in command):
            input = command.replace("poptemp","")
            output = ("@R5\n"
                      "D=A\n"
                      "@" + str(input) + "\n"
                      "D=D+A\n" +
                      pop_general_command)
        elif("pointer" in command):
            input = command.replace("poppointer", "")
            if(int(input) == 1):
                output = ("@SP\n"
                          "AM=M-1\n"
                          "D=M\n"
                          "@THAT\n"
                          "M=D\n")
            else:
                output = ("@SP\n"
                          "AM=M-1\n"
                          "D=M\n"
                          "@THIS\n"
                          "M=D\n")     
        elif("local" in command):
            input = command.replace("poplocal","")
            output = ("@LCL\n"
                      "D=M\n"
                      "@" + str(input) + "\n"
                      "D=D+A\n" +
                      pop_general_command)        
        elif("this" in command):
            input = command.replace("popthis","")
            output = ("@THIS\n"
                      "D=M\n"
                      "@" + str(input) + "\n"
                      "D=D+A\n" +
                      pop_general_command)            
        elif("that" in command):
            input = command.replace("popthat","")
            output = ("@THAT\n"
                      "D=M\n"
                      "@" + str(input) + "\n"
                      "D=D+A\n" +
                      pop_general_command)                
        elif("static" in command):
            input = command.replace("popstatic","")
            output = ("@SP\n"
                      "AM=M-1\n"
                      "D=M\n"
                      "@"+ file_name + "." + str(input) + "\n"
                      "M=D\n")
        else:
            output = "ERROR IN POP COMMAND"
    return output

def get_indexof_num(function):
    for i in range(len(function)-1, 0, -1):
        if not function[i].isdigit():
            return i+1

def stringParser(filePath):
    filePathName = filePath  
    outString = ""
    
    with open(filePathName, 'r') as file:
        multiLineComment = False
        for line in file.readlines():
            if line == "\n": #Removes blank lines
                continue
            if "//" in line: #Splits line if // occurs, and takes left half string + "\n" 
                line = line.split("//")[0] + "\n"
                if(line == "\n"): #if it's a blank line, just remove it 
                    line = ""
                
            if "/*" in line: #If we find multiline comment
                leftLine = line.split("/*")[0] #Make sure to print left string in line outside of comment
                #Append on the extra left string, as we will stop appending everything 
                #until we find the end comment */
                multiLineComment = True   #Until we find a correponding "*/", assume it will exist on another line
                
                rightLine = "" 
                if "*/" in line: #Check if "*/" exists on the same line
                    rightLine = line.split("*/")[1] #Make sure to print right string in line outside of comment
                    if rightLine == "\n": #If there is no right string, don't print a new line
                        rightLine = ""
                    multiLineComment = False                
                    
                line = leftLine + rightLine #Make line only text outside of "/* */"
                outString += line                 
            
            if "*/" in line: #If we find corresponding end comment, then print rest of line on right side
                line = line.split("*/")[1] #Make sure to print right string in line outside of comment
                if line == "\n": #If there is no right string, don't print a new line
                    line = ""
                multiLineComment = False
                
            line = line.replace(" ", "") #Remove empty spaces
            line = line.replace("\t", "") #Remove empty tabs
            
            if multiLineComment == False:
                outString += line
    return outString
    
if __name__ == '__main__':
    main()

    