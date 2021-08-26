import pytesseract
from PIL import Image
import glob
import cv2
import numpy as np
import os
import shutil
import csv
from flask import Flask, jsonify, request
import json
import werkzeug

# declared an empty variable for reassignment
response = ''

# creating the instance of our flask application
app = Flask(__name__)

from flask import request


@app.route('/upload', methods=['POST', 'GET'])
def upload():
    if (request.method == "POST"):
        imagefile = request.files['image']
        filename = werkzeug.utils.secure_filename(imagefile.filename)
        saved_file = "./upload" + filename
        imagefile.save(saved_file)
        find_names_and_save(saved_file)
        return jsonify({"message": "successful upload"})
    if request.method == "GET":
        return jsonify({"message": "GET correct"})

def read_ral_names():
    with open("all_ral_names.txt") as f:
        content = f.readlines()
    content = [x.strip() for x in content]
    return content

ral_names = read_ral_names()

# take pictures and sort them into directories
def find_names_and_save(filename):
    path = './all_classes'
    img = read_bw_image(filename)
    ral_name = find_ral_name(img)
    if ral_name not in ral_names:
        ral_name = "unidentified"
    saved_ral_dir = path + "/" + ral_name
    if not os.path.exists(saved_ral_dir):
        os.mkdir(saved_ral_dir)
        shutil.copy(filename, saved_ral_dir)
        print("Directory ", ral_name, " Created ")
    elif os.path.exists(saved_ral_dir):
        shutil.copy(filename, saved_ral_dir)
    find_rgb_values(ral_name, filename)


def find_ral_name(img):
    text = pytesseract.image_to_string(img, lang='eng', config='--psm 6')
    index = text.find("RAL")
    ralname = text[index:index + 8]
    return ralname


def read_bw_image(filename):
    img = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
    _, img = cv2.threshold(img, 160, 255, cv2.THRESH_BINARY)
    return img



def find_rgb_values(ralname, filename):
    path = './all_classes/' + ralname + "/" + filename
    square_list = []
    rect_list = []
            # print(dirname)
              # /all_classes/each_dir
    try:
        img = read_bw_image(path)
        #cv2.imshow("bw",get_rgb_and_save img)
        contours, _ = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for i, cnt in enumerate(contours):
            approx = cv2.approxPolyDP(cnt, 0.01 * cv2.arcLength(cnt, True), True)
            cv2.drawContours(img, [approx], 0, (0, 0, 0), 3)
            if len(approx) == 4 and cv2.contourArea(cnt) > 100:
                x, y, w, h = cv2.boundingRect(approx)
                aspect_ratio = float(w) / h
                if aspect_ratio >= 0.90 and aspect_ratio <= 1.05:
                    cv2.putText(img, "Square", (x, y), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0))
                    square_list.append(cnt)
                if aspect_ratio >= 1.60 and aspect_ratio <= 2.00 and cv2.contourArea(cnt) > 10000:
                    cv2.putText(img, "Rect", (x, y), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0))
                    rect_list.append(cnt)
            #cv2.imshow("countours", img)
        cv2.waitKey(0)
        square_list = get_small_squares(square_list)
        if len(rect_list) == 2:
            rect_list = get_small_rectangle(rect_list)
        get_rgb_and_save(square_list, rect_list, filename, ralname)
        # cv2.waitKey(0)
    except Exception as e:
        print(str(e))
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def get_small_squares(square_list):
    for i in range(len(square_list)):
        for j in range(0, len(square_list) - i - 1):
            if cv2.contourArea(square_list[j]) > cv2.contourArea(square_list[j + 1]):
                square_list[j], square_list[j + 1] = square_list[j + 1], square_list[j]
    small_squares = []
    for i in range(4):
        small_squares.append(square_list[i])
    return small_squares


def get_small_rectangle(rect_list):
    small_rectangle = []
    if cv2.contourArea(rect_list[0]) > cv2.contourArea(rect_list[1]):
        small_rectangle.append(rect_list[1])
    else:
        small_rectangle.append(rect_list[0])
    return small_rectangle


def get_rgb_and_save(square_list, rect_list, fullname, dirname):
    img = cv2.imread(fullname, 1)
    img = cv2.resize(img, (800, 600))
    values = []
    for rect in rect_list:
        x, y, w, h = cv2.boundingRect(rect)
        print(x, y, w, h)
        start_x = int(x + (w / 10))
        stop_x = int(x + ((8 * w) / 10))
        start_y = int(y + (h / 8))
        stop_y = int(y + ((7 * h) / 10))
        red = 0
        green = 0
        blue = 0
        count = 0
        cv2.putText(img, ".", (start_x, stop_y), cv2.FONT_HERSHEY_COMPLEX, 3, (255, 0, 0))
        cv2.putText(img, ".", (start_x, start_y), cv2.FONT_HERSHEY_COMPLEX, 3, (255, 0, 0))
        cv2.putText(img, ".", (stop_x, start_y), cv2.FONT_HERSHEY_COMPLEX, 3, (255, 0, 0))
        cv2.putText(img, ".", (stop_x, stop_y), cv2.FONT_HERSHEY_COMPLEX, 3, (255, 0, 0))
        for i in range(start_x, stop_x):
            for j in range(start_y, stop_y):
                count += 1
                t_blue, t_green, t_red = img[j][i]
                red += t_red
                green += t_green
                blue += t_blue
        print("Rect values=", int(red / count), int(green / count), int(blue / count), count)
        values.append(int(red / count))
        values.append(int(green / count))
        values.append(int(blue / count))
    count = 0
    red = 0
    green = 0
    blue = 0
    for square in square_list:
        x, y, w, h = cv2.boundingRect(square)
        start_x = x
        stop_x = int(x + (3 * w / 5))
        start_y = int(y + (h / 9))
        stop_y = int(y + ((18 * h) / 20))
        cv2.putText(img, ".", (start_x, stop_y), cv2.FONT_HERSHEY_COMPLEX, 3, (255, 0, 0))
        cv2.putText(img, ".", (start_x, start_y), cv2.FONT_HERSHEY_COMPLEX, 3, (255, 0, 0))
        cv2.putText(img, ".", (stop_x, start_y), cv2.FONT_HERSHEY_COMPLEX, 3, (255, 0, 0))
        cv2.putText(img, ".", (stop_x, stop_y), cv2.FONT_HERSHEY_COMPLEX, 3, (255, 0, 0))
        # cv2.imshow("Points", img)
        # cv2.waitKey(0)
        for i in range(start_x, stop_x):
            for j in range(start_y, stop_y):
                count += 1
                t_blue, t_green, t_red = img[j][i]
                red += t_red
                green += t_green
                blue += t_blue
    print("Average square values=", int(red / count), int(green / count), int(blue / count), count)
    #cv2.imshow("final", img)
    values.append(int(red / count))
    values.append(int(green / count))
    values.append(int(blue / count))
    values.append(dirname)
    # 163,138,47,208,195,181,RAL 1000
    with open('name.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow(values)





if __name__ == "__main__":
    app.run(debug=True)
