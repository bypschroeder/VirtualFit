FROM linuxserver/blender:4.3.1

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-dev \
    python3-pip \
    git \
    wget && \
    apt-get clean

WORKDIR /vf_blender
COPY . /vf_blender/
