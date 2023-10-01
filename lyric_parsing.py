import requests, config, str_parsing
from lyricsgenius import Genius
import azapi
from youtube_transcript_api import YouTubeTranscriptApi
from traceback import format_exc
#declared globally to allow fair cycling and easing of the workload of lyrics apis in findAndParseLyrics()
lyricParsersInd = 0
#creates list of proxies to use AZ API to avoid IP ban
proxDict = dict()
try:
    proxReqResponse = requests.get('https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=US&ssl=all&anonymity=all')
    proxDict = {'http':proxReqResponse.text.split('\r\n')[:-1][0]}
except Exception as e:
    print(e)

def getInappropWordList(file: str)->list[str]|None:
    """
    Decrypts the Vigenere cypher and returns a list of the inappropriate words to look for
    @param file : name of the file with the encrypted words
    @return inappropWordList on success or None on error
    """

    inappropWordList = []
    read_file = ''
    try:
        read_file = open(file,"r")
    except Exception as e:
        return None
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
        print('This error will not stop the program. This is only appearing to reveal how the lyric APIs are working. Error: ' + str(e))
        return None
    lyrics = ''
    #if status_code is valid
    if response.status_code>199 and response.status_code<300:
        data = response.json()
        if('lyrics' in data):
            lyrics=data['lyrics']
            for phrase in inappropWordList:
                if phrase in lyrics:
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

    authResponse = requests.post('https://api.genius.com/oauth/token', {
    'grant_type': 'client_credentials',
    'client_id': config.geniusClientID,
    'client_secret': config.geniusClientSecret,
    })
    if authResponse.status_code>199 and authResponse.status_code<300:
        authResponseData = authResponse.json()
        accessToken = authResponseData['access_token']
        genius = Genius(access_token=accessToken,timeout=5,retries=3,verbose=False)
        song = None
        #added the .join() here so that it would not alter artists for if parseLyristLyrics() needs the formatted string after if this function fails (returns None)
        artists = ' '.join(artists)
        try:
            song = genius.search_song(title=songTitle,artist=artists,get_full_info=False)
        except Exception as e:
            print('This error will not stop the program. This is only appearing to reveal how the lyric APIs are working. Error: ' + str(e))
            return None
        if(song!=None):
            for phrase in inappropWordList:
                if phrase in song.lyrics:
                    return True
            return False
        else:
            return None
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
    
    api = azapi.AZlyrics(proxies=proxDict)
    #added the join here so that it would not alter artists for if parseLyristLyrics() needs the formatted string after if this function returns None
    artists = ' '.join(artists)
    api.artist=artists
    api.title=songTitle
    lyrics = ''
    try:
        lyrics=api.getLyrics() 
    except Exception as e:
        print('This error will not stop the program. This is only appearing to reveal how the lyric APIs are working. Error: ' + str(e),flush=True)
        #This accounts for when instead of normal metadata being returned, an array with one element is returned saying that there has been unusual activity coming from the IP address of the user.
        if 'metadata[1]' in format_exc():
            return None,True
        return None,False
    #if the retrieval of lyrics did not fail
    if type(lyrics) != int:
            for phrase in inappropWordList:
                if phrase in lyrics:
                    return True, False
            return False, False
    else:
        return None, False

def parseYTTranscript(id:str, inappropWordList:list[str]):
    """
    Retrieves and parses a transcript that is either auto-generated or manually entered and looks to see if any of the inappropriate words appear
    @param id : YouTube id for the video
    @param inappropriateWordList
    @return : True if any word from inappropWordList appears, False if none of them do, or None on error
    """
    
    try:
        transcript = YouTubeTranscriptApi.get_transcript(id)
        for phrase in inappropWordList:
            for blurb in transcript:
                if phrase in blurb['text']:
                    return True
        return False
    #later do except (error name) for language unavailable errors and other recoverable errors
    except Exception as e:
        strError = str(e)
        if 'subtitle' not in strError and 'transcript' not in strError:
            print('This error will not stop the program. This is only appearing to reveal how the lyric APIs are working. Error: ' + strError)
        return None

def findAndParseLyrics(artists:list, songTitle:str, appropSongIDs:list, id:str, azUnusActErrOccurred:bool,reqsSinceLastAZReq:int,ytResource):
    """
    Cycles through the lyric APIs (and YouTube transcript if none of the APIs can get results) and adds the given song id to appropSongIDs if the any of lyric API functions return False
    @param artists
    @param songTitle
    @param appropSongIDs : list of ids for a certain platform for appropriate songs 
    @param id : id given by a certain platform for the song
    @param azUnusActErrOccurred : boolean for if the AZ Lyric API libary variable "metadata" has a message about unusual activity as its first element
    @param reqsSinceLastAZReq : number of requests since the last AZ API request
    @param ytResource : YouTube object with the necessary credentials to request data from the YouTube API
    @return azUnusActErrOccurred : boolean for if the AZ Lyric API libary variable "metadata" has a message about unusual activity as its first element
    @return reqsSinceLastAZReq : number of requests since the last AZ API request
    """
    inappropWordList = getInappropWordList("InappropriateWords.txt")
    if inappropWordList==None:
        return None, None
    #boolean for if the song with id is inappropriate, assigned None if the api whose turn it is could not find anything or received an error
    songInapprop = None
    #number for how many lyric parsing functions return None for the current song
    numNoneRetVals = 0
    lyricParsers = [parseAZLyrics,parseLyristLyrics,parseGeniusLyrics]
    global lyricParsersInd
    while(songInapprop==None and numNoneRetVals<len(lyricParsers)):
        numNoneRetVals+=1
        if lyricParsersInd==1:
            songInapprop = lyricParsers[lyricParsersInd](str_parsing.formatArtists(artists),str_parsing.formatSongTitle(songTitle),inappropWordList)
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
    #if all the lyric APIs have been cycled through without success and a resource for requesting info from the YT API has been passed
    if songInapprop==None and ytResource:
        parseYTTranscrRetVal = parseYTTranscript(id,inappropWordList)
        if parseYTTranscrRetVal==False:
            appropSongIDs.append(id)
    #returns these so that their updated values can be referenced when parsing the next song's lyrics
    return azUnusActErrOccurred,reqsSinceLastAZReq
