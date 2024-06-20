import mutagen
import os

path = './'
allItems = os.listdir(path)
musicItems = [item for item in allItems if os.path.isfile(os.path.join(path, item)) and mutagen.File(item) != None]
query = None

for item in musicItems:
    audio = mutagen.File(item, easy=True)
    print(f"Processing: {audio.filename}")
    if "artist" in audio.tags:
        print(f"artist: {audio.tags["artist"]}")    
    if "title" in audio.tags:
        print(f"title: {audio.tags["title"]}")    
    if "album" in audio.tags:
        print(f"album: {audio.tags["album"]}")
    print();

# tag = {
#     "artist": "Something",
#     "album": "Another Thing"
# }

# audio.tags['artist'] = "Something"
# audio.tags['albumartist'] = "Another Thing"
# audio.tags['album'] = "Best Album"
# audio.save()
# print(audio.tags)