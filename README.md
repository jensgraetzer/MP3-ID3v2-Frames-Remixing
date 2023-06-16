# MP3-ID3v2-Frames-Remixing

Creators of new content ideas, involving the ID3v2 tag of MP3 files, need to create content prototypes. The Python scripts of this project may support this experimental content creation. There is a Python script, that exports parts such as the frames of a ID3v2 tag and the audio itself into separate binary files. Every frame of the ID3v2.4 tag will be stored in a single binary file. These files can be edited. Other binary frame files can be deleted. Or a number of newly created binary frame files can be added. There is another Python script, that reassembles these files into a new version of the MP3 file.

Why is this useful? Having separate binary files of every ID3v2.4 tag makes the bitwise editing (with a hex-editor) more easy. (And, as mentioned, adding new frames or deleting frames is possible too.) This, of course, is not a common task.

## id3v2TagExtractor.py

This Python script takes a MP3 file with a ID3v2.3 or ID3v2.4 tag and creates a number of new files. First it creates a file with the pure audio data. This audio file has the file name XXX_audio.mp3. And then it creates a couple of other files with file names, also starting with three letters: XXX. Every single file is the binary data of a single ID3v2 frame found. The names of these files are XXX_N*.bin, where * is a three digit number, followed by a "_" and a name of a ID3v2 frame.

The number is used by the script id3v2TagReassembler.py. It defines the position of the frame within the ID3v2 tag.

What the script does:

* Opens a file picker for selection of a MP3 file
* Reads the MP3 file selected. Makes shure, that it contains a ID3v2.3 or ID3v2.4 tag.
* Deletes all older files XXX_*.*
* Writes the pure audio data (without ID3v2 tag) into file XXX_audio.mp3
* Writes the ID3v2 header into file XXX_header.bin
* Writes every ID3v2 frame into an own file,
  e.g. file XXX_01_TIT2.bin (01 is the position of the frame within the tag)

Usage: Run the script id3v2TagExtractor.py. A file picker opens. Pick a MP3 file and press the "open" button. Find the files created by id3v2TagExtractor.py in the current path. Their names start with "XXX_".

## id3v2TagReassembler.py

This Python script takes the XXX_audio.mp3 file (must be free of ID3 tags) and all the ID3v2.4 frames binary files, found in the current folder, and creates a new MP3 file from it. The new audio file has the file name XXX_newAudio.mp3. It contains a ID3v2.4 tag, made from all of the frames binary files found in the folder.

## id3v2FrameCreator_APIC.py

This Python script creates the binary of an APIC frame, containing a picture. The binary is stored in the file with the name XXX_N999_APIC.bin. Adding this binary file to other binary files, than run the id3v2TagReassembler.py script, creates a MP3 file with a picture.

It's possible to create more than one binary of an APIC frame. This is a way to create MP3 files with more than one picture in it. Simply rename the binary files so they have different filenames, e.g. XXX_N998_APIC.bin and XXX_N999_APIC.bin and so on. Than use the id3v2TagReassembler.py script. Remember: The tree digit numbers define the position of the frame within the ID3 tag. So the number defines, witch image goes first, etc.

## id3v2FrameCreator_SYLT.py

This Python script creates of an APIC frame of a ID3v2.4 tag from a lyrics-text file in the LRC format.

One have to consider, that timing precicion of some MP3 players may be poor, depending on software implementation of the playwer, even at CBR (instead of VBR) MP3 files. So better do not use MP3 audio in karaoke players, but M4A audio for instance.

## id3v2FrameCreator_USLT.py

This Python script creates the binary of an USLT frame. A USLT frame contains the lyrics in simple text format. The Python script let you chose a text file, than it  outputs a binary file with the name XXX_N999_USLT.bin.

## id3v2FrameCreator_XSRT.py

This Python script creates the binary of an experimental frame called XSRT. This frame contains SRT (SubRip) subtitles. The Python script lets you chose a SRT file, than it outputs a binary file with the name XXX_N999_XSRT.bin. This frame has a format similar to the USLT frame.

One have to consider, that timing precicion of some MP3 players may be poor, depending on software implementation of the playwer, even at CBR (instead of VBR) MP3 files. So better do not use MP3 audio in karaoke players, but M4A audio for instance.

## id3v2TagFramesSizeCheck.py

This script checks the frame size within ID3v2.4 frames, stored in separate *.bin files.

This is useful becouse: ID3v2.4 frames thell their size using synchsave integers, but ID3v2.3 frames use standard integers instead. These numbers may be different. If you reassamble a ID3v2.4 tag be sure to use only *.bin files, that fit to the ID3v2.4 standard.

Usage: At the beginning there are some ID3v2 frame files (*.bin files), e.g.:

* XXX_N001_TIT2.bin      # The .bin frames file wildcard is: XXX_N*.bin
* XXX_N002_TPE1.bin
* XXX_N003_TDRL.bin

Than run the script.

This script checks the validity of the frame size value given in the frame.
It outputs, weather the size given fits to ID3v2.4 and/or ID3v2.3 standard,
or is a wrong value at all.

This script doesn't check the validity of other data than the size.
