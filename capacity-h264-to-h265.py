#!/bin/python3
from subprocess import Popen, getstatusoutput
from multiprocessing import Process
import argparse, re
import numpy as np

def getcmd(index):
    cmd=("ffmpeg -y -c:v h264_ni_quadra_dec -xcoder-params 'out=hw' -i %s -c:v h265_ni_quadra_enc -xcoder-params RcEnable=1 -b:v 5000000 -c:a copy" %(args.file))

    # Add the output portion of the command
    cmd = cmd + outputfile(index) + " > " +  resultsfile(index) + " 2>&1 < /dev/null "
    return cmd

def outputfile(index):
    pos = args.output.find(".")
    return " /tmp/ramdisk/" + args.output[:pos] + str(index) + args.output[pos:]

def resultsfile(index):
    return "/dev/shm/ffmpeglog-" + str(index)

def launchCmd(index):
    cmd=getcmd(index)
    if args.dry is True:
        getstatusoutput(cmd)

def printresults():
    print("\n=============== Printing Results =====================\n")
    ignore = 1
    for index in range(instances):
        resultsfilename = resultsfile(index)
        with open(resultsfilename, "r") as file_open:
            fps_results = np.array([])
            for line in file_open:
                if re.search("fps=", line):
                    lastline = line                                         # used to fine the last entry in the file
                    fps = line.partition("fps=")[2][0:3]                    # looks for 'fps=' and returns only the value and stips everything before and after
                    fps_results = np.append(fps_results,int(float(fps)))    # puts the value into an array, converts the string->float->integer

        if len(fps_results) > ignore:
            fps_results_avg = int(np.mean(fps_results[ignore:]))
            speed = lastline.partition("speed=")[2][0:5]
            print("Instance %s had an average FPS of %s with a reported FFmpeg speed of %s " %(index, fps_results_avg, speed))
        else:
            print("Instance %s no FPS data found " %(index))
    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--instances", help="How many instances are to be executed", default=1, type=int)
    parser.add_argument("-f", "--file", help="Source File", default="/tmp/ramdisk/capacity.mp4", type=str)
    parser.add_argument("-o", "--output", help="Output format, defaults to filename<instances>.mp4", default="output.mp4", type=str)
    parser.add_argument("--dry", help="do not run the ffmpeg command", action="store_false")

    args = parser.parse_args()
    
    instances = args.instances

    processes = [Process(target=launchCmd, args=(i,)) for i in  range(instances)]

    for index, process in enumerate(processes):
        process.start()
        print("Instance %s: %s" % (index, getcmd(index)))
    for index, process in enumerate(processes):
        process.join()
        #print("process join")
    
    printresults()