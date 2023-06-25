"""
Author: Eric Reizas
This file is meant to provide functions that help determine whether songs are inappropriate for children based on lyrics.
"""
import requests, config, StrParsing
from lyricsgenius import Genius
import azapi
from youtube_transcript_api import YouTubeTranscriptApi
import traceback
#declared globally to allow fair cycling and easing of the workload of lyrics apis in findAndParseLyrics()
lyricParsersInd = 0
#decrypts the Vigenere cypher and returns a list of the inappropriate words to look for
def getInappropWordList(file: str)->list[str]:
    """
    Decrypts the Vigenere cypher and returns a list of the inappropriate words to look for
    @param file : name of the file with the encrypted words
    @return inappropWordList
    """

    inappropWordList = []
    read_file = ''
    try:
        read_file = open(file,"r")
    except Exception as e:
        print(e)
        exit(1)
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

def parseLyristLyrics(strArtists: str,songTitleFormatted: str,inappropWordList: list[str]):
    """
    Looks through the inappropriate word list and determines if any appear for the Lyrist lyrics of one song
    @param strArtists : artist names
    @param songTitleFormatted : song title with certain characters formatted for url
    @param inappropWordList
    @return : None on error, False if none of the words from inappropWordList appear, or True if at least one does
    """
    response = dict()
    try:
        response = requests.get('https://lyrist.vercel.app/api/' + songTitleFormatted + '/' + strArtists)
    except Exception as e:
        print(e)
        return None
    lyrics = ''
    if(response.status_code>199 and response.status_code<300):
        data = response.json()
        if('lyrics' in data):
            lyrics=data['lyrics']
            for word in inappropWordList:
                if word in lyrics:
                    return True
            return False
        else:
            return None
    else:
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
    genius = Genius(access_token=accessToken,timeout=5,retries=3,verbose=False)
    song = None
    #added the join here so that it would not alter artists for if parseLyristLyrics() needs the formatted string
    artists = ' '.join(artists)
    try:
        song = genius.search_song(title=songTitle,artist=artists,get_full_info=False)
    except Exception as e:
        print(e)
        return None
    if(song!=None):
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
    @return : True if there is an index error when accessing metadata[1] in the azapi library code, False otherwise
    """
    
    api = azapi.AZlyrics()
    #added the join here so that it would not alter artists for if parseLyristLyrics() needs the formatted string
    artists = ' '.join(artists)
    api.artist=artists
    api.title=songTitle
    lyrics = ''
    try:
        lyrics=api.getLyrics() 
    except Exception as e:
        print(e)
        #This accounts for when instead of normal metadata being returned, an array with one element is returned saying that there has been unusual activity coming from the IP address of the user.
        if 'metadata[1]' in traceback.format_exc():
            return None,True
        return None,False
    if type(lyrics) != int:
            for word in inappropWordList:
                if word in lyrics:
                    return True, False
            return False, False
    else:
        return None, False

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

def findAndParseLyrics(artists:list, songTitle:str, appropSongIDs:list, id:str, azUnusActErrOccurred:bool,reqsSinceLastAZReq:int,ytResource):
    """
    This function cycles through the lyric APIs (and YouTube transcript if none of the APIs can get results) and adds the given song id to appropSongIDs if the any of lyric API functions return False
    @param artists
    @param songTitle
    @param appropSongIDs : list of ids for a certain platform for appropriate songs 
    @param id : id given by a certain platform for the song
    @param azUnusActErrOccurred : boolean indicating whether an error occurred recently with AZ Lyrics pertaining to unusual activity coming from the user IP address
    @param reqsSinceLastAZReq : keeps track of the number of requests since the last AZ API request so that another request can be attempted after a certain amount of other API requests
    @param ytResource : YouTube object with the necessary credentials to request data from the YouTube API
    @return azUnusActErrOccurred : boolean for if the AZ Lyric API libary variable "metadata" has a message about unusual activity as its first element
    @return reqsSinceLastAZReq : number of requests since the last AZ API request
    """
    inappropWordList = getInappropWordList("InappropriateWords.txt")
    #boolean for if the song with id is inappropriate, assigned None if the api whose turn it is could not find anything or received an error
    songInapprop = None
    #number for how many lyric parsing functions return None for the current song
    numNoneRetVals = 0
    lyricParsers = [parseAZLyrics,parseLyristLyrics,parseGeniusLyrics]
    global lyricParsersInd
    while(songInapprop==None and numNoneRetVals<len(lyricParsers)):
        numNoneRetVals+=1
        if lyricParsersInd==1:
            songInapprop = lyricParsers[lyricParsersInd](StrParsing.formatArtists(artists),StrParsing.formatSongTitle(songTitle),inappropWordList)
            if azUnusActErrOccurred:
                reqsSinceLastAZReq+=1
            #resets the variable to allow another attempt at an AZ API request
            if reqsSinceLastAZReq==100:
                azUnusActErrOccurred = False
                reqsSinceLastAZReq=0
        elif lyricParsersInd == 2:
            songInapprop = lyricParsers[lyricParsersInd](artists,songTitle,inappropWordList)
            if azUnusActErrOccurred:
                reqsSinceLastAZReq+=1
            #resets the variable to allow another attempt at an AZ API request
            if reqsSinceLastAZReq==100:
                azUnusActErrOccurred = False
                reqsSinceLastAZReq=0
        elif not azUnusActErrOccurred:
            songInapprop,azUnusActErrOccurred = lyricParsers[lyricParsersInd](artists,songTitle,inappropWordList)
        #rotates the lyric APIs
        lyricParsersInd=(lyricParsersInd+1)%len(lyricParsers)
        if songInapprop==False:
            appropSongIDs.append(id)
    #if all the lyric APIs have been cycled through and a resource for requesting info from the YT API has been passed
    if songInapprop==None and ytResource:
        parseYTTranscrRetVal = parseYTTranscript(id,inappropWordList)
        if parseYTTranscrRetVal==False:
            appropSongIDs.append(id)
    #returns these so that their updated values can be referenced when parsing the next song's lyrics
    return azUnusActErrOccurred,reqsSinceLastAZReq