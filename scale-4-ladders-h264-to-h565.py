#!/bin/python3
from subprocess import Popen, getstatusoutput
from multiprocessing import Process
import argparse, re
import numpy as np

def getcmd(index):
    
    output1 = "/tmp/ramdisk/" + str(index) + "-1080p.mp4"
    output2 = "/tmp/ramdisk/" + str(index) + "-720p.mp4"
    output3 = "/tmp/ramdisk/" + str(index) + "-540p.mp4"
    output4 = "/tmp/ramdisk/" + str(index) + "-360p.mp4"

    cmd=("ffmpeg -y -c:v h264_ni_quadra_dec -xcoder-params out=hw:semiplanar0=1:enableOut1=1:semiplanar1=1:scale1=1280x720:enableOut2=1:semiplanar2=1:scale2=960x540 -i %s "
        "-filter_complex '[0:v]ni_quadra_split=1:1:2[1080p][720p][540p][540p_1];[540p_1]ni_quadra_scale=640x360[360p]' "
        "-map [1080p] -xcoder-params RcEnable=1 -b:v 3500000 -c:v h265_ni_quadra_enc -c:a copy %s "
        "-map [720p] -xcoder-params RcEnable=1 -b:v 1000000 -c:v h265_ni_quadra_enc -c:a copy %s "
        "-map [540p] -xcoder-params RcEnable=1 -b:v 800000 -c:v h265_ni_quadra_enc -c:a copy %s "
        "-map [360p] -xcoder-params RcEnable=1 -b:v 500000 -c:v h265_ni_quadra_enc -c:a copy %s " %(args.file, output1, output2, output3, output4) )

    # Add the output portion of the command
    cmd = cmd + " > " +  resultsfile(index) + " 2>&1 < /dev/null "
    return cmd

def resultsfile(index):
    return "/dev/shm/ffmpeglog-" + str(index)

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
            print("Instance %s no FPS data found " %(index))
    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--instances", help="How many instances are to be executed", default=1, type=int)
    parser.add_argument("-f", "--file", help="Source File", default="/tmp/ramdisk/scale.mp4", type=str)
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