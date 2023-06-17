"""
Author: Eric Reizas
This file is meant to provide functions that help determine whether songs are inappropriate for children based on lyrics.
"""
import requests, config
from lyricsgenius import Genius
import azapi
from youtube_transcript_api import YouTubeTranscriptApi
#declared globally to allow fair cycling and easing of the workload of lyrics apis in findAndParseLyrics()
lyricParsersInd = 0
##decrypts the Vigenere cypher and returns a list of the inappropriate words to look for
def getInappropWordList(file: str)->list[str]:
    """
    Decrypts the Vigenere cypher and returns a list of the inappropriate words to look for
    @param file : name of the file with the encrypted words
    @return inappropWordList
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

def parseLyristLyrics(strArtists: str,songTitleFormatted: str,inappropWordList: list[str]):
    """
    Looks through the inappropriate word list and determines if any appear for the Lyrist lyrics of one song
    @param strArtists : artist names
    @param songTitleFormatted : song title with certain characters formatted for url
    @param inappropWordList
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
        
def parseGeniusLyrics(artists: list, songTitle: str, inappropWordList: list[str]):
    """
    Looks through the inappropriate word list and determines if any appear for the Genius lyrics of the song
    @param artists : artist names
    @param songTitle
    @param inappropWordList
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
    song = None
    #added the join here so that it would not alter artists for if parseLyristLyrics() needs the formatted string
    artists = ' '.join(artists)
    try:
        song = genius.search_song(title=songTitle,artist=artists,get_full_info=False)
    except Exception as e:
        print(e)
        pass
    if(song!=None):
        print("Retrieved Genius Lyrics")
        for word in inappropWordList:
            if word in song.lyrics:
                return True
        return False
    else:
        return None

def parseAZLyrics(artists: list, songTitle: str,inappropWordList: list[str]):
    """
    Looks through inappropriate word list and determines if any appear in the lyrics retrieved from the AZ Lyrics API
    @param artists : artist names
    @param songTitle
    @param inappropWordList
    @return : None on error, False if none of the words from inappropWordList appear, or True if at least one does
    """
    
    api = azapi.AZlyrics()
    #added the join here so that it would not alter artists for if parseLyristLyrics() needs the formatted string
    artists = ' '.join(artists)
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

def parseYTTranscript(id:str, inappropWordList:list[str]):
    """
    This function retrieves and parses a transcript that is either auto-generated or manually entered and looks to see if any of the inappropriate words appear.
    @param id : YouTube id for the video
    @param inappropriateWordList
    @return : True if any word from inappropWordList appears, False if none of them do, or None on error
    """
    
    try:
        transcript = YouTubeTranscriptApi.get_transcript(id)
        for word in inappropWordList:
            for blurb in transcript:
                if word in blurb['text']:
                    return True
        return False
    #later do except (error name) for language unavailable errors and other recoverable errors
    except Exception as e:
        print(e)
        return None

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

def findAndParseLyrics(artists:list, songTitle:str, appropSongIDs:list, id:str, ytResource):
    """
    This function cycles through the lyric APIs (and YouTube transcript if none of the APIs can get results) and adds to appropSongIDs if the lyric API functions return False
    @param artists
    @param songTitle
    @param appropSongIDs : list of ids for a certain platform for appropriate songs 
    @param id : id given by a certain platform for the song
    @param ytResource : YouTube object with the necessary credentials to request data from the YouTube API
    """
    artistsFormatted, songTitleFormatted = [], ''
    inappropWordList = getInappropWordList("InappropriateWords.txt")
    #boolean for if the song with id is inappropriate, assigned None if the api whose turn it is could not find anything or received an error
    songInapprop = None
    #number for how many lyric parsing functions return None for the current song
    numNoneRetVals = 0
    lyricParsers = [parseAZLyrics,parseLyristLyrics,parseGeniusLyrics]
    global lyricParsersInd
    while(songInapprop==None and numNoneRetVals<len(lyricParsers)):
        numNoneRetVals+=1
        if lyricParsersInd != 1:
            songInapprop = lyricParsers[lyricParsersInd](artists,songTitle,inappropWordList)
        else:
            #can make into format functions
            if not artistsFormatted:
                artistsFormatted = formatArtists(artists)
            if not songTitleFormatted:
                songTitleFormatted = formatSongTitle(songTitle)
            songInapprop = lyricParsers[lyricParsersInd](artistsFormatted,songTitleFormatted,inappropWordList)
        #rotates the lyric APIs
        lyricParsersInd=(lyricParsersInd+1)%len(lyricParsers)
        if songInapprop==False:
            appropSongIDs.append(id)
            #completes the function so that that parseYTTranscript() won't be called unnecessarily
            return
    if ytResource:
        parseYTTranscrRetVal = parseYTTranscript(id,inappropWordList)
        if parseYTTranscrRetVal==False:
            appropSongIDs.append(id)