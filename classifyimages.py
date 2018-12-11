from time import gmtime, strftime
import configparser
import cv2
import os
import zipfile
import random
import shutil
import boto3
import io

config = configparser.ConfigParser()
config.read('config.ini')


s3client = boto3.client('s3',
                        aws_access_key_id=config['S3_BUCKET']['accesskey'],
                        aws_secret_access_key=config['S3_BUCKET']['accesssecret'],)

specificfile = 'starcraft 2_181207_062429.zip'

# check if file exits locally, if not grab it from s3
clips = s3client.list_objects(
    Bucket=config['S3_BUCKET']['bucket'], Prefix=f'clips/unsorted/{specificfile}')
clips = list(
    filter(lambda x:  os.path.splitext(x['Key'])[1] == '.zip', clips['Contents']))

zipindex = random.randint(0, len(clips) - 1)

clip = s3client.get_object(
    Bucket=config['S3_BUCKET']['bucket'], Key=clips[zipindex]['Key'])

zipfilename = clips[zipindex]['Key']
now = strftime("%y%m%d_%H%M%S", gmtime())
temppath = os.path.join(config['DIRECTORY']['temp'],
                        'clips',  f'{os.path.basename(zipfilename)}_{now}')
if not os.path.exists(temppath):
    os.makedirs(temppath)


frameTypes = {
    "positive": [[103, 112], 'this is gameplay'],
    "bus": [98, 'player is on bus waiting to drop'],
    "negative": [[102, 110], 'this has nothing to do with fortnite'],
    "lobby": [108, 'player is in a lobby or on a loading screen'],
    "waiting": [119, 'player is waiting for a game to fill'],
    "unsure": [117, 'you aren\'t sure how to categorize this photo'],
}

fileno = 0
startIndex = 0  # 875
frameWidth = 1000
bail = False
print('loading clips')
with io.BytesIO(clip['Body'].read()) as tf:
    tf.seek(0)
    tempdir = f'data/temp/frames'
    if not os.path.exists(tempdir):
        os.makedirs(tempdir)
    with zipfile.ZipFile(tf, mode='r') as zf:
        print('clips loaded')
        noOfClips = len(zf.infolist())
        for zippedfile in zf.infolist():
            fileno += 1
            if fileno < startIndex:
                continue
            zf.extract(zippedfile, temppath)
            tempfilename = zippedfile.filename
            tempfile = os.path.join(temppath, tempfilename)
            print(tempfile)
            vidcap = cv2.VideoCapture(tempfile)
            success, image = vidcap.read()
            count = 0

            # positive

            for categories in frameTypes:
                if not os.path.exists(f'{tempdir}/{categories}'):
                    os.makedirs(f'{tempdir}/{categories}')

            grabevery = 50  # Show an image for judgement every x frames.
            width, height = image.shape[:2]
            font = cv2.FONT_HERSHEY_SIMPLEX
            while success and not bail:
                if count % grabevery == 0:
                    textimage = image.copy()
                    height, width, depth = image.shape
                    imgScale = frameWidth/width
                    newX,newY = image.shape[1]*imgScale, image.shape[0]*imgScale
                    textimage = cv2.resize(textimage,(int(newX),int(newY)))
                    textTop = 20
                    cv2.putText(textimage, f'{fileno} of { noOfClips} clips',
                                (0, 20), font, .6, (255, 0, 20), 2, cv2.LINE_AA)
                    for categories in frameTypes:
                        textTop += 20
                        if isinstance(frameTypes[categories][0], list):
                            keys = map(lambda x: chr(
                                x), frameTypes[categories][0])
                            keys = ' or '.join(keys)

                        else:
                            keys = chr(frameTypes[categories][0])
                        message = f'Press {keys} if {frameTypes[categories][1]}'
                        cv2.putText(textimage, message,
                                    (int(frameWidth/2), textTop), font, .6, (255, 255, 255), 2, cv2.LINE_AA)
                    textTop += 20
                    cv2.putText(textimage, 'Enter q to quit',
                                (int(frameWidth/2), textTop), font, .6, (255, 255, 255), 2, cv2.LINE_AA)
                    cv2.imshow("Image", textimage)

                    picResponse = cv2.waitKey()
                    if picResponse == 113:  # Q means Quit
                        bail = True
                        break
                    frameNo = int(count/grabevery)
                    clipname = f'{os.path.splitext(tempfilename)[0]}_{int(frameNo)}'
                    keyFound = False
                    for key in frameTypes:
                        if isinstance(frameTypes[key][0], list):
                            if picResponse in frameTypes[key][0]:
                                keyFound = True
                        else:
                            keyFound = picResponse == frameTypes[key][0]
                        if keyFound:
                            cv2.imwrite(f"{tempdir}/{key}/{clipname}.jpg",
                                        image)
                            break
                if bail:
                    break
                success, image = vidcap.read()
                count += 1
            if bail:
                break
# TODO: Create a processed zip and move every 100 clips over so this can be done in batches.
vidcap.release()
if not bail:
    for dir in os.listdir(tempdir):
        print(dir, '--')
        for root, dirs, files in os.walk(os.path.join(tempdir, dir)):
            for fname in files:
                s3client.upload_file(
                    os.path.join(tempdir, dir, fname), config['S3_BUCKET']['bucket'], f'frames/{dir}/{fname}')
    # s3 move zip file to processed
    oldKey = config['S3_BUCKET']['bucket'] + '/' + zipfilename
    print(zipfilename)
    s3client.copy_object(Bucket=config['S3_BUCKET']['bucket'], CopySource=oldKey,
                         Key=zipfilename.replace('/unsorted/', '/processed/'))
    s3client.delete_object(
        Bucket=config['S3_BUCKET']['bucket'], Key=zipfilename)
shutil.rmtree(tempdir)
# upload sorted files to s3 and then clean up the folders
