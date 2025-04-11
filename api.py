from automation import InstagramAutomation
from flask import Flask, request, jsonify
from database import Database
from flask_cors import CORS
import subprocess
import os
import logging

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db = Database()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("api")

with app.app_context():
    db._init_db()

@app.teardown_appcontext
def close_connection(exception):
    db.close_connection(exception)

def get_connected_devices():
    try:
        result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
        devices = []
        lines = result.stdout.strip().split('\n')[1:]  # skip header
        for line in lines:
            if line.strip():
                device_id = line.split()[0]
                version_result = subprocess.run(
                    ['adb', '-s', device_id, 'shell', 'getprop', 'ro.build.version.release'],
                    capture_output=True, text=True
                )
                platform_version = version_result.stdout.strip()

                model_result = subprocess.run(
                    ['adb', '-s', device_id, 'shell', 'getprop', 'ro.product.model'],
                    capture_output=True, text=True
                )
                model = model_result.stdout.strip()

                devices.append({
                    'device_id': device_id,
                    'platform_version': platform_version,
                    'model': model
                })
        return devices
    except Exception as e:
        logger.error(f"Error getting devices: {str(e)}")
        return []
    
@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    device_id = request.form['device_id']
    local_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(local_path)

    subprocess.run(["adb", "-s", device_id, "push", local_path, "/sdcard/DCIM/"])
    subprocess.run([
        "adb", "-s", device_id, "shell", "am", "broadcast",
        "-a", "android.intent.action.MEDIA_SCANNER_SCAN_FILE",
        "-d", f"file:///sdcard/DCIM/{file.filename}"
    ])

    return jsonify({
        "message": "Upload and push successful",
        "device_path": f"/sdcard/DCIM/{file.filename}"
    })

@app.route('/devices/scan', methods=['POST'])
def scan_devices():
    devices = get_connected_devices()
    for device in devices:
        existing_device = db.get_device_by_id(device['device_id'])
        if not existing_device:
            db.insert_device(
                name=f"Android Device ({device['model']})",
                model=device['model'],
                device_id=device['device_id'],
                platform_version=device['platform_version']
            )

        automation = InstagramAutomation(device['device_id'])
        try:
            automation.connect()
            usernames = automation.get_instagram_accounts()
            for i, username in enumerate(usernames):
                db.insert_account(device['device_id'], username)

            # ✅ Définir le premier compte comme actif
            if usernames:
                db.set_active_account(device['device_id'], usernames[0])
                logger.info(f"✅ Compte actif défini pour {device['device_id']} : {usernames[0]}")
        except Exception as e:
            logger.warning(f"[{device['device_id']}] Impossible d’extraire les comptes : {e}")
        finally:
            automation.close()
    
    return jsonify({'message': 'Devices scanned successfully', 'devices': devices})


@app.route('/devices', methods=['GET'])
def get_devices():
    devices = db.get_devices()
    result = []
    for device in devices:
        accounts = db.get_accounts_by_device(device[5])
        result.append({
            'id': device[0],
            'name': device[1],
            'model': device[2],
            'status': device[3],
            'created_at': device[4],
            'device_id': device[5],
            'platform_version': device[6],
            'accounts': accounts
        })
    return jsonify(result)

@app.route('/posts', methods=['POST'])
def schedule_post():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON payload'}), 400

    post_id = db.add_post(
        device_id=data['device_id'],
        scheduled_time=data['scheduled_time'],
        media_path=data['media_path'],
        caption=data['caption'],
        post_type=data['post_type'],
        account=data.get('account')
    )
    return jsonify({'id': post_id, 'message': 'Post scheduled successfully'})

@app.route('/posts', methods=['GET'])
def get_posts():
    posts = db.get_all_posts()
    result = []
    for post in posts:
        post_id, device_id, scheduled_time, media_path, caption, post_type, account, status, created_at = post
        result.append({
            "id": post_id,
            "device_id": device_id,
            "scheduled_time": scheduled_time,
            "media_path": media_path,
            "caption": caption,
            "post_type": post_type,
            "account": account,
            "status": status,
            "created_at": created_at
        })
    return jsonify(result)

@app.route('/accounts', methods=['GET'])
def get_accounts():
    device_id = request.args.get('device_id')
    if not device_id:
        return jsonify({'error': 'Missing device_id'}), 400
    accounts = db.get_accounts_by_device(device_id)
    return jsonify(accounts)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
