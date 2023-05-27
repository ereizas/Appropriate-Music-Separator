import requests, config

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

def lyristLyrics(strArtists,songTitleFormatted):
    response = requests.get('https://lyrist.vercel.app/api/' + songTitleFormatted + '/' + strArtists)
    lyrics = ''
    data = response.json()
    if(response.status_code==200):
        lyrics=data['lyrics']

def geniusLyrics(artists,strArtists, songTitle, songTitleFormatted):
    clientID, clientSecret = config.geniusClientID,config.geniusClientSecret
    authResponse = requests.post('https://api.genius.com/oauth/token', {
    'grant_type': 'client_credentials',
    'client_id': clientID,
    'client_secret': clientSecret,
    })
    authResponseData = authResponse.json()
    accessToken = authResponseData['access_token']
    geniusReqHeaders = {'Authorization': 'Bearer {token}'.format(token=accessToken)}
    geniusSearchResponse = requests.get("https://api.genius.com/search?q="+ '%20'.join(strArtists)+'%20'+songTitleFormatted,headers=geniusReqHeaders)
    geniusSearchData = geniusSearchResponse.json()
    print(' '.join(artists) + '-' + songTitle + '\n')
    for hit in geniusSearchData['response']['hits']:
        artistsAllPresent = True
        for artist in artists:
            if artist.lower() not in hit['result']['artist_names'].lower():
                print(hit['result']['id'])
                print(hit['result']['artist_names'].lower()+'\n')
                artistsAllPresent=False
                break
        if not artistsAllPresent:
            continue
        elif hit['result']['language'] == 'en' and songTitle in hit['result']['full_title']:
            songResponse = requests.get('https://api.genius.com/songs/' + str(hit['result']['id']) + '?text_format=plain',headers=geniusReqHeaders)
            songData = songResponse.json()
            print(songData['response']['song']['embed_content'] + '\n')
            break
