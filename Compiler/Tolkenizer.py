import re


def initialize_lexical_elements():
    keywords = initialize_keyword()
    symbols = initialize_symbol()
    integer_constants = initialize_integer_constant()
    string_constants = initialize_string_constant()
    identifier = initialize_identifier()
    return('{}|{}|{}|{}|{}'.format(keywords, symbols, integer_constants, string_constants, identifier))

def initialize_keyword():
#    return """(class|constructor|function|method|field|static|var|int|char|boolean|void|true|false|null|this|let|do|if|else|while|return)"""
    return('(class|constructor|function|method|field|static|var|int|'
    'char|boolean|void|true|false|null|this|let|do|if|else|while|return)'
    '(?=[^\w])')
def initialize_symbol():
    return "([{}()[\].,;+\-*/&|<>=~])"

def initialize_integer_constant():
    return '(\d+)'

def initialize_string_constant():
    return '\"([^\n]*)\"'

def initialize_identifier():
    return '([A-Za-z_]\w*)'
    
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
                
#            line = line.replace(" ", "") #Remove empty spaces
            line = line.replace("\t", "") #Remove empty tabs
#            line = line.replace("\n", "") #Remove empty tabs
            
            if multiLineComment == False:
                outString += line
    return outString

def tolkenize(filename):
    file_input = stringParser(filename)  
    
    lexical_elements = initialize_lexical_elements()
    tolkens_regex = re.findall(pattern = lexical_elements, string = file_input)

    output = "<tokens>\n"

    for tolken in tolkens_regex:
        if tolken[0]: output += "<keyword> " + tolken[0] + " </keyword>\n"
        elif tolken[1]: 
            t = tolken[1]            
            output += "<symbol> " + convert_special_symbols(t) + " </symbol>\n"
        elif tolken[2]: output += "<integerConstant> " + tolken[2] + " </integerConstant>\n"
        elif tolken[3]: output += "<stringConstant> " + tolken[3] + " </stringConstant>\n"
        elif tolken[4]: output += "<identifier> " + tolken[4] + " </identifier>\n"

    output += "</tokens>\n"    
    file_path_out = filename.replace(".jack", "") + ".first_tolkenization.xml" 
#    print("Writing translated file into:", file_path_out)
    writeFile = open(file_path_out, "w")
    writeFile.write(output)
    writeFile.close()      
    return file_path_out  

def convert_special_symbols(tolken):
    tolken = tolken.replace("&", "&amp;") 
    tolken = tolken.replace("<", "&lt;")
    tolken = tolken.replace(">", "&gt;")    
    return tolken

#didnt end up using this structure below
def tolkenize_intermediate(filename):
    file_input = stringParser(filename)  
    
    lexical_elements = initialize_lexical_elements()
    tolkens_regex = re.findall(pattern = lexical_elements, string = file_input)

    tolken_array = []
    counter = 0

    for tolken in tolkens_regex:
        if tolken[0]: 
            tolken_array.append([tolken[0]])
            tolken_array[counter].append("KEYWORD")
            counter += 1
        elif tolken[1]: 
            tolken_array.append([tolken[1]])
            tolken_array[counter].append("SYMBOL")
            counter += 1
        elif tolken[2]: 
            tolken_array.append([tolken[2]])
            tolken_array[counter].append("INT_CONST")
            counter += 1
        elif tolken[3]: 
            tolken_array.append([tolken[3]])
            tolken_array[counter].append("STRING_CONST")
            counter += 1
        elif tolken[4]: 
            tolken_array.append([tolken[4]])
            tolken_array[counter].append("IDENTIFIER")
            counter += 1

#    print(tolken_array)   
    return tolken_array 

   
