import docker
import os
import time
import uuid
from flask import Flask, request, jsonify, send_file
from services.generate_3d_model import (
    generate_keypoints,
    generate_mesh,
    shape_obj_smooth,
)
from services.generate_preview_images import (
    move_blend_to_volume,
    get_missing_previews,
    generate_preview_imgs,
)
from services.uptime import format_uptime
from services.s3 import s3, create_buckets, BUCKETS_TO_CREATE
from services.init_data import upload_data
import io
from datetime import timedelta


app = Flask(__name__)
client = docker.from_env()
app.config.from_object("config")
server_start_time = time.time()


@app.route("/")
def index():
    current_time = time.time()
    uptime_seconds = int(current_time - server_start_time)
    uptime = format_uptime(uptime_seconds)

    status = "running"

    return jsonify({"status": status, "uptime": uptime})


@app.route("/generate-3d-model", methods=["POST"])
def generate_3d_model():
    try:
        if "gender" not in request.form:
            return jsonify({"error": "No gender provided"}), 400

        gender = request.form["gender"]
        if gender not in ["male", "neutral", "female"]:
            return jsonify({"error": "Invalid gender provided"}), 400

        if "image" not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        image_file = request.files["image"]

        if image_file.filename == "":
            return jsonify({"error": "No image file provided"}), 400

        file_id = str(uuid.uuid4().hex)
        file_type = os.path.splitext(image_file.filename)[1]
        filename = f"{file_id}{file_type}"
        image_key = f"images/{filename}"

        image_data = io.BytesIO(image_file.read())

        s3.put_object(
            BUCKETS_TO_CREATE[0], image_key, image_data, len(image_data.getvalue())
        )

        if not generate_keypoints(client, s3, BUCKETS_TO_CREATE[0], image_key):
            return jsonify({"error": "Failed to generate keypoints"}), 400

        base_image_name = os.path.splitext(os.path.basename(image_key))[0]
        keypoints_key = f"keypoints/{base_image_name}_keypoints.json"

        if not generate_mesh(
            client, s3, BUCKETS_TO_CREATE[0], image_key, keypoints_key, gender
        ):
            return jsonify({"error": "Failed to generate mesh"}), 400

        obj_key = f"output/{base_image_name}.obj"

        if not shape_obj_smooth(client, s3, BUCKETS_TO_CREATE[0], obj_key):
            return jsonify({"error": "Failed to shape smooth 3d Model"}), 400

        smooth_obj_key = f"output/{base_image_name}_smooth.obj"
        smooth_obj_path = f"/tmp/{base_image_name}_smooth.obj"
        s3.fget_object(BUCKETS_TO_CREATE[0], smooth_obj_key, smooth_obj_path)

        return send_file(smooth_obj_path, as_attachment=True)
    except Exception as e:
        print(f"Unexpected error occurred: {e}")
        return jsonify({"error": e}), 500


@app.route("/generate-previews", methods=["POST"])
def generate_previews():
    if "gender" not in request.form:
        return jsonify({"error": "No gender provided"}), 400

    gender = request.form["gender"]
    if gender not in ["male", "neutral", "female"]:
        return jsonify({"error": "Invalid gender provided"}), 400

    try:
        objects = list(s3.list_objects(BUCKETS_TO_CREATE[1], recursive=True))
        blend_files = [
            obj.object_name
            for obj in objects
            if obj.object_name.endswith(".blend")
            and os.path.basename(obj.object_name).startswith("L_")
            and obj.object_name.split("/")[1] == gender
        ]
        preview_files = [
            obj.object_name
            for obj in objects
            if obj.object_name.startswith("previews")
            and obj.object_name.endswith(".png")
            and os.path.basename(obj.object_name) == f"{gender}.png"
        ]

        missing_previews = []
        for blend_file in blend_files:
            clothing = blend_file.split("/")[0]
            gender = blend_file.split("/")[1]
            preview_file = f"previews/{clothing}/{gender}.png"

            if preview_file not in preview_files:
                missing_previews.append(blend_file)
    except Exception as e:
        print(f"Failed to retrieve missing previews: {e}")
        return jsonify({"error": e}), 500

    if not missing_previews:
        try:
            expiration_time = timedelta(minutes=10)
            presigned_urls = [
                s3.presigned_get_object(
                    BUCKETS_TO_CREATE[1], file_path, expiration_time
                )
                for file_path in preview_files
            ]
            external_url_base = "http://minio.localhost"
            presigned_urls = [
                url.replace("http://minio:9000", external_url_base)
                for url in presigned_urls
            ]
        except Exception as e:
            print(f"Failed to generate presigned URLs: {e}")
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

    # TODO: Funktioniert, allerdings sehr langsam
    if not generate_preview_imgs(
        client,
        BUCKETS_TO_CREATE[1],
        missing_previews,
    ):
        return jsonify({"error": "Failed to generate previews"}), 500

    updated_objects = s3.list_objects(BUCKETS_TO_CREATE[1], recursive=True)
    previews = [
        obj.object_name
        for obj in updated_objects
        if obj.object_name.startswith("previews")
        and obj.object_name.endswith(".png")
        and os.path.basename(obj.object_name) == f"{gender}.png"
    ]

    expiration_time = timedelta(minutes=10)
    presigned_urls = [
        s3.presigned_get_object(BUCKETS_TO_CREATE[1], file_path, expiration_time)
        for file_path in previews
    ]
    external_url_base = "http://minio.localhost"
    presigned_urls = [
        url.replace("http://minio:9000", external_url_base) for url in presigned_urls
    ]

    return (
        jsonify(
            {
                "message": "Previews generated successfully",
                "presigned_urls": presigned_urls,
            }
        ),
        200,
    )


@app.route("/try-on", methods=["POST"])
def try_on():
    pass


if __name__ == "__main__":
    create_buckets()
    upload_data(s3, BUCKETS_TO_CREATE[1], "./init_data/models")
    app.run(host="0.0.0.0", port=3000, debug=True)
