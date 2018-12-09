import os
import json
import cv2
import shutil
import boto
import boto.s3.connection
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

#Set up S3
conn = boto.connect_s3(
    aws_access_key_id=config['S3_BUCKET']['accesskey'],
    aws_secret_access_key=config['S3_BUCKET']['accesssecret'],
    calling_format=boto.s3.connection.OrdinaryCallingFormat()
)

bucket = conn.get_bucket(config['S3_BUCKET']['bucket'])
for key in bucket.list():
    print(key.key)

if False:
    assetdir = 'data/assets'
    key = 'AllMaterial'

    REBUILD_FOLDER = False

    # Change to s3
    # if not os.path.exists(assetdir):
    #     os.makedirs(assetdir)
    # outdir = f'{assetdir}/{key}'

    # if REBUILD_FOLDER:
    #     shutil.rmtree(outdir)
    # if not os.path.exists(outdir):
    #     os.makedirs(outdir)
    # negativedir = f'data/frames/negative'


    with open('data/assets/positives.json', 'r') as outfile:
        positives = json.load(outfile)


    for frame in positives:
        try:
            if not os.path.exists(f"{outdir}/{frame}.jpg"):
                im = cv2.imread(f'data/frames/positive/{frame}')
                crop = positives[frame][key]
                print(crop)
                cropim = im[crop[1]: crop[1] + crop[3], crop[0]: crop[0] + crop[2]]
                cv2.imshow("crop", cropim)
                croppedimname = f"{outdir}/{frame}.jpg"
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

        except:
            print(f'{frame} missing {key}')

    try:
        #TODO: Change this to remove s3 key
        k = boto.s3.connection.Key(bucket)
        k.key = 'negatives/negatives.txt'
        bucket.delete_key(k)
        negativeFiles = ''
        #TODO: Only write for the negatives and change to stream
        for negative in bucket.list():
            negativeFile &= f'\n{negative}'
        k.set_contents_from_stream(negativeFile)
            with open(f'{negativedir}/negatives.txt', 'a+') as outfile:
                # newfile = f'{outfile}\n{croppedimname}'
                outfile.write(f'\n{negative}')
    except:
        pass

