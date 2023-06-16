'''
ID3v2 Tag Extractor
-------------------
* Opens a file picker for selection of a MP3 file
* Reads the MP3 file selected. Makes shure, that it contains a ID3v2.3 or ID3v2.4 tag.
* Deletes all older files XXX_*.*
* Writes the pure audio data (without ID3v2 tag) into file XXX_audio.mp3
* Writes the ID3v2 header into file XXX_header.bin
* Writes every ID3v2 frame into an own file,
  e.g. file XXX_01_TIT2.bin (01 is the position of the frame within the tag)

J. Grätzer, 2020-06-07
'''

from sys import exit
import os
import glob
from tkinter import *
from tkinter.filedialog import askopenfilename

# --- SETTINGS ---
# Prefix of frame bin files
globBinFilePrefix = "XXX_"

# --- INTERNAL GLOBALS ---
# Frame counter
globFrameCounter = 0

# --- FUNCTIONS ---
def deleteFiles(myFileWildcard) :
    ''' Deletes all files, that filenames match myFileWildcard
    '''
    print("deleteFiles() ... myFileWildcard = " + myFileWildcard)
        
    # get a list of file paths that matches pattern
    fileList = glob.glob(myFileWildcard, recursive=False) 
    # Iterate over the list of filepaths & remove each file.
    for filePath in fileList:
        try:
            #if os.path.exists(filePath):
            os.remove(filePath)
        except OSError:
            print("deleteFiles () ... ERROR while deleting file")
                 
def readSomeBytesFromFile(myfile, myN):
    ''' Reads n=myN bytes from a file in binary mode into a bytes object.
        Returns that bytes object.
    '''  
    # Because file may not exist - use try!
    try :
        with open(myfile, "rb") as f:  # read in binary mode
            bytesObject = f.read(myN)
    except FileNotFoundError :
        print('ERROR: File does not exist')
        exit(0) # Successful exit
    #print("TEST: data type of bytesObject is: " + str(type(bytesObject)))
    return bytesObject
    
def processFirst10Bytes(myfile) :
    ''' Reads first 10 Bytes of a mp3 file, analyses ID3 tag header,
        returns bruttoSize, flagUnsync, flagExtendedHeader, flagFooter
    '''
    # read bytes from file
    bytesRead = readSomeBytesFromFile(myfile, 10)
    
    if len(bytesRead) < 10 :
        print("EXIT: this file is too short.")
        exit(0) # Successful exit    

    #print("START=" + str(bytesRead[0]))  # Test
    #for byte in bytesRead:
    #    print("Byte=" + str(byte))

    # Test: first three bytes are "ID3"?
    # https://stackoverflow.com/questions/509211/understanding-slice-notation
    firstThreeBytesString = bytesRead[0:3].decode("latin-1")
    print ("OK, the first bytes are: " + firstThreeBytesString)

    if firstThreeBytesString == "ID3" :
        print("OK, there is an ID3v2 tag.")
    else :
        print("EXIT: This file has no ID3v2 tag.")
        exit(0) # Successful exit
        
    # Get the ID3v2 revision number from bytes 3 and 4 (starting with 0)
    version = int(bytesRead[3])
    revision = int(bytesRead[4])
    myId3Vers = version
    print("OK, version is: ID3v2." + str(version) + "." + str(revision))   
    if version != 3 and version != 4  :
        print("EXIT: This version is other than 3 or 4.")
        exit(0) # Successful exit
        
    # Write a bin file of the header bytes
    saveBytesInARange(bytesRead, 0, 9, globBinFilePrefix + "header.bin")
    
    # Read the flags in byte 5 (starting with 0)
    # Bitwise Operators see: https://wiki.python.org/moin/BitwiseOperators
    fa = bytesRead[5] & 0b10000000
    fb = bytesRead[5] & 0b01000000
    fc = bytesRead[5] & 0b00100000
    fd = bytesRead[5] & 0b00010000
    
    myFlagUnsync = False
    myFlagExtendedHeader = False
    myFlagFooter = False
    if (fa == 0) :
        print("OK, flag a of byte 5: no unsynchronisation")        
    else :
        print("OK, flag a of byte 5: unsynchronisation is used")
        myFlagUnsync = True
    if (fb == 0) :
        print("OK, flag b of byte 5: no extended header")        
    else :
        myFlagExtendedHeader = True
        print("OK, flag b of byte 5: extended header is used")
    if (fc == 0) :
        print("OK, flag c of byte 5: this is not an experimental tag")        
    else :
        print("OK, flag c of byte 5: this tag is experimental")
    if (fd == 0) :
        print("OK, flag d of byte 5: there is no footer present at the end of the tag")        
    else :
        myFlagFooter = True
        print("OK, flag d of byte 5: a footer is present at the end of the tag")

    # Read the tag size in bytes 6 to 9 (starting with 0)
    # (Synchsave integers - see https://stackoverrun.com/de/q/1272468)
    mySize = int(bytesRead[6])       
    mySize = mySize * 128 + int(bytesRead[7])
    mySize = mySize * 128 + int(bytesRead[8])
    mySize = mySize * 128 + int(bytesRead[9])
    
    print("OK, the tag-only size is: " + str(mySize) + " = "  + hex(mySize))
    
    #exit(0) # Successful exit TEST ----------

    if myFlagFooter == True :
        myBruttoSize = 20 + mySize   # Header is 10 bytes, and footer is 10 bytes long
    else :
        myBruttoSize = 10 + mySize   # Header is 10 bytes long, and there is no footer

    return myBruttoSize, myFlagUnsync, myFlagExtendedHeader, myFlagFooter, myId3Vers

def readFullTag(myfile, myBruttoSize) :
    ''' Reads myBruttoSize bytes of a file,
        returns the number of bytes read.
    '''
    # read bytes from file
    bytesRead = readSomeBytesFromFile(myfile, myBruttoSize)
    return bytesRead

def processExtendedHeader(myFullTag, myId3Vers) :
    ''' Reads and analyses the extended header of an ID3 tag,
        returns the adress after that header
    '''
    # Since the function is called, is assumed, the extended header exists:     
    # Read the tag size in bytes 10 to 13 (starting with 0) of the tag.
    # (Synchsave integers - see https://stackoverrun.com/de/q/1272468)
    digitVal = 128  # Jede Stelle der Größe ist 128 wert - in ID3v2.4 Tag (synchsave)
    if myId3Vers == 3 :
        digitVal = 256  # Jede Stelle der Größe ist 256 wert - in ID3v2.3 Tag (nicht synchsave)
    mySize = int(myFullTag[10])
    mySize = mySize * digitVal + int(myFullTag[11])
    mySize = mySize * digitVal + int(myFullTag[12])    
    mySize = mySize * digitVal + int(myFullTag[13])
    
    print("OK, the extended header size is: " + str(mySize))
    myNextDataByte = mySize + 10
    # In this function there is no processing of the extended header data.
    # Instead, only the next data byte adress is returned.
    return myNextDataByte

def processAFrame(myFullTag, sa, myFlagUnsync, myId3Vers) :
    ''' Reads and analyses the follwoing (at start adress sa) ID3 tag,
        returns the framename and the adress after that frame
    '''
    # Break, if there is no frame name, but padding bytes instead
    if int(myFullTag[sa]) == 0x00 or int(myFullTag[sa + 1]) == 0x00 :  # Padding is of 00H bytes
        print("   Padding with 0x00 bytes starts at = " + hex(sa))
        myNextDataByte = 0
        return "", myNextDataByte   # adress 0 returned indicates, that there is no more frames ahead
    
    # Read the frame name
    myFrameName = myFullTag[sa:sa + 4].decode("latin-1")
    print("-> " + myFrameName)  # Ausgabe des Namens des Frame
    
    digitVal = 128  # Jede Stelle der Größe ist 128 wert - in ID3v2.4 Tag (synchsave)
    if myId3Vers == 3 :
        digitVal = 256  # Jede Stelle der Größe ist 256 wert - in ID3v2.3 Tag (nicht synchsave)
    s = int(myFullTag[sa + 4])
    s = s * digitVal + int(myFullTag[sa + 5])
    s = s * digitVal + int(myFullTag[sa + 6])
    s = s * digitVal + int(myFullTag[sa + 7])
    mySize = s + 10    # Adding the size of the frame header
    myFlag1 = myFullTag[sa + 8]  # Flag für status messages
    myFlag2 = myFullTag[sa + 9]
    
    myNextDataByte = sa + mySize
    print("   Next adress is " + str(myNextDataByte) + " = " + hex(myNextDataByte))
    
    return myFrameName, myNextDataByte     # Return the next start adress after this frame and the framename

def selectMp3File() :
    ''' Calls a file picker window, that asks for picking a MP3 file
    '''
    # Filepicker menue
    root = Tk()
    myFilename =  askopenfilename(title = "choose your file", filetypes = (("mp3 audio files","*.mp3"),("all files","*.*")))
    root.withdraw()  # Close the Tk window
    return myFilename

def saveBytesInARange(myFullTag, myStartAdress, myLastAdress, myFileName) :
    ''' Writes a range of bytes from myFullTag into file.
        The range is given by myStartAdress and myLastAdress.
        Filename is: globBinFilePrefix + myTitle + '.bin'
        This way a single ID3-tag-frame of the MP3 file can be saved in a BIN-file.
    '''
    with open(myFileName, "wb") as f:
        byteArray = myFullTag[myStartAdress:myLastAdress + 1]
        f.write(byteArray)

def exportFrame(myFullTag, myFrameName, myStartByteAddress, myLastByteAddress) :
    ''' Check the different Frames
    '''
    if myStartByteAddress >= myLastByteAddress :
        print("   There is no next frame at " + hex(myStartByteAddress))
        return

    global globFrameCounter
    globFrameCounter = globFrameCounter + 1
    
    # Write the frame bytes into a bin file, e.g. XXX_N001_TIT2.bin
    targetFileName = globBinFilePrefix + "N{0:03d}".format(globFrameCounter) + "_" + myFrameName + ".bin"
    saveBytesInARange(myFullTag, myStartByteAddress, myLastByteAddress, targetFileName)

def exportPureAudioStartingAt(myfile, myStartAdress) :
    print("Write pure audio to file starting at " + hex(myStartAdress))
    
    targetFileName = globBinFilePrefix + "audio.mp3"
    with open(targetFileName, "wb") as fTarget:
        # Because the original file may not exist - use try!
        try :
            with open(myfile, "rb") as f:  # read in binary mode
                f.seek(myStartAdress)
                while True:
                    buf = f.read(1024)
                    if buf :
                        # n = fTarget.write(buf)
                        fTarget.write(buf)
                    else:
                        break

        except FileNotFoundError :
            print('ERROR: File does not exist' + myfile)
            exit(1)  # exit with errorcode
   
# --- MAIN SCRIPT ---
# select a MP3 file
filename = selectMp3File()

if filename == "" :
    print ("Nothing selected")    
    exit(0) # Successful exit

#Delete old report files
deleteFiles(globBinFilePrefix + "*.*")

# Analysing this MP3 file
print ("Analysing " + filename)
print("Start reading first 10 bytes of the tag")
bruttoSize, flagUnsync, flagExtendedHeader, flagFooter, tagVers = processFirst10Bytes(filename)
print("Start reading all frames of the ID3v2 tag. Start from " + str(bruttoSize) + " = " + hex(bruttoSize))
fullTag = readFullTag(filename, bruttoSize)
if flagExtendedHeader :
    nextDataByte = processExtendedHeader(fullTag, tagVers)
else :
    nextDataByte = 10   # Header is 10 bytes long

# Read all frames in a do while loop
while True:
    startDataByte = nextDataByte
    frameName, nextDataByte = processAFrame(fullTag, startDataByte, flagUnsync, tagVers)
    exportFrame(fullTag, frameName, startDataByte, nextDataByte - 1)
    # fail_condition for leaving the loop
    if nextDataByte <= 0 or nextDataByte >= bruttoSize :
        break
    
print("OK, end of the tag. Ignoring the footer, next adress is " + hex(bruttoSize))

# Write the pure MP3 data, starting at bruttoSize, into new file
exportPureAudioStartingAt(filename, bruttoSize)

# Finish
print("OK, ready. Data exported into files " + globBinFilePrefix + "*.BIN/MP3")

