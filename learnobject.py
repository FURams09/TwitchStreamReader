import os
import json
import cv2
import shutil
import boto3
import configparser
import botocore

config = configparser.ConfigParser()
config.read('config.ini')

# Set up S3
s3client = boto3.client('s3',
                        aws_access_key_id=config['S3_BUCKET']['accesskey'],
                        aws_secret_access_key=config['S3_BUCKET']['accesssecret'],)
resource = boto3.resource('s3',
                          aws_access_key_id=config['S3_BUCKET']['accesskey'],
                          aws_secret_access_key=config['S3_BUCKET']['accesssecret'])
bucket = resource.Bucket(config['S3_BUCKET']['bucket'])

positiveResources = s3client.get_object(
    Bucket=config['S3_BUCKET']['bucket'], Key='positives.json')
p = json.load(positiveResources['Body'])

# for key in positivies:
#     print(key.name)

key = 'AllMaterial'
for frame in p:
    fileKey = f'frames/positives/{frame}'
    outputFile = f'assets/{key}/{frame}'
    try:
        frameAsset = resource.Object(
            config['S3_BUCKET']['bucket'], key=outputFile).load()
        print(fileKey)
    except botocore.exceptions.ClientError as e:
        print(f'{outputFile} not found. Processing {fileKey}')
        frameImg = resource.Object(
            config['S3_BUCKET']['bucket'], key=fileKey).load()
        if False:
            im = cv2.imread(f'data/frames/positive/{frame}')

            crop = positives[frame][key]
            print(crop)
            cropim = im[crop[1]: crop[1] + crop[3],
                        crop[0]: crop[0] + crop[2]]
            cv2.imshow("crop", cropim)
            croppedimname = f"{outdir}/{frame}"
            cv2.imwrite(croppedimname,
                        cropim)
            with open(f'{outdir}/positives.txt', 'a+') as outfile:
                # newfile = f'{outfile}\n{croppedimname}'
                outfile.write(f'\n{croppedimname}')
            with open(f'{outdir}/info.dat', 'a+') as outfile:
                # newfile = f'{outfile}\n{croppedimname}'
                outfile.write(
                    f'\ndata/frames/positive/{frame} {crop[0]} {crop[1]} {crop[2]} {crop[3]}')
            cv2.waitKey(1000)
if False:
    try:
        # TODO: Change this to remove s3 key
        k = boto.s3.connection.Key(bucket)
        k.key = 'negatives/negatives.txt'
        bucket.delete_key(k)
        negativeFiles = ''
        # TODO: Only write for the negatives and change to stream
        for negative in bucket.list():
            negativeFile &= f'\n{negative}'
        k.set_contents_from_stream(negativeFile)
        with open(f'{negativedir}/negatives.txt', 'a+') as outfile:
                # newfile = f'{outfile}\n{croppedimname}'
            outfile.write(f'\n{negative}')
    except:
        pass
