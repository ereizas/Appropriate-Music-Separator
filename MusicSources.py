import requests, base64

def spotify(link):
    playlistID, appropSongIds, nonAppropSongIds = '', [], []
    #need clientID and clientSecret from a Spotify account to get an access token required to access the API
    clientID, clientSecret = '',''
    authResponse = requests.post('https://accounts.spotify.com/api/token', {
    'grant_type': 'client_credentials',
    'client_id': clientID,
    'client_secret': clientSecret,
    })
    authResponseData = authResponse.json()
    accessToken = authResponseData['access_token']
    headers = {'Authorization': 'Bearer {token}'.format(token=accessToken)}
    data = {}
    if('?' in link):
        playlistID = link[link.index('playlist/')+9:link.index('?')]
    else:
        playlistID = link[link.index('playlist/')+9:]
    response = requests.get('https://api.spotify.com/v1/playlists/'+playlistID+'/tracks',headers=headers)
    data = response.json() 
    moreSongsLeft = True
    while(moreSongsLeft):
        for item in data['items']:
            if item['track']['explicit']:
                nonAppropSongIds.append(item['track']['id'])
                continue
            else:
                pass
        if(data['next']!=None):
            response = requests.get(data['next'],headers=headers)
            data=response.json()
        else:
            moreSongsLeft=False
    


    

print(spotify('https://open.spotify.com/playlist/31hXsTQWKdum0YD6eHzLGf?si=yCdM_Gg_S6yI10rHweJl3Q'))

def appleMusic(link):
    pass

def youtube(link):
    pass

def soundcloud(link):
    pass

def folder(link):
    pass

def m3u(link):
    pass