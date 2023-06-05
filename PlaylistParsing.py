import requests, LyricParsing, config

def getAppropSpotifySongs(link: str)->list[str]:
    """
    This function is meant to parse the Spotfiy playlist data to retrieve the Spotify ids for the appropriate songs and update and return an array with those ids.
    
    @param link : link to playlist
    @return appropSongIds : list with string Spotify ids of the appropriate songs in the playlist
    """
    playlistID, appropSongIds= '', []
    authResponse = requests.post('https://accounts.spotify.com/api/token', {
    'grant_type': 'client_credentials',
    'client_id':  config.spotifyClientID,
    'client_secret': config.spotifyClientSecret,
    })
    authResponseData = authResponse.json()
    accessToken = authResponseData['access_token']
    headers = {'Authorization': 'Bearer {token}'.format(token=accessToken)}
    #extracts playlist id from the two types of spotify links
    if('?' in link):
        playlistID = link[link.index('playlist/')+9:link.index('?')]
    else:
        playlistID = link[link.index('playlist/')+9:]
    response = requests.get('https://api.spotify.com/v1/playlists/'+playlistID+'/tracks',headers=headers)
    data = response.json()
    moreSongsLeft = True
    while(moreSongsLeft):
        #index for lyricParsers (declared later)
        lyricParsersInd = 0
        for item in data['items']:
            if not item['track']['explicit']:
                artists,artistsFormatted, songTitle, songTitleFormatted = [], [], item['track']['name'], ''
                for artist in item['track']['artists']:
                    artists.append(artist['name'])
                    if(artist['name'] not in songTitle):
                        artistsTemp = ''
                        for char in artist['name']:
                            if char not in '\^~`[]}{|\'\"<>#%/?@!$&=,+;:':
                                artistsTemp+=char
                            else:
                                artistsTemp+=hex(ord(char))
                        artistsTemp.replace("0x","0%")
                        artistsFormatted.append(artistsTemp)
                for char in songTitle:
                    if char not in '\^~`[]}{|\'\"<>#%/?@!$&=,+;:':
                        songTitleFormatted+=char
                    else:
                        songTitleFormatted+=hex(ord(char))
                songTitleFormatted=songTitleFormatted.replace('0x','0%')
                inappropWordList = LyricParsing.getInappropWordList("InappropriateWords.txt")
                songInapprop = None
                #number for how many lyric parsing functions return None
                numNoneRetVals = 0
                lyricParsers = [LyricParsing.parseAZLyrics,LyricParsing.parseLyristLyrics,LyricParsing.parseGeniusLyrics]
                artistsFormatted='%20'.join(artistsFormatted)
                artists=' '.join(artists)
                while(songInapprop==None):
                    if lyricParsersInd<2:
                        songInapprop = lyricParsers[lyricParsersInd](artistsFormatted,songTitleFormatted,inappropWordList)
                    else:
                        songInapprop = lyricParsers[lyricParsersInd](artists,songTitle,inappropWordList)
                    lyricParsersInd=(lyricParsersInd+1)%len(lyricParsers)
                    if songInapprop==None:
                        numNoneRetVals+=1
                        if(numNoneRetVals==len(lyricParsers)):
                            numNoneRetVals=0
                            lyricParsersInd=(lyricParsersInd+1)%len(lyricParsers)
                            break
                    elif songInapprop==False:
                        appropSongIds.append(item['track']['id'])
                        numNoneRetVals=0
                    else:
                        numNoneRetVals=0
        if(data['next']!=None):
            response = requests.get(data['next'],headers=headers)
            data=response.json()
        else:
            moreSongsLeft=False
    return appropSongIds

def getAppropAppleSongs(link):
    pass

def getAppropYTSongs(link):
    pass

def getAppropSouncloudSongs(link):
    pass

def getAppropFolderSongs(link):
    pass

def getAppropM3USongs(link):
    pass
