import cv2
import numpy as np
import os
import json
import random
import configparser
import boto3
import shutil
import io

config = configparser.ConfigParser()
config.read('config.ini')

# Read image
positivedir = 'data/frames/positive'
boundaries = [
    'AllMaterial',
    'Wood',
    'Brick',
    'Metal',
    'Weapons Slots',
    'Weapons',
    'HealthShield',
    'Health',
    'Shield',
    'GameStatus',
    'StormClock',
    'PlayersLeft',
    'StormCount',
    'Chat',
    'TeamStats',
    'TeammateHealth',
    'Streamer'
]

multipleSelects = [
    'Weapons',
    'TeammateHealth',
]
if not os.path.exists('data/assets'):
    os.makedirs('data/assets')


assetBoundaries = {}

newFileFound = False
s3client = boto3.client('s3',
                        aws_access_key_id=config['S3_BUCKET']['accesskey'],
                        aws_secret_access_key=config['S3_BUCKET']['accesssecret'],)
positivesList = s3client.get_object(
    Bucket=config['S3_BUCKET']['bucket'], Key='positives.json')
positiveImages = s3client.list_objects(
    Bucket=config['S3_BUCKET']['bucket'], Prefix='frames/positive')
positives = json.load(positivesList['Body'])
while not newFileFound:
    fileIndex = random.randint(0, len(positiveImages['Contents']) - 1)
    filename = os.path.basename(positiveImages['Contents'][fileIndex]['Key'])
    if not filename in positives:
        fileKey = positiveImages['Contents'][fileIndex]['Key']
        newFileFound = True
temppath = os.path.join(config['DIRECTORY']['temp'],
                        'crop')
if not os.path.exists(temppath):
    os.makedirs(temppath)
i = 0
tempfilename = os.path.join(temppath, filename)
s3client.download_file(config['S3_BUCKET']['bucket'], fileKey, tempfilename)


frameWidth = 600
im = cv2.imread(tempfilename)
width, height = im.shape[:2]
# imgScale = frameWidth/width
# newX,newY = im.shape[1]*imgScale, im.shape[0]*imgScale
# resized = cv2.resize(im,(int(newX),int(newY)))

removeImg = False
bail = False

for asset in boundaries:
    mulitpleBounds = []
    # # Select ROI
    font = cv2.FONT_HERSHEY_SIMPLEX
    if removeImg == True or bail == True:
        break
    newimg = im.copy()
    while True:
        cv2.putText(newimg, f'Select {asset}', (int(width/2), 130), font,
                    .8, (200, 255, 155), 2, cv2.LINE_AA)
        cv2.putText(newimg, f'Press enter then d to delete this frame as a positive', (int(width/2), 160), font,
                    .8, (20, 95, 70), 2, cv2.LINE_AA)
        r = cv2.selectROI("Image", newimg)

        if not (asset == 'Weapons' or asset == 'TeammateHealth') or r[2] == 0:
            if r[2] == 0:
                nextCommand = cv2.waitKey()
                if nextCommand == 100:
                    removeImg = True
                if nextCommand == 113:
                    bail = True
            break
        else:
            mulitpleBounds.append(r)
    if r[2] > 0:
        if (asset == 'Weapons' or asset == 'TeammateHealth'):
            assetBoundaries[asset] = mulitpleBounds
        else:
            assetBoundaries[asset] = r


if removeImg == True:
    s3client.delete_object(Bucket=config['S3_BUCKET']['bucket'], Key=fileKey)
    print(f'deleted file {filename}')
elif not bail:
    assetBoundaries['CroppedWidth'] = frameWidth
    positives[os.path.splitext(filename)[0]] = assetBoundaries
    p = json.dumps(positives)
    s3client.put_object(
        Bucket=config['S3_BUCKET']['bucket'], Key='positives.json', Body=p)


shutil.rmtree(temppath)
