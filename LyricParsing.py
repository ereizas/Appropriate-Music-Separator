#look for more APIs because lyrist limits you to 150 requests per hour and the genius one is slow
"""
Author: Eric Reizas
This file is meant to provide functions that help determine whether songs are inappropriate for children based on lyrics.
"""
import requests, config
from lyricsgenius import Genius
import azapi

##decrypts the Vigenere cypher and returns a list of the inappropriate words to look for
def getInappropWordList(file):
    """
    Decrypts the Vigenere cypher and returns a list of the inappropriate words to look for

    @param file (str): name of the file with the encrypted words
    @return inappropWordList (str[]): list of decrypted inappropriate words
    """

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
    """
    Looks the inappropriate word list and determines if any appear for the Lyrist lyrics of one song

    @param strArtists (str): artist names
    @param songTitleFormatted (str): song title with certain characters formatted for url
    @param inappropWordList (str[]): list of inappropriate words
    @return : None on error, False if none of the words from inappropWordList appear, or True if at least one does
    """

    response = requests.get('https://lyrist.vercel.app/api/' + songTitleFormatted + '/' + strArtists)
    lyrics = ''
    if(response.status_code==200):
        data = response.json()
        if('lyrics' in data):
            lyrics=data['lyrics']
            print("Retrieved Lyrist Lyrics")
            for word in inappropWordList:
                if word in lyrics:
                    return True
            return False
        else:
            print("Could not retrieve lyric data")
            return None
    else:
        print("Error in retrieving lyric data")
        return None
        
def parseGeniusLyrics(artists, songTitle,inappropWordList):
    """
    Looks the inappropriate word list and determines if any appear for the Genius lyrics of one song

    @param strArtists (str): artist names
    @param songTitle
    @param inappropWordList (str[]): list of inappropriate words
    @return : None on error, False if none of the words from inappropWordList appear, or True if at least one does
    """
     
    clientID, clientSecret = config.geniusClientID,config.geniusClientSecret
    authResponse = requests.post('https://api.genius.com/oauth/token', {
    'grant_type': 'client_credentials',
    'client_id': clientID,
    'client_secret': clientSecret,
    })
    authResponseData = authResponse.json()
    accessToken = authResponseData['access_token']
    genius = Genius(access_token=accessToken,timeout=5,retries=3)
    song = ''
    try:
        song = genius.search_song(title=songTitle,artist=artists,get_full_info=False)
    except:
        pass
    if(song!=None):
        print("Retrieved Genius Lyrics")
        for word in inappropWordList:
            if word in song.lyrics:
                return True
        return False
    else:
        return None

def parseAZLyrics(artists, songTitle,inappropWordList):
    api = azapi.AZlyrics()
    api.artist=artists
    api.title=songTitle
    lyrics=api.getLyrics()
    if type(lyrics) is not int:
        print("Retrieved AZ Lyrics")
        for word in inappropWordList:
            if word in lyrics:
                return True
        return False
    else:
        return None 