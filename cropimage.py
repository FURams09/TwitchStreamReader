import json

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

with open('data/assets/positives.json', 'r') as outfile:
    positives = json.load(outfile)

print(positives)

for frame in positives:
    for i in range(len(boundaries)):
        a = boundaries[i]
        if a in positives[frame]:
            print(f'data/frames/positive/{frame}', a, positives[frame][a])
