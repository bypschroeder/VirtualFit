# Setup for HierarchicalProbabilistic3DHuman Repository

This is an easy setup guide for the HierarchicalProbabilistic3DHuman repository as a Docker container for the VirtualFit project.

## Installation

### Files

- Download the SMPL models from [here](https://www.dropbox.com/scl/fi/p1xuul5b3vtsx5fpgn20n/smpl.zip?rlkey=9z677uohvn5uqel0h569jtqm7&st=jlxsfv3m&dl=0)
- Download the pre-trained models and the model checkpoint from [here](https://drive.google.com/drive/folders/1WHdbAaPM8-FpnwMuCdVEchskgKab3gel?usp=sharing)

Place the Files like this:

    hp3d
    ├── model_files                                  # Folder with model files
    │   ├── smpl
    │   │   ├── SMPL_NEUTRAL.pkl                     # Gender-neutral SMPL model
    │   │   ├── SMPL_MALE.pkl                        # Male SMPL model
    │   │   ├── SMPL_FEMALE.pkl                      # Female SMPL model
    │   ├── poseMF_shapeGaussian_net_weights.tar     # Pose/Shape distribution predictor checkpoint
    │   ├── pose_hrnet_w48_384x288.pth               # Pose2D HRNet checkpoint
    │   ├── cocoplus_regressor.npy                   # Cocoplus joints regressor
    │   ├── J_regressor_h36m.npy                     # Human3.6M joints regressor
    │   ├── J_regressor_extra.npy                    # Extra joints regressor
    │   └── UV_Processed.mat                         # DensePose UV coordinates for SMPL mesh
    └── ...

### Docker

Running hp3d standalone

```bash
docker build -t {image_name} .
docker run -e NVIDIA_VISIBLE_DEVICES=all \
  -e MINIO_ENDPOINT={minio_endpoint} \
  -e MINIO_ACCESS_KEY={minio_access_key} \
  -e MINIO_SECRET_KEY={minio_secret_key} \
  --network {network_name} \
  --runtime=nvidia \
  -d {image_name}
```

or with docker-compose

```bash
docker-compose build hp3d
docker-compose up -d hp3d
```

Running the whole VirtualFit-App

```bash
docker-compose --profile all build
docker-compose --profile app up -d
```

## Usage

To simply run a prediction on images, you can run the following command:

```bash
python3 run_predict.py --gender <gender> --pose_shape_weights <path_to_pose_shape_weights> --image_dir <path_to_image_dir> --save_dir <path_to_save_dir> --height <height> --export_obj
```

For example, this runs the prediction on the images in the `images` folder with the gender `male` and saves the results in the `output` folder:

```bash
python3 run_predict.py --gender male --pose_shape_weights model_files/poseMF_shapeGaussian_net_weights_male.tar --image_dir images --save_dir output --height 1.75 --export_obj
```

### MinIO Helper Script

The `fetch_and_predict.py` script is a helper script for fetching images from MinIO and running the prediction on them. It can be used as follows:

```bash
python3 fetch_and_predict.py <bucket_name> <image_key> <gender> <height>
```

For example, this fetches the image with the key `image.jpg` from the bucket `my_bucket` and runs the prediction on it with the gender `male` and height `1.75`:

```bash
python3 fetch_and_predict.py my_bucket image.jpg male 1.75
```

The generated obj gets uploaded to the same folder where the image was stored named `model.obj`.

## Code Adjustments

- The `fetch_and_predict.py` script is a helper script for fetching images from MinIO and running the prediction on them.
- Added arguments for --height and --export_obj to scale to real height and export to .obj file
- Added height and export_obj arguments to run_predict function in `run_predict.py`
- Added export_obj argument to predict_poseMF_shapeGaussian_net function in `predict_poseMF_shapeGaussian_net.py`
- Added `save_mesh_as_obj` and `scale_smpl_to_real_height` functions in `predict/predict_poseMF_shapeGaussian_net.py`
- Added `neutral_vertices` to scale the `posed_vertices` to real height within the `predict_poseMF_shapeGaussian_net` function
- Added the export to obj option to the `predict_poseMF_shapeGaussian_net` function
