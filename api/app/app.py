import docker
import os
import time
from flask import Flask, request, jsonify, send_file
from services.generate_3d_model import generate_keypoints, generate_mesh, shape_obj_smooth
from services.uptime import format_uptime

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

    return jsonify({
        "status": status,
        "uptime": uptime
    })

@app.route('/generate-3d-model', methods=['POST'])
def generate_3d_model():
    try:
        if "gender" not in request.form:
            return jsonify({'error': 'No gender provided'}), 400
        
        gender = request.form['gender']
        if gender not in ['male', 'neutral', 'female']:
            return jsonify({'error': 'Invalid gender provided'}), 400
        
        if "image" not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        image_file = request.files['image']

        if image_file.filename == '':
            return jsonify({'error': 'No image file provided'}), 400
        
        images_folder = os.path.join(app.config['DATA_FOLDER'], 'images')
        os.makedirs(images_folder, exist_ok=True)
        
        image_path = os.path.join(images_folder, "sample.jpg")
        image_file.save(image_path)

        if not generate_keypoints(
            client, 
            app.config['DATA_FOLDER'],
            app.config['VOLUME'],
            app.config['VOLUME_BIND']
        ):
            return jsonify({'error': 'Failed to generate keypoints'}), 400
        
        if not generate_mesh(
            gender,
            client, 
            app.config['DATA_FOLDER'],
            app.config['VOLUME'],
            app.config['VOLUME_BIND']
        ):
            return jsonify({'error': 'Failed to generate mesh'}), 400
        
        obj_folder = os.path.join(app.config['DATA_FOLDER'], 'smplify-x_results', 'meshes', 'sample')

        if not shape_obj_smooth(
            os.path.join(obj_folder, '000.obj'),
            client, 
            app.config['VOLUME'], 
            app.config['VOLUME_BIND']
        ):
            return jsonify({'error': 'Failed to shape smooth 3d Model'}), 400
    
        smooth_obj = os.path.join(obj_folder, '000_smooth.obj')

        if not os.path.exists(smooth_obj):
            return jsonify({'error': 'Failed to shape smooth 3d Model'}), 400
        
        try:
            os.remove(image_path)
        except Exception as e:
            print(f"Failed to cleanup temporary image file: {e}")

        return send_file(smooth_obj, as_attachment=True)
    except Exception as e:
        print(f"Unexpected error occurred: {e}")
        return jsonify({'error': e}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3000, debug=True)