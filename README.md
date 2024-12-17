# Docker setup for the VirtualFit Project

A Docker setup for VirtualFit, including OpenPose and SMPLify-X.

## Requirements
- https://docs.nvidia.com/cuda/wsl-user-guide/index.html
- https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html

## Usage

To build:
```bash
docker-compose build
```

To run :
```bash
docker-compose up backend
```

This only runs the backend which is crucial since the api starts the required containers with their commands.

Refer to the ``README.md`` file in each folder for detailed instructions specific to each container. 