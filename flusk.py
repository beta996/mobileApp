from flask import Flask, jsonify, request
import json
import werkzeug

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
    if(request.method == "POST"):
        imagefile = request.files['image']
        filename = werkzeug.utils.secure_filename(imagefile.filename)
        imagefile.save("./upload" + filename)
        return jsonify({"message":"successful upload"})


if __name__ == "__main__":
    app.run(debug=True)
