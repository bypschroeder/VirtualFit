# Docker setup for the VirtualFit Project

A Docker setup for VirtualFit including the frontend, backend, blender, hp3d, minio and nginx containers.

## Requirements

- https://docs.nvidia.com/cuda/wsl-user-guide/index.html
- https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html

## Usage

Before building or running the containers, make sure to look at the `README.md` (or `SETUP.md`) file in each folder for detailed instructions specific to each container.
**IMPORTANT**: For the `hp3d` container, you must download several required files and place them in the locations as specified in the `SETUP.md` file.

To build:

```bash
docker-compose --profile all build
```

To run :

```bash
docker-compose --profile app up -d
```

## Docker-compose info

### Profiles

- `all`: All containers
- `app`: Every container required for the VirtualFit app
- `tools`: Every tool container required for VirtualFit
- `proxy`: The nginx reverse proxy container

### Networks

- `app-network`: The network for the VirtualFit app

The network is required for every container that needs to access the minio server.

### Volumes

- `minio-data`: The volume for the minio server

### MinIO

The default MinIO credentials are `admin` and `password`. If you want to change them, you can do so by modifying the `MINIO_ROOT_USER` and `MINIO_ROOT_PASSWORD` environment variables in the `minio` container.

### Nginx

The nginx reverse proxy container is required for the VirtualFit app to work. Otherwise, the frontend cannot access the minio server.
The configuration file for the nginx container is located in the `nginx.conf` file in the root directory.

Domains:

- `localhost`: The VirtualFit app
- `minio.localhost`: The MinIO server (API)
- `console.localhost`: The MinIO server (Web-Console)
- `api.localhost`: The VirtualFit API
