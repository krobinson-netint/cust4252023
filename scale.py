#!/bin/python3
from subprocess import Popen, getstatusoutput
from multiprocessing import Process
import argparse, re
import numpy as np

def getcmd(index):
    
    output1 = " /tmp/ramdisk/" + str(index) + "-1080p.mp4"
    output2 = " /tmp/ramdisk/" + str(index) + "-720p.mp4"
    output3 = " /tmp/ramdisk/" + str(index) + "-480p.mp4"
    output4 = " /tmp/ramdisk/" + str(index) + "-360p.mp4"

    # cmd=("ffmpeg -y -c:v h264_ni_quadra_dec -dec -1 -xcoder-params out=hw -i %s "
    #     " -filter_complex '[0:v]ni_quadra_split=4[out1][in2][in3][in4];[in2]ni_quadra_scale=1280:720[out2];[in3]ni_quadra_scale=854:480[out3];[in4]ni_quadra_scale=640:360[out4]'"
    #     " -map '[out1]' -c:v h265_ni_quadra_enc -enc -1 -xcoder-params RcEnable=1:RcInitDelay=2000 -b:v 3000000 %s "
    #     " -map '[out2]' -c:v h265_ni_quadra_enc -enc -1 -xcoder-params RcEnable=1:RcInitDelay=2000 -b:v 2000000 %s "
    #     " -map '[out3]' -c:v h265_ni_quadra_enc -enc -1 -xcoder-params RcEnable=1:RcInitDelay=2000 -b:v 1000000 %s "
    #     " -map '[out4]' -c:v h265_ni_quadra_enc -enc -1 -xcoder-params RcEnable=1:RcInitDelay=2000 -b:v 500000 %s " %(args.file, output1, output2, output3, output4) )

    cmd=("ffmpeg -y -c:v h264_ni_quadra_dec  -xcoder-params out=hw -i %s "
        " -filter_complex '[0:v]ni_quadra_split=4[out1][in2][in3][in4];[in2]ni_quadra_scale=1280:720[out2];[in3]ni_quadra_scale=854:480[out3];[in4]ni_quadra_scale=640:360[out4]'"
        " -map '[out1]' -c:v h265_ni_quadra_enc -xcoder-params RcEnable=1:RcInitDelay=2000 -b:v 3000000 %s "
        " -map '[out2]' -c:v h265_ni_quadra_enc -xcoder-params RcEnable=1:RcInitDelay=2000 -b:v 2000000 %s "
        " -map '[out3]' -c:v h265_ni_quadra_enc -xcoder-params RcEnable=1:RcInitDelay=2000 -b:v 1000000 %s "
        " -map '[out4]' -c:v h265_ni_quadra_enc -xcoder-params RcEnable=1:RcInitDelay=2000 -b:v 500000 %s " %(args.file, output1, output2, output3, output4) )


    # Add the output portion of the command
    cmd = cmd + " > " +  resultsfile(index) + " 2>&1 < /dev/null "
    return cmd

def resultsfile(index):
    return "/dev/shm/resultslog-" + str(index)

def launchCmd(index):
    cmd=getcmd(index)
    if args.dry is True:
        getstatusoutput(cmd)


def printresults():
    print("\n=============== Printing Results =====================\n")
    error = 0
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
            print("Instance %s no data " %(index))
            error += 1
    print ("error %s" %(str(error)))



    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--instances", help="How many instances are to be executed", default=1, type=int)
    parser.add_argument("-f", "--file", help="Source File", default="/tmp/ramdisk/scale.mp4", type=str)
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