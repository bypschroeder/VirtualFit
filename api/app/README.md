# Flask API Docker image for VirtualFit

A Docker image for the Flask API for VirtualFit.

## Installationn

### Running the API standalone

```bash
docker build -t {image_name} .
docker run -p 3000:3000 \
  -e MINIO_ENDPOINT={minio_endpoint} \
  -e MINIO_ACCESS_KEY={minio_access_key} \
  -e MINIO_SECRET_KEY={minio_secret_key} \
  -v /var/run/docker.sock:/var/run/docker.sock \
  --network {network_name} \
  -d {image_name}
```

or with docker-compose

```bash
docker-compose build backend
docker-compose up -d backend
```

### Running the whole VirtualFit-App

```bash
docker-compose --profile all build
docker-compose --profile app up -d
```

## Usage

The API is accessible at `http://localhost:3000/` or via `api.localhost` through the nginx reverse proxy (nginx container needs to run). For optimal usage, it is recommended to use the nginx proxy URL (`api.localhost`)

### API Endpoints

- `/`: Returns the uptime of the API
  - Method: `GET`
- `/generate-3d-model`: Generates a 3D model from a given image
  - Method: `POST`
  - Body:
    - `image`: The image to generate the 3D model from
    - `gender`: The gender of the person in the image (male or female)
    - `height`: The height of the person in the image in meters (e.g 1.75)
  - Returns:
    - file: The 3D model as an OBJ file
- `/generate-previews`: Generates preview images for the available garments
  - Method: `POST`
  - Body:
    - `gender`: The gender of the person the garments are for (male or female)
  - Returns:
    - `message`: Status message
    - `presigned_urls`: A list of presigned URLs for the generated preview images
- `/try-on`: Fits an garment to the generated 3D model
  - Method: `POST`
  - Body:
    - `obj`: The 3D model as an OBJ file to fit the garment to
    - `garment`: The garment to try on. Currently only `t-shirt`, `sweatshirt` and `hoodie` are supported
    - `gender`: The gender of the person the garment is for (male or female)
    - `size`: The size of the garment to try on (currently only XS - XXL)
  - Returns:
    - `obj`: The presigned URL for the fitted .obj file
    - `mtl`: The presigned URL for associated .mtl file

## Notes

- The container needs to be run with the `/var/run/docker.sock:/var/run/docker.sock` volume since it needs access to the docker daemon to run the other containers.
- The container needs to be run in the same network as the other containers to access the minio server.
- The container needs to be run with the MINIO environment variables to be able to access it
