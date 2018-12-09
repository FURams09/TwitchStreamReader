import os
import json
import cv2
import shutil

assetdir = 'data/assets'
key = 'AllMaterial'

REBUILD_FOLDER = False


if not os.path.exists(assetdir):
    os.makedirs(assetdir)
outdir = f'{assetdir}/{key}'

if REBUILD_FOLDER:
    shutil.rmtree(outdir)
if not os.path.exists(outdir):
    os.makedirs(outdir)
negativedir = f'data/frames/negative'


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
    os.remove(f'{negativedir}/negatives.txt')
except:
    pass
for negative in os.listdir(negativedir):
    with open(f'{negativedir}/negatives.txt', 'a+') as outfile:
        # newfile = f'{outfile}\n{croppedimname}'
        outfile.write(f'\n{negative}')
