from flask import Flask, request, Response
import ocrmypdf
import os
import requests
import logging

app = Flask(__name__)

# create a counter to avoid overwriting files
file_count = 0

# Configure logging
logging.basicConfig(level=logging.INFO)

# create a logger
logger = logging.getLogger(__name__)

@app.route('/upload', methods=['POST'])
def upload_file():
    global file_count # use the global counter
    data = request.get_data()  # get the binary data
    
    # only allow POST requests
    if request.method != 'POST':
        return 'Only POST requests are allowed', 405

    if not data:
        return 'No file provided', 400

    # create a counter to avoid overwriting files
    file_count += 1

    # create paths for the input and output files
    input_path = os.path.join('temp', f'input {file_count}.pdf')
    output_path = os.path.join('temp', f'ocr_output{file_count}.pdf')

    # write the binary data to a file
    with open(input_path, 'wb') as f:
        f.write(data)

    # run OCR on the file
    try:
        ocrmypdf.ocr(input_path, output_path, deskew=True)
        logger.info(f'OCR complete for file {file_count}')
    except Exception as e:
        return f'An error occurred during OCR: {str(e)}', 500

    # read the output file
    with open(output_path, 'rb') as f:
        data = f.read()
        url = 'https://7c83le1kbc.execute-api.us-east-1.amazonaws.com/upload'
        
        response = requests.post(url,data=data)
        logger.info(f'File {file_count} uploaded to S3')
        if response.status_code != 200:
            return f'An error occurred uploading the file: {response}', 500

    # delete the original file
    os.remove(input_path)
    logger.info(f'File input {file_count} deleted from local storage')

    # delete the output file
    os.remove(output_path)
    logger.info(f'File output {file_count} deleted from local storage')

    # return the response
    respond = Response(response.text, status=200, mimetype='application/json')
    return respond

if __name__ == '__main__':
    app.run(debug=True)


@app.route('/')
def hello_world():
    return 'Hello Coopernauta!'
