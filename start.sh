#!/bin/bash

init_rsrc
sudo mkdir /tmp/ramdisk
sudo chmod 777 /tmp/ramdisk
sudo mount -t tmpfs -o size=150G myramdisk /tmp/ramdisk

cp ~/twitter/source/*.mp4 /tmp/ramdisk