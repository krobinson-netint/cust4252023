#!/bin/bash

ffmpeg -y -dec 0 -c:v h264_ni_quadra_dec -xcoder-params 'out=hw' -i source/roi_1080p-source.h264 \
-vf 'ni_quadra_roi=nb=./source/network_binary_yolov4_head.nb:qpoffset=-0.6' \
-enc 0 -c:v h264_ni_quadra_enc -xcoder-params 'roiEnable=1:RcEnable=1:bitrate=500000' -an roi_1080p-output.mp4
