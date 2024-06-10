from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
import base64
from flask import jsonify

app = Flask(__name__)
app.static_folder = 'static'

# Replace with your actual MongoDB connection details
client = MongoClient("mongodb://localhost:27017/")
db = client["third_eye"]
collection = db["login"]
login_collection = db['login']
questions_collection = db['questions']
detected_objects_collection = db['detected_objects']

@app.route("/")
def login():
    return render_template("login.html")

@app.route('/add_user')
def add():
    return render_template("add_user.html")

@app.route('/add', methods=['POST'])
def add_user():
    
        # Get user details from the form
    username = request.form['username']
    password = request.form['password']
    account_type = request.form['account_type']  # 'admin' or 'user'
    
    # Insert new user into the login collection
    login_collection.insert_one({
        'username': username,
        'password': password,
        'account_type': account_type
    })
    
    # Redirect to the admin home page after adding the user
    return redirect(url_for('admin'))

@app.route('/view_detected_objects')
def view_detected_objects():
    # Retrieve all detected objects from the detected_objects collection
    detected_objects = detected_objects_collection.find({}, {"_id": 0})
    
    return render_template('view_objects.html', detected_objects=detected_objects)

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
        if user['account_type']=="admin":
            return redirect('/admin')
        else:
        # Successful login, redirect to guideline page
            return redirect(url_for("guidelines"))
    else:
        return render_template("login.html", error="Invalid username or password.")

@app.route("/guidelines")
def guidelines():
    return render_template("guidelines.html")

@app.route('/admin')
def admin():
    return render_template("admin.html")

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

@app.route('/view_users')
def view_users():
    # Retrieve all users from the login collection
    users = login_collection.find({}, {"_id": 0, "username": 1, "account_type": 1})
    user_data = [(user['username'], user['account_type']) for user in users]
    return render_template('view_users.html', users=user_data)

@app.route('/delete_user')
def delete_user():
    return render_template("delete_user.html")



@app.route('/delete', methods=['POST'])
def delete_users():
    if request.method == 'POST':
        # Get the username and confirmation status from the request data
        data = request.json
        username = data.get('username')
        confirmation = data.get('confirmation')
        
        # Check if the username exists in the database
        user = login_collection.find_one({"username": username})
        if user:
            if confirmation:
                # Delete the user from the collection
                login_collection.delete_one({"username": username})
                return jsonify({"deleted": True}), 200
            else:
                # If confirmation checkbox is not checked, return appropriate response
                return jsonify({"error": "Confirmation checkbox not checked."}), 400
        else:
            # If user not found, return appropriate response
            return jsonify({"error": "User not found."}), 404
    
    # If request method is not POST, return invalid request response
    return jsonify({"error": "Invalid request."}), 400


@app.route('/view_questions')
def view_questions():
    # Retrieve all questions from the questions collection
    questions = questions_collection.find({}, {"_id": 0})
    
    return render_template('view_questions.html', questions=questions)
    
    
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
@app.route("/adhi")
def adhi():
    return render_template("adhi.html")

if __name__ == "__main__":
    app.run(debug=True)
