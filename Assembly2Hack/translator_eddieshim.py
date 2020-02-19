#Project 6 
#Eddie Shim
#Due 10/30/19

import sys

def main():
    filePath = sys.argv[1]    
    text = stringParser(filePath)
    output = convert2Assembly(text)
        
    filePathOut = filePath.replace(".asm", "") + ".hack" 
    print("Writing translated file into:", filePathOut)
    writeFile = open(filePathOut, "w")
    writeFile.write(output)
    writeFile.close()       
    
def lookupTableRight(input):    
    if input == "0" : return "0101010"
    elif input == "1": return "0111111"
    elif input == "-1": return "0111010"
    elif input == "D": return "0001100"
    elif input == "A": return "0110000"
    elif input == "!D": return "0001101"
    elif input == "!A": return "0110001"
    elif input == "-D": return "0001111"
    elif input == "-A": return "0110011"
    elif input == "D+1" or input == "1+D": return "0011111"
    elif input == "A+1" or input == "1+A": return "0110111"
    elif input == "D-1" or input == "-1+D": return "0001110"
    elif input == "A-1" or input == "-1+A": return "0110010"
    elif input == "D+A" or input == "A+D": return "0000010"
    elif input == "D-A" or input == "-A+D": return "0010011"
    elif input == "A-D" or input == "-D+A": return "0000111"
    elif input == "D&A" or input == "A&D": return "0000000"
    elif input == "D|A" or input == "A|D": return "0010101"
    elif input == "M": return "1110000"
    elif input == "!M": return "1110001"
    elif input == "-M": return "1110011"
    elif input == "M+1" or input == "1+M": return "1110111"
    elif input == "M-1" or input == "-1+M": return "1110010"
    elif input == "D+M" or input == "M+D": return "1000010"
    elif input == "D-M" or input == "-M+D": return "1010011"
    elif input == "M-D" or input == "-D+M": return "1000111"
    elif input == "D&M" or input == "M&D": return "1000000"
    elif input == "D|M" or input == "M|D": return "1010101"   
    
def lookupTableLeft(input):
    if input == "": return "000"
    elif input == "M": return "001"
    elif input == "D": return "010"
    elif input == "MD": return "011"
    elif input == "A": return "100"
    elif input == "AM": return "101"
    elif input == "AD": return "110"
    elif input == "AMD": return "111"
    
def lookupTableJump(input):
    if input == "": return "000"
    elif input == "JGT": return "001"    
    elif input == "JEQ": return "010"    
    elif input == "JGE": return "011"    
    elif input == "JLT": return "100"    
    elif input == "JNE": return "101"    
    elif input == "JLE": return "110"    
    elif input == "JMP": return "111"    

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
                
    
def convert2Assembly(input):   
    memory_index = 16 #start memory location for variable names at address 16
    var_table = {} #hash table which stores our variable addresses
    output = ""
    line_counter = 0
    parsedInput = ""
    
    #predefined variables
    screen_location = 16384
    kdb_location = 24576
    sp_location = 0
    lcl_location = 1
    arg_location = 2
    this_location = 3
    that_location = 4
    
    #first scan over code in order to check for jump locations e.g. (LOOP) and store line number as memory
    for line in input.split("\n"):
        if ("(" in line): #check if this is a line we should skip (e.g. (LOOP))
            var = line.replace("(", "").replace(")","")
            var_table[var] = format(int(line_counter), "016b")

        else:
            parsedInput += line + "\n"
            line_counter += 1             
    
    for line in parsedInput.split("\n"):   
            assembly_inst = ""          
            if (len(line) == 0): #parse out any blank lines
                continue
            if ("@" in line): #check if this is a memory location assignment
                var = line.split("@")[1]
                
                if((var[0] == "R" and var[1:len(var)].isdigit()) or var.isdigit()): #given a digit address
                    var = var.replace('R', "")
                    assembly_inst = format(int(var),"016b")                
                
                #predefined variables
                elif (var == "SCREEN"):
                    var_table[var] = format(screen_location, "016b")
                    assembly_inst = format(screen_location, "016b")
                elif (var == "KBD"):
                    var_table[var] = format(kdb_location, "016b")
                    assembly_inst = format(kdb_location, "016b")     
                elif (var == "SP"):
                    var_table[var] = format(sp_location, "016b")
                    assembly_inst = format(sp_location, "016b")
                elif(var == "LCL"):
                    var_table[var] = format(lcl_location, "016b")
                    assembly_inst = format(lcl_location, "016b")
                elif(var == "ARG"):
                    var_table[var] = format(arg_location, "016b")
                    assembly_inst = format(arg_location, "016b")
                elif(var == "THIS"):
                    var_table[var] = format(this_location, "016b")
                    assembly_inst = format(this_location, "016b")
                elif(var == "THAT"):
                    var_table[var] = format(that_location, "016b")
                    assembly_inst = format(that_location, "016b")
                    
                #new variable encountered, put into dictionary with memory location    
                else:                    
                    if var in var_table: #given a variable name address
                        assembly_inst = var_table.get(var) #if it's already assigned a memory location, grab the location
                    else:
                        var_table[var] = format(memory_index,"016b") #if not assigned, assign it a location in the hash table 
                        assembly_inst = format(memory_index,"016b")
                        memory_index += 1; #increment variable locations up starting from 16
                              
            else: #variable assignment, or jump command
                char0to2 = "111"                    
                if("=" in line): #variable assignment
                    left = line.split("=")[0]
                    right = line.split("=")[1]
                    char3to9 = lookupTableRight(right) #c1 to c6 instructions
                    char10to12 = lookupTableLeft(left) #destination instructions
                    char13to15 = "000" #jump instructions
                        
                elif(";" in line): #jump command
                    left = line.split(";")[0]
                    right = line.split(";")[1]
                    char3to9 = lookupTableRight(left) #c1 to c6 instructions
                    char10to12 = "000" #destination instructions
                    char13to15 = lookupTableJump(right) #jump instructions  
                assembly_inst = char0to2 + char3to9 + char10to12 + char13to15                               
                
            
            output += assembly_inst + "\n"
            
                        
    return output  

if __name__ == '__main__':
    main()

