import requests, LyricParsing, config
from bs4 import BeautifulSoup

def parseSpotifyPlaylist(link):
    playlistID, appropSongIds= '', []
    #need clientID and clientSecret from a Spotify account to get an access token required to access the API
    clientID, clientSecret = config.spotifyClientID,config.spotifyClientSecret
    authResponse = requests.post('https://accounts.spotify.com/api/token', {
    'grant_type': 'client_credentials',
    'client_id': clientID,
    'client_secret': clientSecret,
    })
    authResponseData = authResponse.json()
    accessToken = authResponseData['access_token']
    headers = {'Authorization': 'Bearer {token}'.format(token=accessToken)}
    data = {}
    #extracts playlist id from the two types of spotify links
    if('?' in link):
        playlistID = link[link.index('playlist/')+9:link.index('?')]
    else:
        playlistID = link[link.index('playlist/')+9:]
    response = requests.get('https://api.spotify.com/v1/playlists/'+playlistID+'/tracks',headers=headers)
    data = response.json() 
    moreSongsLeft = True
    while(moreSongsLeft):
        for item in data['items']:
            if not item['track']['explicit']:
                artists,strArtists, songTitle, songTitleFormatted = [], [], item['track']['name'], ''
                for artist in item['track']['artists']:
                    if(artist['name'] not in songTitle):
                        strArtists.append(artist['name'].replace(' ','%20'))
                        artists.append(artist['name'])
                for char in songTitle:
                    if char in '\^~`[]}{|\'\"<>#%/?@!$&=,+;:':
                        songTitleFormatted+=hex(ord(char))
                    else:
                        songTitleFormatted+=char
                songTitleFormatted=songTitleFormatted.replace('0x','0%')
                inappropWordList = LyricParsing.getInappropWordList("InappropriateWords.txt")
                lyristInapprop = LyricParsing.parseLyristLyrics('%20'.join(strArtists),songTitleFormatted,inappropWordList)
                if lyristInapprop == False:
                    appropSongIds.append(item['track']['id'])
                    print(item['track']['artists'][0]['name'] + ' - ' + item['track']['name'])
                elif lyristInapprop == None:
                    geniusInapprop = LyricParsing.parseGeniusLyrics(artists,songTitle,inappropWordList)
                    if geniusInapprop==False:
                        appropSongIds.append(item['track']['id'])
                        print(item['track']['artists'][0]['name'] + ' - ' + item['track']['name'])
        if(data['next']!=None):
            response = requests.get(data['next'],headers=headers)
            data=response.json()
        else:
            moreSongsLeft=False
    return appropSongIds

print(parseSpotifyPlaylist('https://open.spotify.com/playlist/3Zc0vSZnaQK9eJvhnvnWpi'))

def parseAppleMusicPlaylist(link):
    pass

def parseYoutubePlaylist(link):
    pass

def parseSoundcloudPlaylist(link):
    pass

def parseFolderPlaylist(link):
    pass

def parseM3uPlaylist(link):
    pass