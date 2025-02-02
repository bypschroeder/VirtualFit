import time
import uuid
import os
import io
import docker
from flask import Blueprint, jsonify, send_file, request, current_app
from minio.error import S3Error
from services.s3 import s3
from services.generate_3d_model import generate_model, shape_obj_smooth
from services.generate_preview_images import (
    get_files_by_gender,
    find_missing_previews,
    generate_preview_imgs,
    generate_presigned_urls,
)
from services.uptime import format_uptime
from services.validation import (
    validate_gender,
    validate_height,
    validate_image,
    validate_obj,
    validate_garment,
    validate_size,
    validate_quality,
)
from services.simulate_cloth import simulate_cloth

main = Blueprint("main", __name__)

client = docker.from_env()  # Docker client
server_start_time = time.time()  # Server start time


@main.route("/")
def index():
    current_time = time.time()
    uptime_seconds = int(current_time - server_start_time)
    uptime = format_uptime(uptime_seconds)

    status = "running"

    return jsonify({"status": status, "uptime": uptime})


@main.route("/generate-3d-model", methods=["POST"])
def generate_3d_model():
    try:
        # Form validation
        gender = validate_gender(request.form)
        if gender is None:
            current_app.logger.error("Invalid gender provided")
            return jsonify({"error:" "Invalid gender provided"})

        height = validate_height(request.form)
        if height is None:
            current_app.logger.error("Invalid height provided")
            return jsonify({"error:" "Invalid height"})

        image_file = validate_image(request.files)
        if image_file is None:
            current_app.logger.error("Invalid image file provided")
            return jsonify({"error": "Invalid image file provided"})

        # Generate UUID for folder
        folder_id = str(uuid.uuid4().hex)
        file_type = os.path.splitext(image_file.filename)[1]
        filename = f"image{file_type}"
        image_key = f"{folder_id}/{filename}"

        # Upload image to Minio
        image_data = io.BytesIO(image_file.read())
        s3.put_object(
            current_app.config["BUCKETS"][0],
            image_key,
            image_data,
            len(image_data.getvalue()),
        )

        # Generate 3D-Model
        if not generate_model(
            client, s3, current_app.config["BUCKETS"][0], image_key, gender, height
        ):
            current_app.logger.error("Failed to generate 3D-Model")
            return jsonify({"error": "Failed to generate 3D-Model"}), 400

        # Shape obj smooth
        obj_key = f"{folder_id}/model.obj"
        if not shape_obj_smooth(client, s3, current_app.config["BUCKETS"][0], obj_key):
            current_app.logger.error("Failed to shape smooth 3D-Model")
            return jsonify({"error": "Failed to shape smooth 3D-Model"}), 400

        smooth_obj_key = os.path.join(folder_id, "model_smooth.obj")
        smooth_obj_path = f"/tmp/model_smooth.obj"
        try:
            # Get smooth obj from Minio
            s3.fget_object(
                current_app.config["BUCKETS"][0], smooth_obj_key, smooth_obj_path
            )
        except S3Error as e:
            current_app.logger.error(f"Failed to download smooth obj: {e}")
            return jsonify({"error": f"Failed to download smooth obj: {e}"}), 500

        # Return smooth obj
        return send_file(smooth_obj_path, as_attachment=True)
    except Exception as e:
        current_app.logger.error(f"Unexpected error occurred: {e}")
        return jsonify({"error": e}), 500


@main.route("/generate-previews", methods=["POST"])
def generate_previews():
    # Form validation
    gender = validate_gender(request.form)
    if gender is None:
        current_app.logger.error("Invalid gender provided")
        return jsonify({"error": "Invalid gender provided"}), 400

    # Retrieve missing previews
    try:
        blend_files, preview_files = get_files_by_gender(
            current_app.config["BUCKETS"][1], gender, "L"
        )
        missing_previews = find_missing_previews(blend_files, preview_files)
    except Exception as e:
        current_app.logger.error(f"Failed to retrieve missing previews: {e}")
        return jsonify({"error": e}), 500

    # Return presigned URLs if no missing previews
    if not missing_previews:
        try:
            presigned_urls = generate_presigned_urls(preview_files)
        except Exception as e:
            current_app.logger.error(f"Failed to generate presigned URLs: {e}")
            return jsonify({"error": e}), 500

        return (
            jsonify(
                {
                    "message": "All previews are up-to-date",
                    "presigned_urls": presigned_urls,
                }
            ),
            200,
        )

    # Generate preview images
    if not generate_preview_imgs(
        client,
        current_app.config["BUCKETS"][1],
        missing_previews,
    ):
        current_app.logger.error("Failed to generate previews")
        return jsonify({"error": "Failed to generate previews"}), 500

    # Retrieve updated previews and generate presigned URLs
    updated_objects = s3.list_objects(current_app.config["BUCKETS"][1], recursive=True)
    previews = [
        obj.object_name
        for obj in updated_objects
        if obj.object_name.startswith("previews")
        and obj.object_name.endswith(".png")
        and os.path.basename(obj.object_name) == f"{gender}.png"
    ]
    presigned_urls = generate_presigned_urls(previews)

    return (
        jsonify(
            {
                "message": "Previews generated successfully",
                "presigned_urls": presigned_urls,
            }
        ),
        200,
    )


@main.route("/try-on", methods=["POST"])
def try_on():
    # Form validation
    obj_key = validate_obj(request.files, s3, current_app.config["BUCKETS"][0])
    if obj_key is None:
        current_app.logger.error("Invalid obj file provided")
        return jsonify({"error": "Invalid obj file provided"}), 400

    garment = validate_garment(request.form, s3, current_app.config["BUCKETS"][1])
    if garment is None:
        current_app.logger.error("Invalid garment provided")
        return jsonify({"error": "Invalid garment provided"}), 400

    gender = validate_gender(request.form)
    if gender is None:
        current_app.logger.error("Invalid gender provided")
        return jsonify({"error": "Invalid gender provided"}), 400

    size = validate_size(
        request.form, s3, current_app.config["BUCKETS"][1], garment, gender
    )
    if size is None:
        current_app.logger.error("Invalid size provided")
        return jsonify({"error": "Invalid size provided"}), 400

    quality = validate_quality(request.form)
    if quality is None:
        current_app.logger.error("Invalid quality provided")

    # Get garment key
    garment_upper_case = garment.replace("-", " ").title().replace(" ", "-")
    garment_key = f"{garment}/{gender}/{size}_{garment_upper_case}.blend"

    # Simulate cloth
    if not simulate_cloth(
        client,
        current_app.config["BUCKETS"][0],
        current_app.config["BUCKETS"][1],
        obj_key,
        garment_key,
        gender,
        quality,
    ):
        current_app.logger.error("Failed to simulate cloth")
        return jsonify({"error": "Failed to simulate cloth"}), 500

    # Get avatar with fitted garment
    file_name = f"{os.path.splitext(os.path.basename(garment_key))[0]}.obj"
    fit_obj_key = os.path.join(os.path.dirname(obj_key), file_name)
    fit_obj_path = os.path.join("tmp", file_name)

    s3.fget_object(current_app.config["BUCKETS"][0], fit_obj_key, fit_obj_path)

    # Return full obj of avatar and fitted garment
    return send_file(fit_obj_path, as_attachment=True), 200
