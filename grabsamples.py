import cv2
import numpy as np
import time
import http.client
import streamlink
import configparser
import json
import os
import shutil
from time import gmtime, strftime
import zipfile
import urllib
# use live streamer to figure out the stream info

config = configparser.ConfigParser()
config.read('config.ini')
connection = http.client.HTTPSConnection("api.twitch.tv")

getterconfig = config['STREAMGRAB']
topstreams = getterconfig['topstreams']
clipstograb = int(getterconfig['clipstograb'])
clipsseconds = int(getterconfig['clipsseconds'])
datadir = getterconfig['datadir']
game = getterconfig['game']

workingdir = f'{datadir}/working/{game}'
gameurl = urllib.parse.quote(game)
print(gameurl)
connection.request("GET", f"/helix/games?name={gameurl}",
                   headers={"Client-ID": config['TWITCH_API']['CLIENT_ID']})
response = connection.getresponse()
game_id = json.loads(response.read())['data'][0]['id']

# TODO: Add better logging

connection.request("GET", f"/helix/streams?game_id={game_id}&first={topstreams}",
                   headers={"Client-ID": config['TWITCH_API']['CLIENT_ID']})
response = connection.getresponse()
data = json.loads(response.read())['data']


# initialize directory to store images
if not os.path.exists(f'{datadir}'):
    os.makedirs(f'{datadir}')

if os.path.exists(f'{workingdir}'):
    shutil.rmtree(workingdir)
# delete workingdir
for k in range(clipstograb):
    print(f'Starting Pass {k}')
    for j in range(len(data)):
        try:
            username = data[j]['user_name']
            gameurl = f'http://twitch.tv/{username}'
            now = strftime("%y%m %d_%H%M%S", gmtime())
            key = f'{username}_{now}'
            gamestreams = streamlink.streams(gameurl)
            if 'best' in gamestreams:
                print(f'Grabbing #{k} for stream {j}-{gameurl}')
                if not os.path.exists(f'{workingdir}/{username}'):
                    os.makedirs(f'{workingdir}/{username}')

                fname = f"{workingdir}/{username}/{username}_{now}.mpg"
                vid_file = open(fname, "wb")
                # dump from the stream into an mpg file -- get a buffer going
                fd = gamestreams['best'].open()
                for i in range(0, 2*2048):
                    if i % 256 == 0:
                        new_bytes = fd.read(1024)
                        vid_file.write(new_bytes)
                timeout_start = time.time()
                while time.time() < timeout_start + clipsseconds:
                    if (0xFF & cv2.waitKey(5) == 27):
                        vid_file.close()
                        fd.close()
                        break
                    time.sleep(0.05)
                    # dump some more data to the stream so we don't run out.
                    new_bytes = fd.read(1024*16)
                    vid_file.write(new_bytes)
                vid_file.close()
                fd.close()
        except:
            continue

now = strftime("%y%m%d_%H%M%S", gmtime())
if not os.path.exists(f'{datadir}/clips'):
    os.makedirs(f'{datadir}/clips')
zf = zipfile.ZipFile(f'{datadir}/clips/{game}_{now}.zip', 'w')
for dirname, subdirs, files in os.walk(f'{workingdir}'):
    for filename in files:
        zf.write(os.path.join(dirname, filename), filename)
shutil.rmtree(workingdir)
