from pymongo import MongoClient
import certifi
import bcrypt

client = MongoClient(
    "mongodb+srv://ttp_coffee_love:9mj2tcB0xhrzxPuV@cluster0.vpotj.mongodb.net/myFirstDatabase?retryWrites=true&w=majority",
    tlsCAFile=certifi.where())  # host uri
user_db = client.get_database('total_records')  # Select the database
user_records = user_db.register

image_db = client.image_predition  # Select the database
image_details = image_db.imageData


# def addNewUser(user):
#     user_records.insert_one({
#         "name": user,
#     })
#
# def addNewEmail(email):
#     user_records.insert_one({
#         "email": email,
#     })
#
# def addNewPass(hashed):
#     user_records.insert_one({
#         "password": hashed,
#     })
#

def addNewImage(i_name, class_name, score, time, url, name):
    image_details.insert({
        "file_name": i_name,
        "class": class_name,
        "score": score,
        "upload_time": time,
        "url": url,
        "user_name": name
    })


def getAllImages():
    image_data = image_details.find()
    return image_data
