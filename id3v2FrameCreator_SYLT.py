'''
ID3v2 Frame Creator: SYLT
-------------------------
Builds a new binary file with a ID3v4 SYLT frame from a LRC file.

Steps/Strategy:
1) Select a LRC file
2) Create and save the frame data

Jens Grätzer
2020-08-23

'''

from sys import exit
from tkinter import *
from tkinter.filedialog import askopenfilename

# --- SETTINGS ---
# Prefix of frame bin files
globBinFilePrefix = "XXX_"  # files starting with this prefix will be deleted at the beginning
# Target filename (BIN file)
globTargetFileName = "XXX_N999_SYLT.BIN"
globTargetLanguage = 'eng'  # 3 characters, e.g. "eng"
globTargetDescription = ''  # Content description
globContentType = b'\x08'    # SYLT content type b'\x08' for "image url" or b'\x00' for "other"

# --- INTERNAL GLOBALS ---
# none

# --- FUNCTIONS ---
def selectImageFile(pickerTitle) :
    ''' Calls a file picker window, that asks for picking a LRC file
    '''
    # Filepicker menue
    root = Tk()
    root.filename =  askopenfilename(title = pickerTitle, filetypes = (("lrc files",".lrc"),("all files",".*")))
    if root.filename == "" :
        #exit(0) # Successful exit
        #print ("Nothing selected.")    
        myFilename = ""
    else : 
        myFilename = root.filename
    root.withdraw()  # Close the Tk window
    return myFilename

def makeFrameCoreBytes(myInputFileName, myLanguage, myContentDescription, myContentType) :  
    # Start the bytes object with the first byte 03H - sets text encoding to UTF-8
    frameBytes = b'\x03'
    
    # Append language code, e.g. 'eng'
    frameBytes = frameBytes + bytes(myLanguage, 'utf-8')

    # Append time format - always 02H for miliseconds
    frameBytes = frameBytes + b'\x02'
    
    # Append content type - 00H for 'other' or 08H for 'image url'
    frameBytes = frameBytes + myContentType

    # Append content description
    frameBytes = frameBytes + bytes(myContentDescription, 'utf-8') + b'\x00' 

    # Append text bytes from file myInputFileName
    '''
    try :
        with open(myImageFileName, "rb") as f:  # read in binary mode
            bytesObject = f.read()
            frameBytes = frameBytes + bytesObject
    except FileNotFoundError :
        print('writeTempFrameCore() FATAL ERROR on reading ' + myImageFileName)
        exit(1) # Exit with error code 1
    '''

    # Read TXT file into array of strings (lines)
    with open(myInputFileName, "r", encoding="utf-8-sig") as file :   # "utf-8-sig" removes BOM
        linesArray = file.readlines()

    # append every line to the result bytes
    for line in linesArray:
        line = line.strip()

        # if it is a correct LRC line only, it looks like [mm:ss.xx]
        if len(line) >= 10 and line[0] == '[' and line[3] == ':' and line[9] == ']' :
            min = int(line[1:3])
            sek = int(line[4:6])
            ms = int(line[7:9]) * 10
            ms = (min * 60 + sek) * 1000 + ms
            textpart = line[10:]
            print(str(ms) + 'ms\t ' + textpart)  # Test
            if textpart.startswith('~') :
                # Our definition for the LRC file: First letter '~' indicates, that 
                # the letters following continue at the last line, but not at a new line.
                textpart = line[11:]
                frameBytes = frameBytes + bytes(textpart, 'utf-8')
            else :
                # New text, that does not start with a space, must
                # be text on a new line, rather a next word at a given line.
                # So write a 0AH (newline) byte before the textpart
                frameBytes = frameBytes + b'\x0a' + bytes(textpart, 'utf-8')
            # Write 00H for "end of textpart"
            frameBytes = frameBytes + b'\x00'
            # Calculate the four bytes of the timestamp (in milliseconds) of this textpart
            b0 = ms & 0b11111111
            tmp = ms >> 8
            b1 = tmp & 0b11111111
            tmp = tmp >> 8
            b2 = tmp & 0b11111111    
            tmp = tmp >> 8
            b3 = tmp & 0b11111111 
            # Append the four bytes of the timestamp to the output bytes
            frameBytes = frameBytes + bytes([b3]) + bytes([b2]) + bytes([b1]) + bytes([b0])
    
    ## Append the 00H byte at the end of the text
    #frameBytes = frameBytes + b'\x00'
    
    # Return the result
    return frameBytes


def writeFrame(myTargetFileName, myFrameCoreBytes, myFrameName) :
    # Get the frame data size
    myCoreSize = len(myFrameCoreBytes)

    # Create frame header "APIC......" (10 Bytes)
    # using a Bytes object - see:
    #   https://en.wikiversity.org/wiki/Python_Concepts/Bytes_objects_and_Bytearrays#bytes_objects
    #   https://techtutorialsx.com/2018/02/04/python-converting-string-to-bytes-object/
    # Start with 4 bytes of frame name
    #headerBytes = b'\x41\x50\x49\x43'  # e.g. APIC frame start with these 4 bytes: 49 44 33 04
    headerBytes = bytes(myFrameName, 'utf-8')
    
    # Calculate the next 4 bytes: Frame size as synchsave integer (4 bytes with 7 bits)
    byte7 = myCoreSize & 0b01111111
    tmp = myCoreSize >> 7
    byte6 = tmp & 0b01111111
    tmp = tmp >> 7
    byte5 = tmp & 0b01111111    
    tmp = tmp >> 7
    byte4 = tmp & 0b01111111    
    
    # Append the next 4 bytes (Mind the [] brackets!)
    headerBytes = headerBytes + bytes([byte4]) + bytes([byte5]) + bytes([byte6]) + bytes([byte7])
    
    # Append 2 flag bytes:    
    headerBytes = headerBytes + b'\x00\x00'
    
    # Write the headerBytes data to destination file with "wb". Overides old file.
    with open(myTargetFileName, "wb") as fileTarget:
        fileTarget.write(headerBytes)
        
    # Append the myFrameCoreBytes
    with open(myTargetFileName, "ab") as fileTarget:
        fileTarget.write(myFrameCoreBytes)


# --- MAIN SCRIPT ---
# Choose the SRT File
srtFileName = selectImageFile("Choose the LRC file")

if srtFileName == "" :
    print ("Nothing selected")    
    exit(0) # Successful exit
    
# Make the SYLT frame core content bytes
frameCoreBytes = makeFrameCoreBytes(srtFileName, globTargetLanguage, globTargetDescription, globContentType)

# Store the USLT frame in BIN file
writeFrame(globTargetFileName, frameCoreBytes, "SYLT")

# Finish
print("OK, ready: " + globTargetFileName)