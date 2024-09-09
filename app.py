from flask import Flask, request, redirect, render_template, url_for
import boto3
from botocore.exceptions import NoCredentialsError, ClientError

app = Flask(__name__)
# app.secret_key = 'ZJ9OKq2ZY2aF0M5Nap7SF9DFTRFKDxNfx0v6qbUcS/'  # Replace with your actual secret key

# Initialize S3 client with your AWS credentials
s3 = boto3.client(
    's3',
    # aws_access_key_id=' AKIA356SJQ2M6DWDKLSAOQIM',  # Replace with your actual access key id
    # aws_secret_access_key='ZJ9OKq2ZY2aF0M5Nap7SF9JSADFTRFxNfx0v6qbUcS/',
    region_name='us-east-1'  # Replace with your region if needed
)

# BUCKET_NAME = 'sourabhsivare-bucket-1'

@app.route('/')
def list_bucket_contents():
    try:
        response = s3.list_objects_v2(Bucket=BUCKET_NAME)
        contents = response.get('Contents', [])
    except NoCredentialsError:
        return "Credentials not available", 403
    except ClientError as e:
        return str(e), 400
    return render_template('index.html', contents=contents)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files or not request.form['folder_name']:
        return redirect('/')
    file = request.files['file']
    folder_name = request.form['folder_name']
    if file.filename == '':
        return redirect('/')
    try:
        s3.upload_fileobj(file, BUCKET_NAME, folder_name + '/' + file.filename)
    except NoCredentialsError:
        return "Credentials not available", 403
    except ClientError as e:
        return str(e), 400
    return redirect('/')

@app.route('/delete_file/<file_key>', methods=['POST'])
def delete_file(file_key):
    try:
        s3.delete_object(Bucket=BUCKET_NAME, Key=file_key)
    except ClientError as e:
        return str(e), 400
    return redirect('/')

@app.route('/copy_file', methods=['POST'])
def copy_file():
    src_key = request.form['src_key']
    dest_key = request.form['dest_key']
    try:
        copy_source = {'Bucket': BUCKET_NAME, 'Key': src_key}
        s3.copy_object(CopySource=copy_source, Bucket=BUCKET_NAME, Key=dest_key)
    except ClientError as e:
        return str(e), 400
    return redirect('/')

@app.route('/move_file', methods=['POST'])
def move_file():
    src_key = request.form['src_key']
    dest_key = request.form['dest_key']
    try:
        copy_source = {'Bucket': BUCKET_NAME, 'Key': src_key}
        s3.copy_object(CopySource=copy_source, Bucket=BUCKET_NAME, Key=dest_key)
        s3.delete_object(Bucket=BUCKET_NAME, Key=src_key)
    except ClientError as e:
        return str(e), 400
    return redirect('/')

@app.route('/create_folder', methods=['POST'])
def create_folder():
    folder_name = request.form['folder_name']
    try:
        s3.put_object(Bucket=BUCKET_NAME, Key=folder_name + '/')
    except ClientError as e:
        return str(e), 400
    return redirect('/')

@app.route('/delete_folder', methods=['POST'])
def delete_folder():
    folder_name = request.form['folder_name']
    try:
        # Delete all objects with the folder prefix
        response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=folder_name + '/')
        for obj in response.get('Contents', []):
            s3.delete_object(Bucket=BUCKET_NAME, Key=obj['Key'])
        # Delete the folder itself
        s3.delete_object(Bucket=BUCKET_NAME, Key=folder_name + '/')
    except ClientError as e:
        return str(e), 400
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
