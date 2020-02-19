import Tolkenizer
from CompilationUnit_P2 import CompilationUnit_P2
import sys
import os
from VMWriter import VMWriter

def main():
    # upload all files from path provided as arg
    file_path = sys.argv[1]    
        
#    file_path = "C:/Users/eddie/Documents/MSCS/Intro to Computer Systems/shimEddieProject11/Seven/"
#    file_path = "C:/Users/eddie/Documents/MSCS/Intro to Computer Systems/shimEddieProject11/ConvertToBin/"
#    file_path = "C:/Users/eddie/Documents/MSCS/Intro to Computer Systems/shimEddieProject11/Square/"    
#    file_path = "C:/Users/eddie/Documents/MSCS/Intro to Computer Systems/shimEddieProject11/Average/"
#    file_path = "C:/Users/eddie/Documents/MSCS/Intro to Computer Systems/shimEddieProject11/Pong/"    
#    file_path = "C:/Users/eddie/Documents/MSCS/Intro to Computer Systems/shimEddieProject11/ComplexArrays/"
    
    jack_files = []    
    for files_in in os.listdir(file_path):
        if(".jack" in files_in):            
            jack_files.append(files_in)
    print("Jack files found in filepath: ", jack_files)
    
    # loop through each file and translate each .jack file into an vm file
    for jack_file in jack_files:
        file_path_in = file_path + jack_file
        print("Loaded file from: " + file_path_in + "\n")                      
    
        #first, tolkenize each atom of the script and assign corresponding terminal element
#        tolken_file_name = file_path_in.replace(".jack","") + "T.xml"
        tolkens = Tolkenizer.tolkenize_intermediate(file_path_in)           
#        for t in tolkens: print(t)
        
        #next, take tolkens and compile them into vm arguments       
        vm_file_path_out = file_path_in.replace(".jack","") + ".vm"
        print("Writing into VM file path: " + vm_file_path_out)
        
        vm_writer_unit = VMWriter(vm_file_path_out)
        CompilationUnit_P2(vm_writer_unit, tolkens)

    
if __name__ == '__main__':
    main()