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
    get_files_by_gender,
    find_missing_previews,
    generate_preview_imgs,
    generate_presigned_urls,
)
from services.uptime import format_uptime
from services.s3 import s3, create_buckets, BUCKETS_TO_CREATE
from services.init_data import upload_data
from services.validation import (
    validate_gender,
    validate_image,
    validate_obj,
    validate_garment,
    validate_size,
)
import io
from services.simulate_cloth import simulate_cloth


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
        gender = validate_gender(request.form)
        if gender is None:
            return jsonify({"error:" "Invalid gender provided"})

        image_file = validate_image(request.files)
        if image_file is None:
            return jsonify({"error": "Invalid image file provided"})

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
    gender = validate_gender(request.form)
    if gender is None:
        return jsonify({"error": "Invalid gender provided"}), 400

    try:
        blend_files, preview_files = get_files_by_gender(gender)
        missing_previews = find_missing_previews(blend_files, preview_files)
    except Exception as e:
        print(f"Failed to retrieve missing previews: {e}")
        return jsonify({"error": e}), 500

    if not missing_previews:
        try:
            presigned_urls = generate_presigned_urls(preview_files)
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


@app.route("/try-on", methods=["POST"])
def try_on():
    obj_key = validate_obj(request.files, s3, BUCKETS_TO_CREATE[0])
    if obj_key is None:
        return jsonify({"error": "Invalid obj file provided"}), 400

    garment = validate_garment(request.form, s3, BUCKETS_TO_CREATE[1])
    if garment is None:
        return jsonify({"error": "Invalid garment provided"}), 400

    gender = validate_gender(request.form)
    if gender is None:
        return jsonify({"error": "Invalid gender provided"}), 400

    size = validate_size(request.form, s3, BUCKETS_TO_CREATE[1], garment, gender)
    if size is None:
        return jsonify({"error": "Invalid size provided"}), 400

    garment_upper_case = garment.replace("-", " ").title().replace(" ", "-")
    garment_key = f"{garment}/{gender}/{size}_{garment_upper_case}.blend"

    if not simulate_cloth(
        client,
        BUCKETS_TO_CREATE[0],
        BUCKETS_TO_CREATE[1],
        obj_key,
        garment_key,
        gender,
    ):
        return jsonify({"error": "Failed to simulate cloth"}), 500

    file_name = f"{os.path.splitext(os.path.basename(obj_key))[0]}_{os.path.splitext(os.path.basename(garment_key))[0]}.obj"
    fit_obj_key = os.path.join("fits", file_name)
    fit_obj_path = os.path.join("tmp", file_name)

    s3.fget_object(BUCKETS_TO_CREATE[0], fit_obj_key, fit_obj_path)

    return send_file(fit_obj_path, as_attachment=True), 200


if __name__ == "__main__":
    create_buckets()
    upload_data(s3, BUCKETS_TO_CREATE[1], "./init_data/models")
    app.run(host="0.0.0.0", port=3000, debug=True)
