TAS271-SOURABH SIVARE-PYTHON_ASSIGNMENT 


Q. Implement s3 file manager using any python web framework(flask/django/...etc).
functions :
1. List content of s3.
2. Create/Delete folder + bucket .
3. Upload files to s3 + delete file from s3.
4. Copy/Move file withing s3.
Note:
1. Make sure your code is readable
2. Make sure your app is working properly
3. Need basic UI from which we can access app

Response: 
*  AWS account creation: 

Visit:   
“ https://aws.amazon.com/free/?gclid=Cj0KCQjwlvW2BhDyARIsADnIe-IYmiRIevE41DMm6lAAjyplcOmjVS-tahDWFm2H_Duutuu_0DXgUp4aAj0iEALw_wcB&trk=09863622-0e2a-4080-9bba-12d378e294ba&sc_channel=ps&ef_id=Cj0KCQjwlvW2BhDyARIsADnIe-IYmiRIevE41DMm6lAAjyplcOmjVS-tahDWFm2H_Duutuu_0DXgUp4aAj0iEALw_wcB:G:s&s_kwcid=AL!4422!3!453325184854!e!!g!!aws%20free%20tier!10712784862!111477280251&all-free-tier.sort-by=item.additionalFields.SortRank&all-free-tier.sort-order=asc&awsf.Free%20Tier%20Types=*all&awsf.Free%20Tier%20Categories=*all 
“


-> Enter personal details 
-> Enter user detail (group, corporation, individual ) 
-> Enter payment details (cost free) 
-> Enter purpose/usage 


*  IAM-User Configuration : 

-> Open aws

-> Search ‘Users’ 
    
-> Create User (enter username)
         Provide user access to the AWS Management Console - optional    // select this checkbox
  
  -> Are you providing console access to a person?
                                                                                                                                  //   Select-   I want to create an IAM user   
     -> Select Custom Password 
    
     -> Add Password 
    
    -> Permission Options : 
        -> Select: Attach policies directly
          
        -> In policies options : 
                                                                                                                                   // select : AmazonS3FullAccess


-> Tap on ‘ CREATE USER’ option . 
// user will be created . 

 
-> Create Credentials to access aws-S3 bucket from third party application or application running outside env of S3. 
  
 -> Go to aws-Console 

  -> Go to IAM 

  -> Go to Users 

  -> Select User 

  -> Tap on ‘ Create access key ‘ 

 -> Select ‘ Application running outside AWS ‘ 
. 
-> Download .CSV file which contains credentials details . 


                





*  Open VS Code 

-> Open Project Directory 
   
     -> Install necessary dependencies:
     -> pip install flask boto3 flask-wtf

    -> Set up AWS credentials
    -> Install AWS CLI
    
   -> Configure AWS CLI to store your credentials locally:
   -> aws configure

  // Example Configuration : 
      $ aws configure
     
      AWS Access Key ID [None]: YOUR_ACCESS_KEY
    
     AWS Secret Access Key [None]: YOUR_SECRET_KEY
    
      Default region name [None]: YOUR_REGION (e.g., us-east-1, it worked for me because it is globally        active )
      Default output format [None]: json



*  Files: 
-> Create app.py file in project directory. 

Code: 

-> This is the main file which contains programming logic to connect with aws s3’s bucket and enable upload and retrieval or files and folders on amazon s3 bucket. 



from flask import Flask, request, redirect, render_template, url_for
import boto3
from botocore.exceptions import NoCredentialsError, ClientError

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace this key with the key we created in amazon-console # after creating user. 

# Initialize S3 client with your AWS credentials
s3 = boto3.client(
    's3',
    aws_access_key_id='your_access_key_id',  # Replace with your actual access key id
    aws_secret_access_key='ZJ9OKq2ZY2aF0M5Nap7SF9DFTRFxNfx0v6qbUcS/',
    region_name='us-west-1'  # Replace with your region if needed
)

BUCKET_NAME = 'sourabhsivare-bucket-1'

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



 



     
*  Create directory ‘ templates ‘ in project directory 

  -> Create file index.html  

  -> This file will display the dashboard from which we can : 

      -> user can create folder on aws-S3 bucket . 

      -> user can delete folder on aws-S3 bucket . 
      
      -> user can upload a file on aws-S3. 
          // select folder name and create file . 

      -> user can delete a file on aws-S3. 

     -> user can copy a file to destination on aws-S3 . 
 
    -> user can move a file to destination on aws-S3 . 
    

Code:    





<!DOCTYPE html>
<html>
<head>
   <title>S3 File Manager</title>
</head>
<body>
   <h1>List of Files in Bucket</h1>
   <ul>
       {% for item in contents %}
       <li>
           {{ item.Key }}
           <form action="{{ url_for('delete_file', file_key=item.Key) }}" method="post" style="display:inline;">
               <button type="submit">Delete File</button>
           </form>
           <form action="{{ url_for('copy_file') }}" method="post" style="display:inline;">
               <input type="hidden" name="src_key" value="{{ item.Key }}">
               <input type="text" name="dest_key" placeholder="Destination Key" required>
               <button type="submit">Copy File</button>
           </form>
           <form action="{{ url_for('move_file') }}" method="post" style="display:inline;">
               <input type="hidden" name="src_key" value="{{ item.Key }}">
               <input type="text" name="dest_key" placeholder="Destination Key" required>
               <button type="submit">Move File</button>
           </form>
       </li>
       {% endfor %}
   </ul>
  
   <h2>Upload a File</h2>
   <form action="/upload" method="post" enctype="multipart/form-data">
       <input type="file" name="file" required>
       <input type="text" name="folder_name" placeholder="Folder Name" required>
       <button type="submit">Upload</button>
   </form>


   <h2>Create a Folder</h2>
   <form action="/create_folder" method="post">
       <input type="text" name="folder_name" placeholder="Folder Name" required>
       <button type="submit">Create Folder</button>
   </form>


   <h2>Delete a Folder</h2>
   <form action="/delete_folder" method="post">
       <input type="text" name="folder_name" placeholder="Folder Name" required>
       <button type="submit">Delete Folder</button>
   </form>
</body>
</html>






*  Run File: 

Run the Flask Application:
bash
Copy code
python3 app.py

Access the Application: Open your browser and navigate to http://127.0.0.1:5000/.











              


















































