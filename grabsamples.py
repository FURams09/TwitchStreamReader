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
game = getterconfig['game']
tempDirectory = config['DIRECTORY']['TEMP']
workingdir = os.path.join(tempDirectory, 'streams', game)

print(os.path.exists('smb:\\\\blanket/FortniteData'))
if not os.path.exists(os.path.join(tempDirectory, 'streams')):
    os.makedirs(os.path.join(tempDirectory, 'streams'))
if not os.path.exists(workingdir):
    os.makedirs(workingdir)

gameurl = urllib.parse.quote(game)  
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
for k in range(clipstograb):
    print(f'Starting Pass {k}')
    for j in range(len(data)):
        # try:
            username = data[j]['user_name']
            gameurl = f'http://twitch.tv/{username}'
            now = strftime("%y%m%d_%H%M%S", gmtime())
            gamestreams = streamlink.streams(gameurl)
            #TODO: Allow for different levels of quality
            if 'best' in gamestreams:
                print(f'Grabbing clip #{k+1} for stream {j}-{gameurl}')
                streamDir = os.path.join(workingdir, username)
                if not os.path.exists(streamDir):
                    os.makedirs(streamDir)
                fname = os.path.join(streamDir, f'{username}_{now}.mpg')
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
        # except:
        #     continue

now = strftime("%y%m%d_%H%M%S", gmtime())
clipsDir = config['DIRECTORY']['clipsstorage']
if not os.path.exists(clipsDir):
    os.makedirs(clipsDir)
zipfileName = os.path.join(clipsDir,f'{game}_{now}.zip' )
zf = zipfile.ZipFile(zipfileName, 'w')
for dirname, subdirs, files in os.walk(f'{workingdir}'):
    for filename in files:
        zf.write(os.path.join(dirname, filename), filename)
shutil.rmtree(workingdir)
