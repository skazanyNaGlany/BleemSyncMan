# docker run -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix -v /home/sng/projects/bleemsyncman:/root -it debian:bleemsyncman /bin/bash

#FROM ubuntu:trusty
FROM ubuntu:xenial

RUN apt-get update
RUN apt-get install -y python3
RUN apt-get install -y python3-pip
RUN apt-get install -y python3-tk
RUN apt-get install -y python3-pil.imagetk
RUN apt-get install -y libarchive-dev
RUN apt-get install -y libjpeg-dev
RUN apt-get install -y zlib1g-dev

RUN pip3 install libarchive-c
RUN pip3 install pyunpack
RUN pip3 install patool
RUN pip3 install Pillow
RUN pip3 install cx_freeze
#RUN pip3 install pyinstaller

WORKDIR "/root"

ENTRYPOINT ["/bin/bash"]
