import requests, config
from lyricsgenius import Genius

##decrypts the Vigenere cypher and returns a list of the inappropriate words to look for
def getInappropWordList(file):
    inappropWordList = []
    read_file = open(file,"r")
    lines = read_file.readlines()
    for line in range(len(lines)):
        key = "music"
        temp = ""
        for c in range(len(lines[line])):
            if(ord(lines[line][c])>96):
                temp+=chr((((ord(lines[line][c])-97)-(ord(key[c%len(key)])-97))%26)+97)
            elif lines[line][c]!='\n':
                temp+=lines[line][c]
        inappropWordList.append(temp)
    return inappropWordList

#these functions return a boolean value: true for appropriate, false for not

def parseLyristLyrics(strArtists,songTitleFormatted,inappropWordList):
    response = requests.get('https://lyrist.vercel.app/api/' + songTitleFormatted + '/' + strArtists)
    lyrics = ''
    data = response.json()
    if(response.status_code==200 and 'lyrics' in data):
        lyrics=data['lyrics']
        for word in inappropWordList:
            if word in lyrics:
                return True
        return False
    else:
        return None
        

def parseGeniusLyrics(artists, songTitle,inappropWordList):
    clientID, clientSecret = config.geniusClientID,config.geniusClientSecret
    authResponse = requests.post('https://api.genius.com/oauth/token', {
    'grant_type': 'client_credentials',
    'client_id': clientID,
    'client_secret': clientSecret,
    })
    authResponseData = authResponse.json()
    accessToken = authResponseData['access_token']
    genius = Genius(accessToken)
    print(' '.join(artists) + '-' + songTitle + ':\n')
    song = genius.search_song(artist = ' '.join(artists), title=songTitle)
    print(song.lyrics)
