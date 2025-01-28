FROM nvidia/cuda:11.6.1-cudnn8-devel-ubuntu20.04

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /HP3D
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-dev \
    python3-pip \
    gcc \
    g++ \
    wget \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 && \
    apt-get clean

COPY . /HP3D/

RUN pip3 install networkx==3.1 numpy==1.23.1 chumpy minio
RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
RUN pip3 install -r requirements.txt

RUN pip3 install --extra-index-url https://miropsota.github.io/torch_packages_builder pytorch3d==0.7.8+pt2.4.1cu118

RUN mkdir -p /root/.cache/torch/hub/checkpoints
RUN wget -O /root/.cache/torch/hub/checkpoints/maskrcnn_resnet50_fpn_coco-bf2d0c1e.pth https://download.pytorch.org/models/maskrcnn_resnet50_fpn_coco-bf2d0c1e.pth