def getSpotifyPlaylistID(link:str):
    """
    Retrieves playlist ID for Spotify playlist based on link given
    @param : link to Spotify playlist
    @return : the Spotify playlist ID on success, otherwise None on failure
    """
    try:
        if('?' in link):
            return link[link.index('playlist/')+9:link.index('?')]
        else:
            return link[link.index('playlist/')+9:]
    except Exception as e:
        return None

def getYTPlaylistID(link:str):
    """
    Retrieves playlist ID for YouTube or YouTube Music playlist based on link given
    @param link : link to YouTube or YouTube Music playlist
    """
	
    try:
        lastInd = link.rfind('&')
        listEqInd = link.find('list=')
        if(lastInd<listEqInd):
            lastInd = len(link)
        return link[listEqInd+5:lastInd]
    except:
        return None

def formatArtists(artists:list[str])->str:
    """
    This function formats the artists names in URL format.
    @param artists
    @return : string formatted for url
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
    @return : string formatted for url
    """
    songTitleFormatted = ''
    for char in songTitle:
        if char not in '\^~`[]}{|\'\"<>#%/?@!$&=,+;: ':
            songTitleFormatted+=char
        else:
            songTitleFormatted+=hex(ord(char))
    return songTitleFormatted.replace('0x','%')

def getStrAppropSongIDs(appropSongIDs:list[str],firstInd:int=0):
    """
    Returns a string version of song ids to be later inputted into the appropriate part of the GUI
    @param appropSongIDs : list of song ids deemed appropriate for children
    @param firstInd : first index of the splice of remaining appropriate song IDs
    """
    strAppropSongIDs = ''
    for id in appropSongIDs[firstInd:]:
        strAppropSongIDs+=id + ' '
    return strAppropSongIDs.strip()
