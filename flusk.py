from flask import Flask, jsonify, request
import json
import werkzeug
import glob
import cv2

# declared an empty variable for reassignment
response = ''

# creating the instance of our flask application
app = Flask(__name__)

from flask import request

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         return do_the_login()
#     else:
#         return show_the_login_form()


# from werkzeug.utils import secure_filename
#
# @app.route('/upload', methods=['GET', 'POST'])
# def upload_file():
#     if request.method == 'POST':
#         file = request.files['the_file']
#         file.save(f"/var/www/uploads/{secure_filename(file.filename)}")

# route to entertain our post and get request from flutter app


@app.route('/upload', methods=['POST', 'GET'])
def upload():
    if (request.method == "POST"):
        imagefile = request.files['image']
        filename = werkzeug.utils.secure_filename(imagefile.filename)
        file_name = imagefile.save("./upload" + filename)
        print(file_name)
        if file_name:
            img = cv2.imread(file_name, cv2.IMREAD_GRAYSCALE)
            print(file_name)
            img = cv2.resize(img, (800, 600))
            _, threshold = cv2.threshold(img, 155, 255, cv2.THRESH_BINARY)
            cv2.imshow("threshold1", threshold)
        return jsonify({"message": "successful upload"})
    if request.method == "GET":
        return jsonify({"message": "GET correct"})


if __name__ == "__main__":
    app.run(debug=True)

