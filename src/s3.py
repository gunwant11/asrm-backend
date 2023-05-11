import boto3, os

BUCKET_NAME = '3d-assets-portfolio'
os.environ['AWS_ACCESS_KEY_ID'] = 'AKIAQJBBCSNVEL3KVMFG'
os.environ['AWS_SECRET_ACCESS_KEY'] = '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'

# Create an S3 client object
s3 = boto3.client('s3', region_name='ap-south-1')

def uplaodtoS3(audioPathType, fileName, file):
    try:
        key = ''
        if (audioPathType == 'testing_set' ):
            key = 'model/testing_set/' + fileName
        elif (audioPathType == 'training_set' ):
            key = 'model/training_set/' + fileName
        elif (audioPathType == 'trained_models' ):
            key = 'model/trained_models/' + fileName
        else:
            return "Error uploading file to S3"
        # Upload the file to S3
        s3.upload_fileobj(file.file, BUCKET_NAME, key)
        # Generate the URL for the uploaded file
        url = f'https://{BUCKET_NAME}.s3.amazonaws.com/{key}'

        return url
    except Exception as e:
        print(e)
        return "Error uploading file to S3"

def download_from_s3(folder_path):
    try:
        # Create an S3 client object
        s3 = boto3.client('s3')
        
        # Get a list of objects in the folder path
        objects = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=folder_path)['Contents']
        
        # Download each object and add it to a list
        results = []
        for obj in objects:
            key = obj['Key']
            file = s3.get_object(Bucket=BUCKET_NAME, Key=key)['Body'].read()
            results.append(file)
        print(results)
        return results
    except Exception as e:
        print(e)
        return "Error downloading from S3"
