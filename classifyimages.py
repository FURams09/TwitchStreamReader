from time import gmtime, strftime
import cv2
import os
import zipfile
import random
import shutil
# Get list of zip files from clips directory
clipzips = os.listdir('data/clips')
now = strftime("%y%m %d_%H%M%S", gmtime())

bail = False
# Specify a file in data/clips to pull from or else this will just grab a random file

specificfile = 'fortnite_181207_164325.zip'

if specificfile == '':
    zipindex = random.randint(0, len(clipzips) - 1)
    zip = os.listdir('data/clips')[zipindex]
    zipfilename = zip
else:
    zipfilename = specificfile
zipdir = f'data/clips/{zipfilename}'

#
startIndex = 875
temppath = f'data/temp/{zipfilename}_{now}'
if not os.path.exists(temppath):
    os.makedirs(temppath)
fileno = 0
with zipfile.ZipFile(zipdir) as zf:
    noOfClips = len(zf.infolist())
    for zippedfile in zf.infolist():
        fileno += 1
        if fileno < startIndex:
            continue
        zf.extract(zippedfile, temppath)
        tempfilename = zippedfile.filename
        tempfile = f'{temppath}/{tempfilename}'
        print(tempfile)
        vidcap = cv2.VideoCapture(tempfile)
        success, image = vidcap.read()
        count = 0

        # positive

        if not os.path.exists(f'data/frames'):
            os.makedirs(f'data/frames')
        if not os.path.exists(f'data/frames/positive'):
            os.makedirs(f'data/frames/positive')
        if not os.path.exists(f'data/frames/bus'):
            os.makedirs(f'data/frames/bus')
        if not os.path.exists(f'data/frames/lobby'):
            os.makedirs(f'data/frames/lobby')
        if not os.path.exists(f'data/frames/negative'):
            os.makedirs(f'data/frames/negative')
        if not os.path.exists(f'data/frames/waiting'):
            os.makedirs(f'data/frames/waiting')
        if not os.path.exists(f'data/frames/unsure'):
            os.makedirs(f'data/frames/unsure')

        grabevery = 50  # Show an image for judgement every x frames.
        width, height = image.shape[:2]
        font = cv2.FONT_HERSHEY_SIMPLEX
        while success:
            if count % grabevery == 0:
                textimage = image.copy()
                cv2.putText(textimage, f'{fileno} of { noOfClips} clips',
                            (0, 20), font, .6, (255, 0, 20), 2, cv2.LINE_AA)
                cv2.putText(textimage, 'Enter G or P  if this is gameplay',
                            (int(width/2), 20), font, .6, (0, 0, 20), 2, cv2.LINE_AA)
                cv2.putText(textimage, 'Enter F or N  if this is a negative',
                            (int(width/2),  45), font, .6, (0, 0, 0), 2, cv2.LINE_AA)
                cv2.putText(textimage, 'Enter B if the player is flying on the bus',
                            (int(width/2), 70), font, .6, (0, 0, 0), 2, cv2.LINE_AA)
                cv2.putText(textimage, 'Enter L if the player is in the lobby or on a loading screen',
                            (int(width/2),  95), font, .6, (0, 0, 0), 2, cv2.LINE_AA)
                cv2.putText(textimage, 'Enter W if the player is waiting for a game to fill',
                            (int(width/2),  120), font, .6, (0, 0, 0), 2, cv2.LINE_AA)
                cv2.putText(textimage, 'Enter U if you can\'t quite classify',
                            (int(width/2), 145), font, .6, (0, 0, 0), 2, cv2.LINE_AA)
                cv2.putText(textimage, 'Enter Q to quit',
                            (int(width/2), 165), font, .6, (0, 0, 0), 2, cv2.LINE_AA)
                cv2.imshow("Image", textimage)

                picResponse = cv2.waitKey()
                print(picResponse)
                frameNo = int(count/grabevery)
                clipname = f'{os.path.splitext(tempfilename)[0]}_{int(frameNo)}'

                if picResponse == 103 or picResponse == 112:  # G or P means it's a valid game screen
                    cv2.imwrite(f"data/frames/positive/{clipname}.jpg",
                                image)     # save frame as JPEG file
                elif picResponse == 98:  # B means they're on bus waiting to drop in
                    cv2.imwrite(f"data/frames/bus/{clipname}.jpg",
                                image)     # save frame as JPEG file
                elif picResponse == 102 or picResponse == 110:  # F or N means they failed and this goes to negative
                    cv2.imwrite(f"data/frames/negative/{clipname}.jpg",
                                image)     # save frame as JPEG file
                elif picResponse == 108:  # L means they are Lobby
                    cv2.imwrite(f"data/frames/lobby/{clipname}.jpg",
                                image)     # save frame as JPEG file
                elif picResponse == 119:  # W means they are Waiting to fill the party
                    cv2.imwrite(f"data/frames/waiting/{clipname}.jpg",
                                image)     # save frame as JPEG file
                elif picResponse == 117:  # U means they are Unsure how to classify this image
                    cv2.imwrite(f"data/frames/unsure/{clipname}.jpg",
                                image)     # save frame as JPEG file
                if picResponse == 113:  # Q means Quit
                    bail = True
                    break
            if bail:
                break
            success, image = vidcap.read()
            count += 1

        if bail:
            break
vidcap.release()
if not bail:
    shutil.move(f'data/clips/{zipfilename}',
                f'data/clips/processed/{zipfilename}')
shutil.rmtree(temppath)
