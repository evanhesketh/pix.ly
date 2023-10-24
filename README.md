# pix.ly (backend)
This is the backend for a photo storage/filter app

## Local setup
1. Create virtual environment and activate

    ``` 
    python3 -m venv venv  
    source venv/bin/activate
    ```

2. Install dependencies

    ```
    pip3 install -r requirements.txt
    ```
3. Create a new PostgreSQL database
   ```
   createdb pixly
   ```
4. Set up AWS: <br>
   Create a free AWS account at https://aws.amazon.com/ <br>
   Create a new S3 bucket <br>
   Under permissions, add the following to bucket policy: 
    ```
     {
      "Version": "2012-10-17",
      "Statement": [
          {
              "Effect": "Allow",
              "Principal": "*",
              "Action": "s3:GetObject",
              "Resource": "arn:aws:s3:::[remove brackets and replace with your bucket name]*"
          }
        ]
      }
    ```
    Permissions should be: <br>
    -Access: public <br>
    -Block all public access: off <br>
    -Object ownership: Bucket owner enforced <br>
   
4. Create a file named .env and add environment variables with values from your AWS account:
   ```
   AWS_ACCESS_KEY_ID=*add your value here*
   AWS_SECRET_ACCESS_KEY=*add your value here*
   BUCKET_NAME=*add your value here*
   REGION=*add your value here*
   ```
5. Create the database tables <br>
   Run IPython:
   ```
   ipython
   ```
   In IPython:
   ```
   %run app.py
   db.create_all()
   ```

7. To start server:
    ```
    python3 -m flask run -p 5000 (or 5001 if on newer mac)
    ```
8. Refer to instructions for front end at https://github.com/evanhesketh/pix.ly-frontend
