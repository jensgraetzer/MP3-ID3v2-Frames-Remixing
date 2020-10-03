'''
ID3v2 Frame Creator: XSRT
-------------------------
Builds a new binary file with a ID3v4 XSRT frame,
containing SRT subtitles text. A XSRT frame is an experimental frame,
containing SRT text in a format similar to the USLT frame.

Steps/Strategy:
1) Select a srt file
2) Create and save the frame data

Jens Grätzer
2020-10-03 ... Bugfix
2020-08-16

'''

from sys import exit
import os
import ntpath
from tkinter import *
from tkinter.filedialog import askopenfilename

# --- SETTINGS ---
# Prefix of frame bin files
globBinFilePrefix = "XXX_"  # files starting with this prefix will be deleted at the beginning
# Target filename (BIN file)
globTargetFileName = "XXX_N999_XSRT.BIN"
globTargetLanguage = 'eng'  # 3 characters, e.g. 'eng'
globTargetDescription = ''  # Content description

# --- INTERNAL GLOBALS ---
# none

# --- FUNCTIONS ---
def selectImageFile(pickerTitle) :
    ''' Calls a file picker window, that asks for picking a MP3 file
    '''
    # Filepicker menue
    root = Tk()
    root.filename =  askopenfilename(title = pickerTitle, filetypes = (("srt files",".srt"),("all files",".*")))
    if root.filename == "" :
        #exit(0) # Successful exit
        #print ("Nothing selected.")    
        myFilename = ""
    else : 
        myFilename = root.filename
    root.withdraw()  # Close the Tk window
    return myFilename

def makeFrameCoreBytes(mySrtFileName, myLanguage, myContentDescription) :  
    # Start the bytes object with the first byte 03H - sets text encoding to UTF-8
    frameBytes = b'\x03'
    
    # Append language code, e.g. 'eng'
    frameBytes = frameBytes + bytes(myLanguage, 'utf-8')

    # Append content description
    frameBytes = frameBytes + bytes(myContentDescription, 'utf-8') + b'\x00'

    # Append srt text bytes from file myImageFileName
    '''
    try :
        with open(myImageFileName, "rb") as f:  # read in binary mode
            bytesObject = f.read()
            frameBytes = frameBytes + bytesObject
    except FileNotFoundError :
        print('writeTempFrameCore() FATAL ERROR on reading ' + myImageFileName)
        exit(1) # Exit with error code 1
    '''

    # Read SRT file into array of strings (lines)
    with open(mySrtFileName, "r", encoding="utf-8-sig") as file :   # "utf-8-sig" removes BOM
        linesArray = file.readlines()

    # append every line to the result bytes
    for line in linesArray:
        print(line.strip())
        frameBytes = frameBytes + bytes(line.strip(), 'utf-8') + b'\x0a'
    
    # Append the 00H byte at the end of the text
    frameBytes = frameBytes + b'\x00'
    
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
srtFileName = selectImageFile("Choose the SRT File")

if srtFileName == "" :
    print ("Nothing selected")    
    exit(0) # Successful exit
    
# Make the XSRT frame core content bytes
frameCoreBytes = makeFrameCoreBytes(srtFileName, globTargetLanguage, globTargetDescription)

# Store the XSRT frame in BIN file
writeFrame(globTargetFileName, frameCoreBytes, "XSRT")

# Finish
print("OK, ready.")
