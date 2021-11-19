import os
import bcrypt
import cv2
import tensorflow as tf
import numpy as np
from datetime import datetime
from keras.models import load_model
from modules.dataBase import collection as db
from modules.dataBase.collection import user_records
from flask import Blueprint, request, render_template, jsonify, redirect, session, url_for

mod = Blueprint('backend', __name__, template_folder='templates', static_folder='./static')
UPLOAD_URL = 'http://0.0.0.0:8400/static/'
model = load_model("modules/model/mobilenet_model.hdf5")
class_names = ['Dark', 'Green', 'Light', 'Medium']
model.make_predict_function()


@mod.route('/upload')
def home():
    return render_template('image_predict.html')


# assign URLs to have a particular route
@mod.route("/", methods=['post', 'get'])
def register():
    message = ''
    # if method post in index
    if "email" in session:
        return redirect(url_for("backend.logged_in"))
    if request.method == "POST":
        user = request.form.get("fullname")
        email = request.form.get("email")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        # if found in database showcase that it's found
        user_found = user_records.find_one({"name": user})
        email_found = user_records.find_one({"email": email})
        if user_found:
            message = 'There already is a user by that name'
            return render_template('index.html', message=message)
        if email_found:
            message = 'This email already exists in database'
            return render_template('index.html', message=message)
        if password1 != password2:
            message = 'Passwords should match!'
            return render_template('index.html', message=message)
        else:
            # hash the password and encode it
            hashed = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())
            # assing them in a dictionary in key value pairs
            user_input = {'name': user, 'email': email, 'password': hashed}
            # insert it in the record collection
            user_records.insert_one(user_input)

            # find the new created account and its email
            user_data = user_records.find_one({"email": email})
            new_email = user_data['email']
            # if registered redirect to logged in as the registered user
            return render_template('logged_in.html', email=new_email)

    return render_template('index.html')


@mod.route("/login", methods=["POST", "GET"])
def login():
    message = 'Please login to your account'
    if "email" in session:
        return redirect(url_for("backend.logged_in"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # check if email exists in database
        email_found = user_records.find_one({"email": email})
        if email_found:
            email_val = email_found['email']
            passwordcheck = email_found['password']
            # encode the password and check if it matches
            if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                session["email"] = email_val
                return redirect(url_for('backend.logged_in'))
            else:
                if "email" in session:
                    return redirect(url_for("backend.logged_in"))
                message = 'Wrong password'
                return render_template('login.html', message=message)
        else:
            message = 'Email not found'
            return render_template('login.html', message=message)
    return render_template('login.html', message=message)


@mod.route('/logged_in')
def logged_in():
    if "email" in session:
        email = session["email"]
        return render_template('logged_in.html', email=email)
    else:
        return redirect(url_for("login"))


@mod.route("/logout", methods=["POST", "GET"])
def logout():
    if "email" in session:
        session.pop("email", None)
        return render_template("signout.html")
    else:
        return render_template('index.html')


@mod.route('/predict', methods=['POST'])
def predict():
    user_name = session.get('email')
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return "someting went wrong 1"

        user_file = request.files['file']
        if user_file.filename == '':
            return "file name not found ..."

        elif user_name:
            path = os.path.join(os.getcwd() + '\\modules\\static\\' + user_file.filename)
            user_file.save(path)

            image = cv2.resize(cv2.imread(path), (224, 224))
            # Use gaussian blur
            blurImg = cv2.GaussianBlur(image, (5, 5), 0)

            # Convert to HSV image
            hsvImg = cv2.cvtColor(blurImg, cv2.COLOR_BGR2HSV)

            # Create mask (parameters - green color range)
            lower_green = (25, 40, 50)
            upper_green = (75, 255, 255)
            mask = cv2.inRange(hsvImg, lower_green, upper_green)
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

            # Create bool mask
            bMask = mask > 0

            # Apply the mask
            clear = np.zeros_like(image, np.uint8)  # Create empty image
            clear[bMask] = image[bMask]  # Apply boolean mask to the origin image
            clearTestImg = clear / 255
            clearTestImg = tf.expand_dims(clearTestImg, 0)
            predictions = model.predict(clearTestImg)
            score = tf.nn.softmax(predictions)

            class_name = class_names[np.argmax(score)]
            score = np.max(score) * 100

            db.addNewImage(
                user_file.filename,
                class_name,
                str(round(score, 2)),
                datetime.now(),
                UPLOAD_URL + user_file.filename,
                user_name
            )
            return jsonify({
                "status": "success",
                "class": class_name,
                "score": str(round(score, 2)),
                "upload_time": datetime.now(),
                "user_name": user_name
            }), user_name
