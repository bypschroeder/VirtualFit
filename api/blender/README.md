# Blender Docker Image for VirtualFit

A Docker image for running Blender Python scripts for VirtualFit.

## Insallation

### Running Blender standalone

```bash
docker build -t {image_name} .
docker run -p 3000:3000 \
  -e MINIO_ENDPOINT={minio_endpoint} \
  -e MINIO_ACCESS_KEY={minio_access_key} \
  -e MINIO_SECRET_KEY={minio_secret_key} \
  -e NVIDIA_VISIBLE_DEVICES=all \
  --network {network_name} \
  --runtime=nvidia \
  -d {image_name}
```

or with docker-compose

```bash
docker-compose build blender
docker-compose up -d blender
```

### Running the whole VirtualFit-App

```bash
docker-compose --profile all build
docker-compose --profile app up -d
```

## Usage

To use the blender scripts, you can run simply run the following commands. However, there are helper scripts available in the `minio_helpers` folder for each use case. These scripts handle fetching and uploading files from the MinIO server and automatically execute the appropriate blender script.

### Blender Scripts

- Shade an obj smooth: `blender -b -P shade_smooth.py -- --obj <path_to_obj>`
- Generate preview image for garment: `blender -b -P generate_preview.py -- --blend <path_to_blend_file> --output <path_to_output_folder>`
- Fit garment to avatar object: `blender -b -P fit_clothes.py -- --gender <gender> --obj <path_to_obj> --garment <path_to_garment_blend_file> --output <path_to_output_folder>`

### Helper Scripts

- Fetch generated obj from hp3d and shade smooth: `python3 ./minio_helpers/fetch_shade_smooth.py <bucket_name> <obj_key>`
- Fetch garments and preview images and generate presigned URLs: `python3 ./minio_helpers/fetch_generate_preview.py <bucket_name> <missing_previews>`
- Fetch garment/avatar and fit garment to avatar: `python3 ./minio_helpers/fetch_try_on.py <obj_bucket_name> <garment_bucket_name> <obj_key> <garment_key> <gender>`

## Notes

- The container needs to be run with NVIDIA GPU support. This can be done by adding `--runtime=nvidia` and `-e NVIDIA_VISIBLE_DEVICES=all` to the docker run command.
- The container needs to be run in the same network as the other containers to access the minio server.
- The container needs to be run with the MinIO environment variables to be able to access it
- The `<missing_previews>` argument for the `fetch_generate_preview`.py script containing the paths of all blend_files, seperated by commas. Inside the script, this string is split into a list of blend file paths by seperating it at each comma.
- The container must be run with an overwritten entrypoint to set the environment variables correctly. To achieve this add `entrypoint: "/bin/bash"` to the python run command and put `-c '{python_command}'` as the command to run. Otherwise the helper script cannot access the environment variables for the minio server.
- The container must be run with an overridden entrypoint to ensure the environment variables can be accessed correctly. To do this, add `entrypoint: "/bin/bash"` to the Python run command and include `-c '{python_command}'` as the command to execute. Without this, the helper script will not be able to access the MinIO server.
