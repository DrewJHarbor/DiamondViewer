"""
HARBOR Diamond Viewer - Web Server
Flask server with WebSocket for mobile control and customer sharing
"""

import os
import cv2
import time
import threading
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from src.arduino_controller import ArduinoController
from dotenv import load_dotenv
from twilio.rest import Client
import resend

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SESSION_SECRET', 'harbor-diamond-viewer-secret')

# Restrict CORS to local network only (more secure than '*')
# In production, customers will be on same WiFi network
CORS(app, origins=["http://localhost:*", "http://127.0.0.1:*", "http://192.168.*.*:*", "http://10.*.*.*:*"])
socketio = SocketIO(app, cors_allowed_origins=["http://localhost:*", "http://127.0.0.1:*", "http://192.168.*.*:*", "http://10.*.*.*:*"])

# Arduino controller instance
arduino = ArduinoController()

# Auto-rotation state
auto_rotation_active = False
auto_rotation_direction = 0

# Video capture state
video_recordings = {}


@app.route('/')
def index():
    """Landing page"""
    return "<h1>HARBOR Diamond Viewer</h1><p>Use the display viewer to scan QR codes</p>"


@app.route('/control')
def control_interface():
    """Mobile control interface"""
    return render_template('control.html')


@app.route('/share')
def share_interface():
    """Customer sharing interface"""
    return render_template('share.html')


@app.route('/api/status')
def get_status():
    """Get system status"""
    return jsonify({
        'arduino_connected': arduino.is_connected(),
        'auto_rotation': auto_rotation_active,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/video/record', methods=['POST'])
def start_video_recording():
    """Start 30-second video recording from top camera"""
    data = request.json
    session_id = data.get('session_id', str(int(time.time())))
    
    # Start recording in background thread
    thread = threading.Thread(target=record_video, args=(session_id,))
    thread.start()
    
    return jsonify({
        'status': 'recording_started',
        'session_id': session_id,
        'duration': 30
    })


@app.route('/api/video/<session_id>')
def get_video(session_id):
    """Retrieve recorded video"""
    video_path = f"recordings/{session_id}.mp4"
    if os.path.exists(video_path):
        return send_file(video_path, mimetype='video/mp4')
    return jsonify({'error': 'Video not found'}), 404


def record_video(session_id, duration=30):
    """Record video from top camera for specified duration"""
    os.makedirs('recordings', exist_ok=True)
    output_path = f"recordings/{session_id}.mp4"
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print(f"Error: Could not open camera for recording {session_id}")
        return
    
    # Get camera properties
    fps = 30
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Define codec and create VideoWriter
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    start_time = time.time()
    frame_count = 0
    
    while time.time() - start_time < duration:
        ret, frame = cap.read()
        if ret:
            out.write(frame)
            frame_count += 1
        else:
            break
    
    cap.release()
    out.release()
    
    video_recordings[session_id] = {
        'path': output_path,
        'duration': time.time() - start_time,
        'frames': frame_count,
        'timestamp': datetime.now().isoformat()
    }
    
    print(f"Recording complete: {session_id} ({frame_count} frames, {duration}s)")


# WebSocket events for real-time control
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    emit('status', {
        'arduino_connected': arduino.is_connected(),
        'auto_rotation': auto_rotation_active
    })


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')


@socketio.on('arduino_connect')
def handle_arduino_connect():
    """Connect to Arduino"""
    port = ArduinoController.find_arduino_port()
    if not port:
        ports = ArduinoController.list_available_ports()
        port = ports[0] if ports else None
    
    if port and arduino.connect(port):
        emit('arduino_status', {'connected': True, 'port': port})
    else:
        emit('arduino_status', {'connected': False, 'error': 'Connection failed'})


@socketio.on('move_axis')
def handle_move_axis(data):
    """Handle axis movement command"""
    axis = data.get('axis')  # 'X' or 'Y'
    direction = data.get('direction')  # 1 or -1
    
    if arduino.is_connected():
        arduino.move_axis(axis, direction)
        emit('command_sent', {'axis': axis, 'direction': direction})


@socketio.on('stop_axis')
def handle_stop_axis(data):
    """Handle stop axis command"""
    axis = data.get('axis')
    
    if arduino.is_connected():
        arduino.stop_axis(axis)
        emit('command_sent', {'axis': axis, 'action': 'stop'})


@socketio.on('rotate')
def handle_rotate(data):
    """Handle rotation command"""
    direction = data.get('direction')  # 1 (CW) or -1 (CCW)
    
    if arduino.is_connected():
        arduino.rotate(direction)
        emit('command_sent', {'action': 'rotate', 'direction': direction})


@socketio.on('stop_rotation')
def handle_stop_rotation():
    """Handle stop rotation command"""
    global auto_rotation_active
    auto_rotation_active = False
    
    if arduino.is_connected():
        arduino.stop_rotation()
        emit('command_sent', {'action': 'stop_rotation'})
        emit('auto_rotation_status', {'active': False})


@socketio.on('auto_rotate')
def handle_auto_rotate(data):
    """Handle auto-rotation (continuous rotation triggered by double-tap)"""
    global auto_rotation_active, auto_rotation_direction
    
    direction = data.get('direction', 1)
    auto_rotation_active = True
    auto_rotation_direction = direction
    
    if arduino.is_connected():
        arduino.auto_rotate(direction)  # Use new auto_rotate command
        emit('auto_rotation_status', {'active': True, 'direction': direction})


@socketio.on('heartbeat')
def handle_heartbeat():
    """Handle heartbeat from client"""
    if arduino.is_connected():
        arduino.send_command("PING")
    emit('heartbeat_ack', {'timestamp': datetime.now().isoformat()})


@app.route('/api/share', methods=['POST'])
def share_video():
    """Send video and GIA number via email/SMS"""
    data = request.json
    session_id = data.get('session_id')
    method = data.get('method', 'email')
    email = data.get('email')
    phone = data.get('phone')
    
    # Get video path
    video_path = f"recordings/{session_id}.mp4"
    if not os.path.exists(video_path):
        return jsonify({'error': 'Video not found'}), 404
    
    # TODO: GIA number detection (will be implemented in next task)
    gia_number = "GIA-PENDING"  # Placeholder
    
    # Build video URL (will be accessible via LattePanda's IP)
    video_url = f"http://{request.host}/api/video/{session_id}"
    
    try:
        # Send based on method
        if method == 'email' or method == 'both':
            if email:
                send_email(email, video_url, gia_number, session_id)
        
        if method == 'sms' or method == 'both':
            if phone:
                send_sms(phone, video_url, gia_number)
        
        return jsonify({
            'status': 'success',
            'session_id': session_id,
            'gia_number': gia_number,
            'video_url': video_url
        })
    
    except Exception as e:
        print(f"Error sharing video: {e}")
        return jsonify({'error': str(e)}), 500


def send_email(to_email, video_url, gia_number, session_id):
    """Send email with video link and GIA number using Resend"""
    try:
        resend_api_key = os.getenv('RESEND_API_KEY')
        email_from = os.getenv('EMAIL_FROM', 'noreply@harbordiamonds.com')
        
        if not resend_api_key:
            print(f"⚠️  EMAIL to {to_email}: Video={video_url}, GIA={gia_number}")
            print("⚠️  RESEND_API_KEY not configured - email not sent")
            return
        
        # Configure Resend
        resend.api_key = resend_api_key
        
        # Create email HTML
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #1a237e 0%, #3949ab 100%); color: white; padding: 30px; text-align: center; border-radius: 8px; }}
                .content {{ padding: 30px; background: #f5f5f5; border-radius: 8px; margin-top: 20px; }}
                .video-link {{ display: inline-block; background: #3949ab; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .gia-number {{ font-size: 24px; font-weight: bold; color: #1a237e; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🔷 HARBOR Diamond Viewer</h1>
                <p>Your Diamond Video is Ready</p>
            </div>
            <div class="content">
                <p class="gia-number">GIA Number: {gia_number}</p>
                <p>Thank you for viewing your diamond at HARBOR. Your video is now available:</p>
                <a href="{video_url}" class="video-link">📹 Watch Your Diamond Video</a>
                <p><small>Video ID: {session_id}</small></p>
                <p><small>This link will remain active for 30 days.</small></p>
            </div>
        </body>
        </html>
        """
        
        # Send email
        params = {
            "from": email_from,
            "to": [to_email],
            "subject": f"Your Diamond Video - GIA {gia_number}",
            "html": html_content,
        }
        
        email_response = resend.Emails.send(params)
        print(f"✅ EMAIL sent to {to_email}: Video={video_url}, GIA={gia_number}")
        print(f"   Email ID: {email_response['id']}")
        
    except Exception as e:
        print(f"❌ EMAIL ERROR: {e}")
        print(f"   Failed to send to {to_email}")


def send_sms(to_phone, video_url, gia_number):
    """Send SMS with video link and GIA number using Twilio"""
    try:
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        from_phone = os.getenv('TWILIO_PHONE_NUMBER')
        
        if not all([account_sid, auth_token, from_phone]):
            print(f"⚠️  SMS to {to_phone}: Video={video_url}, GIA={gia_number}")
            print("⚠️  Twilio credentials not configured - SMS not sent")
            return
        
        # Initialize Twilio client
        client = Client(account_sid, auth_token)
        
        # Create SMS message
        message_body = f"""HARBOR Diamond Viewer

GIA: {gia_number}

Watch your diamond video:
{video_url}

Thank you for visiting HARBOR"""
        
        # Send SMS
        message = client.messages.create(
            body=message_body,
            from_=from_phone,
            to=to_phone
        )
        
        print(f"✅ SMS sent to {to_phone}: Video={video_url}, GIA={gia_number}")
        print(f"   Message SID: {message.sid}")
        
    except Exception as e:
        print(f"❌ SMS ERROR: {e}")
        print(f"   Failed to send to {to_phone}")


def start_web_server():
    """Start the web server (can be called from display viewer or standalone)"""
    # Create recordings directory
    os.makedirs('recordings', exist_ok=True)
    
    # Run server in production mode with eventlet for better Socket.IO performance
    print("Starting HARBOR Diamond Viewer Web Server...")
    print("Control interface: http://<your-ip>:5000/control")
    print("Share interface: http://<your-ip>:5000/share")
    print("\nSECURITY: This server should only be accessible on your local WiFi network")
    print("Ensure proper network isolation (firewall, WiFi password protection)")
    
    # Production mode: debug=False, use eventlet async mode
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=False)


if __name__ == '__main__':
    start_web_server()
