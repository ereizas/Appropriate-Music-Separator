# Synopsis

This program is meant to take in a music playlist link or file with one or more songs and create a new playlist with only the songs appropriate for children. Even though songs may not be marked explicit, they can still have inappropriate references to things such as drugs, violence, etc. Those who use this program should still verify that each outputted playlist has appropriate songs based on their best judgement and lyric verification if needed, but given a playlist with a mix of inappropriate and appropriate songs, it should reduce the time it takes to check manually.

# Setup

Certain setups need to be completed before you run the program.

1. If you are inputting a Spotify playlist, go through the "Genius Lyric API Setup" and "Spotify Setup"

## Genius Lyric API Setup

This is what allows the program to request lyrics from Genius to analyze and pick out appropriate songs.

1. Go to https://genius.com/api-clients/new
2. Enter what you would like for the "App Name" field
3. Paste https://github.com/ereizas/Appropriate-Song-Separator into the "App Website URL" and click "Save"
4. Copy the Client ID and paste it into the single quote marks next to geniusClientID in the config.py file
5. Copy the Client Secret and paste it into the single quote marks next to geniusClientSecret in the same file

## Spotify Setup

You can skip steps 1-5 if you are **not** on a Windows machine. These steps are necessary in order to get some required info to put into the program.

1. Press the Windows button (or click on the search bar in the bottom left corner of your home screen)
2. Search "Control Panel" and click on the app
3. Click on "Programs"
4. Click on "Turn Windows features on or off"
5. Make sure "Internet Information Services" and "Internet Information Services Hostable Web Core" are checked and press "OK" if you had to checkmark either one
6. Go to https://developer.spotify.com/
7. Click "Log in" in the upper right corner and log in to your Spotify account
8. Click on your username in the same spot you clicked to log in and click "Dashboard"
9. Accept the Spotify Developer Terms of Service
10. Click Create App
11. Type whatever you would like in "App name" and "App description" (leave "Website" blank)
12. Type https://localhost:8080/callback into the "Redirect URI" field
13. Check the box next to "I understand and agree with Spotify's Developer Terms of Service and Design Guidelines" and click "Save"
14. Go back to the dashboard if not already there, click on the app you created, and click on "Settings" in the upper right area of the screen
15. Copy the Client ID and paste it into the single quote marks next to spotifyClientID in the config.py file you downloaded
16. Click view Client Secret and do the same as the last step but for the single quote marks next to spotifyClientSecret