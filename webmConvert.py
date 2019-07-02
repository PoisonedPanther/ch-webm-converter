#!/usr/bin/python
import os
import glob
import math
from subprocess import PIPE, run

#probably don't touch these
BITRATE_COMMAND = "ffprobe -v error -select_streams v:0 -show_entries stream=bit_rate -of default=nokey=1:noprint_wrappers=1 {0}"
FAST_CONVERT_COMMAND = "ffmpeg -y -i {0} -vf \"scale='min({1},iw)':-1\" -map 0:v -c:v libvpx -speed 3 -b:v {2} {3}"
SLOW_CONVERT_COMMAND = "ffmpeg -y -i {0} -vf \"scale='min({1},iw)':-1\" -map 0:v -c:v libvpx -b:v {2} {3}"

#user config area
CONVERT_COMMAND = FAST_CONVERT_COMMAND #SLOW_CONVERT_COMMAND for much slower but higher quality
OUTPUT_NAME = "video.webm" #outputs to this file name in same folder as source video
MAX_BITRATE = 2500000 #denoted in bps, default equal to 2500 kbps
MAX_WIDTH = 1280 #for 1280x720, enforces width to keep aspect ratio
FORCE_OVERWRITE = False #True if you want to overwrite without prompting

def out(command): #wrapper to run a command in shell and return output, used to get bitrate
    result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
    return result.stdout.strip()

def getPath():
    #Get input from user
    videoFolder = input("Please drag the folder onto this window and press enter:")
    #Get rid of surrounding quotes if path has spaces
    if videoFolder.startswith("\"") and videoFolder.endswith("\"") or videoFolder.startswith("'") and videoFolder.endswith("'"):
        videoFolder = videoFolder[1:-1]

    #Replace '\ ' with just a space
    videoFolder = videoFolder.replace(r"\ ", " ")
    return(videoFolder)

def getVideoFiles(): #uses glob to get all mp4 files in folder recursively
    videoFiles = glob.glob("./**/*.mp4", recursive=True)
    return(videoFiles)

def getBitrate(file): #uses ffprobe command to get bitrate of current file
    bitrate = out(BITRATE_COMMAND.format(file))
    return(min(int(bitrate), 2500000))

def convert(file): #converts using specified ffmpeg command
    oldDir = os.getcwd()
    os.chdir(file[0])
    bitrate = getBitrate(file[1])
    if(overwriteProtection()):
        out(CONVERT_COMMAND.format(file[1], MAX_WIDTH, bitrate, OUTPUT_NAME)) #actual conversion step
    os.chdir(oldDir)

def recursiveConvert(files):
    numFiles = len(files)
    for i in range(0,numFiles):
        curr = i+1
        file = os.path.split(files[i])
        #give user friendly output, ex. [1/43 2%] ./Tier 01 - Mic Check 1, 2/B.I - BE I
        print("[{0}/{1} {2}%] {3}".format(curr, numFiles, math.floor(curr / numFiles * 100), file[0]))
        convert(file) #do conversion

def overwriteProtection(): #If output file exists, ask before overwriting
    write = True
    if(not FORCE_OVERWRITE and os.path.isfile(OUTPUT_NAME)): #if file exists
        write = getBoolean("Would you like to overwrite this webm? [y/N] ")
    return(write)

def getBoolean(prompt):
    answer = input(prompt)
    return(answer.lower().startswith("y")) #default to no

def main():
    path = getPath()
    oldDir = os.getcwd()
    os.chdir(path)
    files = getVideoFiles()
    recursiveConvert(files)
    os.chdir(oldDir)

main()