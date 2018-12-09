import cv2
import numpy as np
import os
import json
import random

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

with open('data/assets/positives.json', 'r') as outfile:
    positives = json.load(outfile)
    while not newFileFound:
        fileindex = random.randint(0, len(os.listdir(positivedir)) - 1)
        filename = os.listdir(positivedir)[fileindex]
        if not filename in positivedir:
            newFileFound = True

i = 0
im = cv2.imread(f'{positivedir}/{filename}')
width, height = im.shape[:2]

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
    print(f'deleted file {filename}')
    os.remove(f'{positivedir}/{filename}')
elif not bail:
    with open('data/assets/positives.json', 'r') as outfile:
        positives = json.load(outfile)
        positives[os.path.splitext(filename)[0]] = assetBoundaries
    with open('data/assets/positives.json', 'w') as outfile:
        json.dump(positives, outfile)
