from flask import Flask, render_template, Response
import cv2
import numpy as np
import face_recognition
import os
from flask import Flask, render_template, request, redirect, url_for,Response,jsonify
from pymongo import MongoClient
import base64
from ultralytics import YOLO
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

model = YOLO("yolov8n.pt")

video_url = "http://192.168.29.219:4747/video"

# Create VideoCapture object with the URL
capture = cv2.VideoCapture(video_url)


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
        detected_objects_collection.insert_many(objects)


def gen_frames_obj():
    capture = cv2.VideoCapture(video_url)
    while True:
        success, img = capture.read()

        if success:
            detected_objects = []  # List to store detected objects
            
            # Perform object detection
            results = model(img, stream=True)

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

            # Save detected objects to the database
            save_detected_objects(detected_objects)

            # Encoding the frame to JPEG and yielding it
            ret, buffer = cv2.imencode('.jpg', img)
            frame = buffer.tobytes()
            yield (b'--frames\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
capture.release()

# Function to load reference encoding
def load_reference_encoding():
    reference_image_path = "D:/snapshot"  # Path to directory containing reference image
    reference_image_files = os.listdir(reference_image_path)
    # Filter out directories from the list of files
    reference_image_files = [file for file in reference_image_files if os.path.isfile(os.path.join(reference_image_path, file))]
    if not reference_image_files:
        print("Error: No reference image found in the directory.")
        return None
    reference_image_file = os.path.join(reference_image_path, reference_image_files[0])
    reference_image = face_recognition.load_image_file(reference_image_file)
    return face_recognition.face_encodings(reference_image)[0]

reference_encoding = load_reference_encoding()

def gen_frames():
    cap = cv2.VideoCapture(0)
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            # Convert the frame to RGB for face recognition
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Find all face locations and encodings in the frame
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            for face_location, face_encoding in zip(face_locations, face_encodings):
                # Compare current face encoding with the reference encoding
                is_same_person = face_recognition.compare_faces([reference_encoding], face_encoding)[0]
                # Draw a rectangle around the face and display text indicating whether it's the same person
                color = (0, 255, 0) if is_same_person else (0, 0, 255)
                cv2.rectangle(frame, (face_location[3], face_location[0]), (face_location[1], face_location[2]), color, 2)
                cv2.putText(frame, "Same Person" if is_same_person else "Different Person", (face_location[3], face_location[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            # Encoding the frame to JPEG and yielding it
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frames\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


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
            
@app.route('/video_feed_object')
def video_feed_object():
    return Response(gen_frames_obj(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed_face')
def video_feed_face():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
   

@app.route('/fetch_questions', methods=['GET'])
def fetch_questions():
    questions = list(qnt_collection.find({}, {'_id': 0}))
    return jsonify(questions)


@app.route('/tqpage.html')
def tq():
    return render_template("tqpage.html")


if __name__ == "__main__":
    app.run(debug=True)