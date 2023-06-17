from flask import Flask, request
import ocrmypdf
import os
import requests

app = Flask(__name__)

# Set the Tesseract executable path
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

@app.route('/upload', methods=['POST'])
def upload_file():
    data = request.get_data()  # get the binary data

    if request.method != 'POST':
        return 'Only POST requests are allowed', 405

    if not data:
        return 'No file provided', 400

    # create paths for the input and output files
    input_path = os.path.join('temp', 'input.pdf')
    output_path = os.path.join('temp', 'ocr_output.pdf')

    # write the binary data to a file
    with open(input_path, 'wb') as f:
        f.write(data)

    # run OCR on the file
    try:
        ocrmypdf.ocr(input_path, output_path, deskew=True)
    except Exception as e:
        return f'An error occurred during OCR: {str(e)}', 500

    # read the output file
    with open(output_path, 'rb') as f:
        data = f.read()
        url = 'https://7c83le1kbc.execute-api.us-east-1.amazonaws.com/upload'
        
        response = requests.post(url,data=data)
        if response.status_code != 200:
            return f'An error occurred uploading the file: {response}', 500

    # delete the original file
    os.remove(input_path)

    # delete the output file
    os.remove(output_path)

    return f'OCR upload successfully: {response.text}', 200

if __name__ == '__main__':
    app.run(debug=True)


@app.route('/')
def hello_world():
    return 'Hello Coopernauta!'
