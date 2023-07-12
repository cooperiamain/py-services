from flask import Flask, request, Response
from flask_cors import CORS
import ocrmypdf
import os
import requests
import logging
import tempfile
import uuid

app = Flask(__name__)
# enable CORS
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)

# create a logger
logger = logging.getLogger(__name__)

@app.route('/upload', methods=['POST'])
def upload_file():
    data = request.get_data()  # get the binary data

    if not data:
        return 'No file provided', 400

    # create a unique file name
    filename = str(uuid.uuid4().hex)

    # create paths for the input and output files using tempfile
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as input_file, \
        tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as output_file:
        input_path = input_file.name
        output_path = output_file.name

        # write the binary data to a file
        input_file.write(data)


    # run OCR on the file
    try:
        ocrmypdf.ocr(input_path, output_path, deskew=True)
        logger.info(f'OCR complete for file {filename}')
    except Exception as e:
        logger.exception('An error occurred during OCR')
        return f'An error occurred during OCR: {str(e)}', 500

    # read the output file
    with open(output_path, 'rb') as f:
        data = f.read()
        url = 'https://7c83le1kbc.execute-api.us-east-1.amazonaws.com/upload'
        
        response = requests.post(url,data=data)
        logger.info(f'File {filename} uploaded to S3')
        if response.status_code != 200:
            return f'An error occurred uploading the file: {response}', 500

    # delete the original file
    os.remove(input_path)
    logger.info(f'File {filename} deleted from local storage')

    # delete the output file
    os.remove(output_path)

    # return the response
    respond = Response(response.text, status=200, mimetype='application/json')
    return respond

if __name__ == '__main__':
    app.run(debug=True)


@app.route('/')
def hello_world():
    return 'Hello Coopernauta!'
