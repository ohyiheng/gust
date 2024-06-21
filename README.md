# Spotify Autotagger

A python CLI utility to auto tag music files using metadata from Spotify, supports auto retrieval of:

- Track Title
- Artist(s)
- Album Title
- Album Artist
- Date
- Track Number
- Total Tracks
- Disc Number
- Total Discs

## Compatibility

Currently I've only developed this with a focus on Vorbis Comments, ID3 tags are supported but I haven't thoroughly tested it yet. I also don't yet know if this works APE and MP4 formats or not.

## TODO

- [x] Search and fetch tracks from Spotify
- [x] Add an option to choose from a list of query result
- [ ] Retreive album images
- [ ] Let users customise the behaviour of the program using config file
- [ ] Let users select the tags they want to write