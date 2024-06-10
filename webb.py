from flask import Flask, render_template, request, redirect, url_for,Response,jsonify
from pymongo import MongoClient
import base64
from ultralytics import YOLO
import requests
import cv2
from flask import flash
app = Flask(__name__)
app.static_folder = 'static'
client = MongoClient("mongodb://localhost:27017/")
db = client["third_eye"]
collection = db["users"]
detected_objects_collection = db['detected_objects']
qnt_collection = db['questions']

app = Flask(__name__)

# Load YOLO model (assuming "yolov8n.pt" is in the same directory)
model = YOLO("yolov8n.pt")

video_url = "http://192.168.137.123:4747/video"

# Create VideoCapture object with the URL
cap = cv2.VideoCapture(video_url)


# Start webca

# Object classes (modify according to your YOLOv8n.pt model)
classNames = ["person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat",
              "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
              "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella",
              "handbag", "tie", "suitcase", "frisbee", "spipkis", "snowboard", "sports ball", "kite", "baseball bat",
              "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
              "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli",
              "carrot", "hot dog", "pizza", "donut", "cake", "chair", "sofa", "pottedplant", "bed",
              "diningtable", "toilet", "tvmonitor", "laptop", "mouse", "remote", "keyboard", "cell phone",
              "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors",
              "teddy bear", "hair drier", "toothbrush"]  # ... (list all classes)




# Global variable to keep track of the total number of entries
total_entries = 0


    
    
def save_detected_objects(objects):
    # Check if there are at least two persons or a cellphone or a book detected
    person_count = sum(1 for obj in objects if obj['label'] == 'person')
    cellphone_count = sum(1 for obj in objects if obj['label'] == 'cell phone')
    book_count = sum(1 for obj in objects if obj['label'] == 'book')
    
    if person_count >= 2 or cellphone_count > 0 or book_count > 0:
        # Insert detected objects into the database
        return jsonify({'warning': 'Don\'t Cheat'})

    detected_objects_collection.insert_many(objects)


import cv2
import numpy as np
import requests
from flask import Flask, render_template, Response, jsonify

app = Flask(__name__)

# Load YOLO model (assuming "yolov8n.pt" is in the same directory)
model = YOLO("yolov8n.pt")

video_url = "http://192.168.137.123:4747/video"

def gen_frames():
    while True:
        try:
            # Fetch video frame from the URL
            response = requests.get(video_url)
            img_array = np.frombuffer(response.content, dtype=np.uint8)
            frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

            if frame is not None:
                detected_objects = []  # List to store detected objects
                
                # Perform object detection
                results = model(frame, stream=True)

                # Process detection results and add labels
                for r in results:
                    boxes = r.boxes
                    for box in boxes:
                        cls = int(box.cls[0])  # Get the class index
                        label = classNames[cls]  # Get the corresponding label
                        
                        # Check if the detected object is person, book, or cell phone
                        if label.lower() in ['person', 'book', 'cell phone']:
                            x1, y1, x2, y2 = box.xyxy[0]
                            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                            
                            # Append detected object information to the list
                            detected_objects.append({
                                'label': label,
                                'bounding_box': {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2}
                            })

                # Check for alert condition and get response
                alert_response = save_detected_objects(detected_objects)

                # If there's an alert response, yield it to trigger the alert message in the frontend
                if alert_response:
                    yield alert_response
                else:
                    # If no alert, continue processing frames
                    ret, buffer = cv2.imencode('.jpg', frame)
                    frame = buffer.tobytes()
                    yield (b'--frames\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            else:
                # If frame capture fails, break the loop
                break
        except Exception as e:
            print("Error:", e)
            continue

# Now use this gen_frames function as before in your Flask app

            # Save detected objects to the database
        
@app.route('/')
def login():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login_post():
    username = request.form.get("username")
    password = request.form.get("password")

    # Basic validation (improve security in production)
    if not username or not password:
        return render_template("login.html", error="Please enter username and password.")

    # Fetch user from database
    user = collection.find_one({"username": username})

    # Check if user exists and password matches (hashed passwords recommended in production)
    if user and user["password"] == password:
        # Successful login, redirect to guideline page
        return redirect(url_for("guidelines"))
    else:
        return render_template("login.html", error="Invalid username or password.")

@app.route("/guidelines")
def guidelines():
    return render_template("guidelines.html")

@app.route('/save_snapshot', methods=['POST'])
def save_snapshot():
    try:
        # Get the data URL of the snapshot from the request JSON
        data_url = request.json.get('image')

        # Remove the prefix from the data URL
        img_data = data_url.split(',')[1]

        # Decode the base64 image data
        img_binary = base64.b64decode(img_data)

        # Write the image binary to a file
        with open(r'D:\snapshot\snapshot.jpg', 'wb') as f:
            f.write(img_binary)

        return 'Snapshot saved successfully!', 200
    except Exception as e:
        print('Error saving snapshot:', e)
        return 'Failed to save snapshot!', 500

    return "Snapshot saved successfully!", 200

@app.route("/submit_guidelines", methods=["POST"])
def submit_guidelines():
    # Handle submission of guidelines form here
    # For example, you can save the form data to the database
    # Or perform any other necessary actions
    # Then redirect to the capture image page
    return redirect(url_for("capture_image"))

@app.route("/capture_image")
def capture_image():
    return render_template("cap_img.html")

@app.route("/prep.html")
def prep():
    return render_template("prep.html")
@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/qnt', methods=['GET'])
def index():
    return render_template("archa.html")
   
camera = cv2.VideoCapture(0) 
def generate_frames():
    while True:
        succes, frame = camera.read()
        if not succes:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
@app.route('/video_feeds')
def video_feeds():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
   

@app.route('/fetch_questions', methods=['GET'])
def fetch_questions():
    questions = list(qnt_collection.find({}, {'_id': 0}))
    return jsonify(questions)


@app.route('/tqpage.html')
def tq():
    return render_template("tqpage.html")



if __name__ == "__main__":
    app.run(debug=True)
