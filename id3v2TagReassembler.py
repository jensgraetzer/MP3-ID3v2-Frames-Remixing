'''
ID3v2.4 Tag Reassembler
-----------------------
This builds a new MP3 file from ID3v2.4 frames files and the pure MP3 data file.
The tag version is 4, so the result is a MP3 with a ID3v2.4 tag.

The script assembles ID3 frames files and a MP3 file into a new MP3 file.
Thus, at the beginning, there are these files:

* XXX_N001_TIT2.bin    # The frames file wildcard is: XXX_N*.bin
* XXX_N002_TPE1.bin
* XXX_N003_TDRL.bin
* XXX_audio.mp3        # pure audio (MP3) data

These files originate from the "ID3v2 Tag Exporter" (_id3v2TagExtractor.py).

This script doesn't check the validity of the frames, found in the .bin frames files.
So make sure, they are valid. Attention: ID3v2.4 frames thell their size using
synchsave integers, but ID3v2.3 frames use standard integers instead.

Working Steps of this script:
1) Writing a temporary binary file with all frames data, found in the .bin frames files.
2) Createing a ID3 tag header, writing it into a new file "target.MP3".
3) Appending the frames data, than the pure audio (MP3) data.

J. Grätzer
2020-05-21
2020-07-19 ... minor bugfix

'''

from sys import exit
import os
import glob


# --- SETTINGS ---
# Prefix of frame bin files
globId3v2Version = 4    # 3 or 4 (4 is recommended)
globBinFilePrefix = "XXX_"
globFrameFilePrefix = globBinFilePrefix + "N"  # "XXX_N"
globAudioFilename = globBinFilePrefix + "audio.mp3"  # "XXX_audio.mp3"
globTempFramesFilename = globBinFilePrefix + "tempFrames.bin"
globNewAudioFilename = globBinFilePrefix + "newAudio.mp3"

# --- INTERNAL GLOBALS ---
# Frame counter
#globFrameCounter = globBinFilePrefix = "XXX_"

# --- FUNCTIONS ---
def writeTheAllFramesTmpFile() :
    ''' Writes a temporary binary file with all frames,
        from the ID3 frames files. The frames wildcard is: XXX_N*.bin
        Returns the length of the temporary binary file written.
        Returns 0. if no temporary binary file has been written.
    '''
    print("writeTheAllFramesTmpFile() START")
    
    # Is there the "XXX_audio.mp3" file?
    if os.path.exists(globAudioFilename) :
        pass
    else :
        print("writeTheAllFramesTmpFile() PROBLEM: Audiofile is missing.")
        return 0
    
    # get a list of file paths that matches pattern
    myFileWildcard = globFrameFilePrefix + "*.bin"
    fileList = glob.glob(myFileWildcard, recursive=False)
    fileList.sort(reverse=False)  # make sure the list is sorted
    
    # Is there the "XXX_audio.mp3" file?
    if len(fileList) == 0 :
        print("writeTheAllFramesTmpFile() PROBLEM: Framefiles are missing.")
        return 0

    # Write the frame data to temp. destination file. "Open w" overrides the old file.
    dataSize = 0
    with open(globTempFramesFilename, "wb") as fileTarget:
        # Iterate over the list of input files
        for filePath in fileList:
            print("writeTheAllFramesTmpFile() " + filePath)

            # Read the actual file
            try :
                with open(filePath, "rb") as f:  # read in binary mode
                    bytesObject = f.read()
                    dataSize = dataSize + len(bytesObject)                    
            except FileNotFoundError :
                print('writeTheAllFramesTmpFile() FATAL ERROR')
                exit(1) # Exit with error code 1

            # write/append the actual data to temp. destination file
            fileTarget.write(bytesObject)
        print('writeTheAllFramesTmpFile() OK: Temporary file saved. dataSize=' + str(dataSize))
 
    return dataSize  # returns the number of bytes written into fileTarget 


def testCopyAFrameFile(myFileNam) :
    # Read the file
    try :
        with open(myFileNam, "rb") as f:  # read in binary mode
            bytesObject = f.read()
    except FileNotFoundError :
        print('testCopyAFrameFile() ERROR: File does not exist: ' + myFileNam)
        exit(0) # Successful exit

    # Write the data to destination file
    fn = "test.bin"
    with open(fn, "wb") as f:
        f.write(bytesObject)

    print('testCopyAFrameFile() OK: Temp. frames file saved.')


def writeAudioFileWithHeaderAndFrames(myAudioFileName, myFrameSize, myAllFramesFileName) :
    # Write the data to destination file with "wb". Overides old file.

    # First: create bytes object "ID3..." (10 Bytes)
    # Bytes object - see:
    #   https://en.wikiversity.org/wiki/Python_Concepts/Bytes_objects_and_Bytearrays#bytes_objects        
    # Start with 6 bytes 49 44 33 04 00 00 (last byte is "flags")
    if globId3v2Version == 3 :
        headerBytes = b'\x49\x44\x33\x04\x00\x00'   # first bytes in ID3v2.3 tag
    else :
        headerBytes = b'\x49\x44\x33\x03\x00\x00'   # first bytes in ID3v2.4 tag
    
    # calculate the next 4 bytes: Frame size as synchsave integer (4 bytes with 7 bits)
    byte9 = myFrameSize & 0b01111111
    tmp = myFrameSize >> 7
    byte8 = tmp & 0b01111111
    tmp = tmp >> 7
    byte7 = tmp & 0b01111111    
    tmp = tmp >> 7
    byte6 = tmp & 0b01111111      
    
    # Append the next 4 bytes (Mind the [] brackets!)
    headerBytes = headerBytes + bytes([byte6]) + bytes([byte7]) + bytes([byte8]) + bytes([byte9])
    
    # Write this bytes object (10 bytes) into a new file 
    with open(myAudioFileName, "wb") as f:
        f.write(headerBytes)
        
    # Append the AllFramesFile bytes to that new file
    with open(myAudioFileName, "ab") as fileTarget:
        try :
            with open(myAllFramesFileName, "rb") as f:  # read in binary mode
                bytesObject = f.read()
                fileTarget.write(bytesObject)
        except FileNotFoundError :
            print('writeAudioFileWithHeaderAndFrames() FATAL ERROR on appending tag.')
            exit(1) # Exit with error code 1

    # Append the AudioFile bytes
    with open(myAudioFileName, "ab") as fileTarget:
        try :
            with open(globAudioFilename, "rb") as f:  # read in binary mode
                bytesObject = f.read()
                fileTarget.write(bytesObject)
        except FileNotFoundError :
            print('writeAudioFileWithHeaderAndFrames() FATAL ERROR on appending audio.')
            exit(1) # Exit with error code 1    

    print('writeAudioFileWithHeaderAndFrames() OK: New file saved.')
    
    # delete the temporary file
    try:
        #if os.path.exists(globTempFramesFilename):
        os.remove(globTempFramesFilename)
        print('writeAudioFileWithHeaderAndFrames() OK: Temporary file deleted.')
    except OSError:
        print("ERROR while deleting temporary file")

# --- MAIN SCRIPT ---
# Write all frames data files into a single temp. file
tmpFileSize = writeTheAllFramesTmpFile()

if tmpFileSize > 0 :
    writeAudioFileWithHeaderAndFrames(globNewAudioFilename, tmpFileSize, globTempFramesFilename)
    
# Finish
print("OK, ready: " + globNewAudioFilename)

