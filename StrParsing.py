def getYTPlaylistID(link:str):
	#given a playlist link from either a specific video on the list (which means the video id is in the playlist link) or just the playlist itself, lastAmpInd will be the needed end index for playlistID
	lastInd = link.rfind('&')
	listEqInd = link.find('list=')
	if(lastInd<listEqInd):
		lastInd = len(link)
	return link[listEqInd+5:lastInd]

def formatArtists(artists:list[str])->str:
    """
    This function formats the artists names in URL format.
    @param artists
    """
    artistsFormatted = []
    for artist in artists:
        artistsTemp = ''
        for char in artist:
            if char not in '\^~`[]}{|\'\"<>#%/?@!$&=,+;: ':
                artistsTemp+=char
            else:
                artistsTemp+=hex(ord(char))
        artistsFormatted.append(artistsTemp)
    #joins artists in the list with space as represented by a URL
    artistsFormatted='%20'.join(artistsFormatted)
    return artistsFormatted.replace('0x','%')

def formatSongTitle(songTitle:str)->str:
    """
    This function formats the song title in URL format.
    @param songTitle
    """
    songTitleFormatted = ''
    for char in songTitle:
        if char not in '\^~`[]}{|\'\"<>#%/?@!$&=,+;: ':
            songTitleFormatted+=char
        else:
            songTitleFormatted+=hex(ord(char))
    return songTitleFormatted.replace('0x','%')