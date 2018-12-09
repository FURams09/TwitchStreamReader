## Data directory

These files should be created if they do not exist when being used.

data/
-- clips/ zip files of streams grabbed for analysis.

-- frames/ Where to store process frames from streams. Can be any of the following categories.
lobby, bus, inventory are states that will probably be important and should be saved

---- positive/ Game footage basically from dropping in to dying or victory royale when the main hud is visible
---- negative/ Anything not Fortnite, other games, just the streamer face, excessive banners.
---- lobby/ Pre waiting screen where you have your menus up.
---- waiting/ the free for all where you wait for the game
---- bus/ after lobby but before dropping in. Not if you're in free fall, that should be positive
---- unsure/ if you don't think it fits easily in any of the above category just throw it here and see if there's another category. Don't sweat it there's a lot of fortnight.

-- temp/ when pulling frames for review this is where the zipped movie files will be saved. Should not put anything here that can't be deleted at random. Should never feel bad about deleting this folder.

-- working/ When grabbing streams in accordance with the config, this is where the files are saved before being zipped and archived in /clips
