import requests
import miniirc
import time

# Constants
CLIENT_ID = ""
OAUTH2_TOKEN = ""
TWITCH_API_URL = "https://api.twitch.tv/helix/streams"
CHANNELS = {"djphixx" : False,
            "drsldr"  : False}

# Set up IRC connection and API request
irc = miniirc.IRC('irc.dtek.se', 6697, 'PhixxBot', ['#dtek'], verify_ssl=False)
headers = {"Client-Id": CLIENT_ID, "Authorization": "Bearer " + OAUTH2_TOKEN}

while(True):
    for channel in CHANNELS:
        parameters = {"user_login": channel}
        try:
            response = requests.request("GET", TWITCH_API_URL, params=parameters, headers=headers)
            print("Twitch repsonse:", response.status_code)
            responseJson = response.json()
        except Exception as e:
            print(e)
            time.sleep(60)
            continue

        # Channel has gone live
        if(response.ok and (len(responseJson["data"]) > 0) and not CHANNELS[channel]):
            CHANNELS[channel] = True
            print("Channel twitch.tv/" + channel + " is live with " + responseJson["data"][0]["game_name"] + "!")
            irc.send('PRIVMSG', '#dtek', "Channel twitch.tv/" + channel + " is live with " + responseJson["data"][0]["game_name"] + "!")

        # Channel was live and gone offline
        elif(response.ok and CHANNELS[channel] and len(responseJson["data"]) == 0):
            print("Channel twitch.tv/" + channel + " has gone offline. See you next time!")
            #irc.send('PRIVMSG', '#dtek', "Channel twitch.tv/" + channel + " has gone offline. See you next time!")
            CHANNELS[channel] = False

        # Twitch error
        elif(not response.ok):
            print("Twitch error:", response.text)

        # None of the selected channels are live
        else:
            print("Channel twitch.tv/" + channel + " is not live. *cricket noise*")
    time.sleep(45)