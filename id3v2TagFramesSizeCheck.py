'''
UNCOMLETE ... 
(UNFERTIG ... Alle Logik fehlt noch.)

ID3v2 Tag Frames Size Check
---------------------------
This script checks the frame size within ID3v2.4 frames, stored 
in separate *.bin files.

This is useful becouse: ID3v2.4 frames thell their size using synchsave integers,
but ID3v2.3 frames use standard integers instead. These numbers may be different.
If you reassamble a ID3v2.4 tag be sure to use only *.bin files, that fit
to the ID3v2.4 standard.

Usage: At the beginning there are some ID3v2 frame files (*.bin files), e.g.:

* XXX_N001_TIT2.bin      # The .bin frames file wildcard is: XXX_N*.bin
* XXX_N002_TPE1.bin
* XXX_N003_TDRL.bin

Than run the script.

This script checks the validity of the frame size value given in the frame.
It outputs, weather the size given fits to ID3v2.4 and/or ID3v2.3 standard,
or is a wrong value at all.

This script doesn't check the validity of other data than the size.

J. Grätzer
2020-07-21

'''

from sys import exit
import os
import glob


# --- SETTINGS ---
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
                    print('    Valid frame size - ID3v2.4')
                    ok = True
                if (bytesObject[4] == iByte1 and
                    bytesObject[5] == iByte2 and
                    bytesObject[6] == iByte3 and
                    bytesObject[7] == iByte4) :
                    if ok :
                        print('    Valid frame size - ID3v2.3 as well')
                    else :
                        print('    Valid frame size - ID3v2.3 only')
                    ok = True
                if ok == False :  
                    print('    ERROR: Wrong frame size.')
                    
        except FileNotFoundError :
            print('writeAllFramesFile() FATAL ERROR')
            exit(1) # Exit with error code 1

    return


# --- MAIN SCRIPT ---
# Get the file size of 
doAllFramesFile()
    
# Finish
print("OK, ready.")

