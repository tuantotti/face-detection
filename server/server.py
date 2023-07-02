import os
import uuid

import cv2
import torch
from flask import Flask, request, flash, send_from_directory
from werkzeug.utils import secure_filename

ROOT_FOLDER = os.getcwd()
UPLOAD_FOLDER = f'{ROOT_FOLDER}/file_upload'
BOUNDING_BOX_FOLDER = f'{ROOT_FOLDER}/bounding_box'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['BOUNDING_BOX_FOLDER'] = BOUNDING_BOX_FOLDER

# load the best trained model
model = torch.hub.load('ultralytics/yolov5', 'custom',
                       path=f'{ROOT_FOLDER}/best.pt', force_reload=True)


def pre_processing_img(crop_img):
    # grayscale region within bounding box
    gray = cv2.cvtColor(crop_img, cv2.COLOR_RGB2GRAY)

    # resize image to three times as large as original for better readability
    gray = cv2.resize(gray, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)

    # perform gaussian blur to remove noise
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    ret, binary = cv2.threshold(
        blur, 127, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    # perform another blur on character region
    result = cv2.medianBlur(binary, 5)

    return result


def save_image(img, results, bd_id):
    lp_list = results.pandas().xywh[0].values.tolist()
    for idx, lp in enumerate(lp_list):
        x, y, w, h = lp[0], lp[1], lp[2], lp[3]
        x1 = int(x - w / 2)
        y1 = int(y - h / 2)
        x2 = int(x + w / 2)
        y2 = int(y + h / 2)

        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 4)
    cv2.imwrite(f"{ROOT_FOLDER}/bounding_box/" + bd_id + ".jpeg", cv2.cvtColor(img, cv2.COLOR_BGR2RGB))


def is_allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/api/image', methods=['POST'])
def upload_image():
    # check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part')
        return {"message": "Error"}
    file = request.files['file']
    print(file.filename)
    # If the user does not select a file, the browser submits an empty file without a filename.
    if file.filename == '':
        flash('No selected file')
        return {"message": "Error"}
    if file and is_allowed_file(file.filename):
        filename = secure_filename(file.filename)
        img_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        img = cv2.imread(img_path, cv2.IMREAD_COLOR)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # predict
        results = model(img)

        print(results.pandas().xyxy)
        detect = False
        image = ""

        if len(results.pandas().xyxy) > 0:
            bd_id = str(uuid.uuid4())
            save_image(img, results, bd_id)
            detect = True
            image = bd_id + ".jpeg"

    return {"detect": detect, "image": image}


@app.route('/image/<name>')
def view_image(name):
    return send_from_directory(app.config['BOUNDING_BOX_FOLDER'], name)


if __name__ == '__main__':
    app.run()
