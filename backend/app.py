from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_cors import CORS  
import time
app = Flask(__name__)


CORS(app)

pi_uid=None
app.config["MONGO_URI"] = "mongodb://localhost:27017/test"  
mongo = PyMongo(app)
bcrypt = Bcrypt(app)


@app.route('/register', methods=['POST'])
def register():
    global pi_uid
    data = request.get_json()

    
    if not data or not data.get('username') or not data.get('email') or not data.get('password') :
        return jsonify({"message": "Missing required fields"}), 400

    username = data['username']
    email = data['email']
    password = data['password']
    # make a new request to get user id from raspberrypi and wait for the response from raspberrypi to scan the nfc and send a post request on /register_uid()
    print("Now Scan NFC card")
    while not pi_uid:
        time.sleep(0.2)
        continue
    uid = data['uid']

    
    user = mongo.db.users.find_one({"email": email})
    if user:
        return jsonify({"message": "User already exists!"}), 400
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    user_data = {
        "username": username,
        "email": email,
        "password": hashed_password,
        "uid": uid
    }

    mongo.db.users.insert_one(user_data)
    pi_uid=None
    return jsonify({"message": "User registered successfully!"}), 201


@app.route('/check_uid', methods=['GET,POST'])
def check_uid():
    uid = request.args.get('uid')  
    print(uid)
    if not uid:
        return jsonify({"message": "UID is required"}), 400

    
    user = mongo.db.users.find_one({"uid": uid})
    print(user)

    if user:
        
        return jsonify({"username": user['username']}), 200
    else:
        return jsonify({"message": "User not found"}), 404
@app.route('/register_uid', methods=['POST'])
def register_uid():
    global pi_uid
    uid = request.args.get('uid')  
    pi_uid=uid
    print(pi_uid)
    return jsonify({"message": "User registered successfully!"}), 200

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
