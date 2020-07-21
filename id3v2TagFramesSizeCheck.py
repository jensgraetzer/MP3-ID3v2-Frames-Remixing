'''
UNFERTIG ... Alle Logik fehlt noch.

ID3v2 Tag Frames Size Check
---------------------------
This script checks and rewrites the frame size within ID3v2.4 frames, stored 
in separate .bin files. Attention: ID3v2.4 frames thell their size using
synchsave integers, but ID3v2.3 frames use standard integers instead.

At the start there are .bin frame files, e.g.:

* XXX_N001_TIT2.bin    # The .bin frames file wildcard is: XXX_N*.bin
* XXX_N002_TPE1.bin
* XXX_N003_TDRL.bin

These frame files originate from the "ID3v2 Tag Exporter" (_id3v2TagExtractor.py).

This script doesn't check the validity of other data than the size.

Working Steps of this script:
* Read a .bin frame file into a array.
* Get the array size.
* Get the frame size value found in the frame header in the array
  data. In ID3v2.4 frames the size is stored by an synchsave integer.
* Compare the array size with the size value found in the 
  frame header. Print the result.
* Do this with all frame files.

J. Grätzer
2020-07-21

'''

from sys import exit
import os
import glob


# --- SETTINGS ---
# Prefix of frame bin files
#globId3v2Version = 4    # 3 or 4 (4 is recommended)
globBinFilePrefix = "XXX_"
globFrameFilePrefix = globBinFilePrefix + "N"  # "XXX_N"

# --- FUNCTIONS ---
def doAllFramesFile() :
    ''' Writes a temporary binary file with all frames,
        from the ID3 frames files. The frames wildcard is: XXX_N*.bin
        Returns the length of the temporary binary file written.
        Returns 0. if no temporary binary file has been written.
    '''
    print("doAllFramesFile() START")
    
    # get a list of file paths that matches pattern
    myFileWildcard = globFrameFilePrefix + "*.bin"
    fileList = glob.glob(myFileWildcard, recursive=False)
    fileList.sort(reverse=False)  # make sure the list is sorted

    # Iterate over the list of input files
    for filePath in fileList:
        print('--> ' + filePath)

        # Read the actual file
        try :
            with open(filePath, "rb") as f:  # read in binary mode
                bytesObject = f.read()
                objectSize = len(bytesObject)
                dataSize = objectSize - 10  # the size without 10 header bytes
                
                # calculate the frame size as synchsave integer (4 bytes with 7 bits)
                siByte4 = dataSize & 0b01111111
                tmp = dataSize >> 7
                siByte3 = tmp & 0b01111111
                tmp = tmp >> 7
                siByte2 = tmp & 0b01111111    
                tmp = tmp >> 7
                siByte1 = tmp & 0b01111111
                
                # calculate the frame size as integer (4 bytes with 8 bits)
                iByte4 = dataSize & 0b11111111
                tmp = dataSize >> 8
                iByte3 = tmp & 0b11111111
                tmp = tmp >> 8
                iByte2 = tmp & 0b11111111    
                tmp = tmp >> 8
                iByte1 = tmp & 0b11111111
                
                '''
                # Test output
                print('---' + filePath)
                print(bytesObject[4])
                print(bytesObject[5])
                print(bytesObject[6])
                print(bytesObject[7])
                print('--')
                print(siByte1)
                print(siByte2)
                print(siByte3)
                print(siByte4)
                print('--')
                print(iByte1)
                print(iByte2)
                print(iByte3)
                print(iByte4)
                '''
                
                ok = False
                if (bytesObject[4] == siByte1 and
                    bytesObject[5] == siByte2 and
                    bytesObject[6] == siByte3 and
                    bytesObject[7] == siByte4) :
                    print('    OK, the frame size fits ID3v2.4')
                    ok = True
                if (bytesObject[4] == iByte1 and
                    bytesObject[5] == iByte2 and
                    bytesObject[6] == iByte3 and
                    bytesObject[7] == iByte4) :
                    if ok :
                        print('    It also fits ID3v2.3')
                    else :
                        print('    The frame size only fits ID3v2.3')
                    ok = True
                if ok == False :  
                    print('    ERROR: The frame size is wrong.')
                    
        except FileNotFoundError :
            print('writeAllFramesFile() FATAL ERROR')
            exit(1) # Exit with error code 1

    return


# --- MAIN SCRIPT ---
# Get the file size of 
doAllFramesFile()
    
# Finish
print("OK, ready.")

