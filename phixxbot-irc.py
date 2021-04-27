import requests
import miniirc
import time
import sys
from datetime import datetime

# Constants
CLIENT_SECRET = ""
CLIENT_ID = ""
TWITCH_API_URL = "https://api.twitch.tv/helix/streams"
TWITCH_TOKEN_API = "https://id.twitch.tv/oauth2/token"
CHANNELS = {"djphixx" : False,
            "drsldr"  : False}

def main():
    token = authenticate()
    if(token == ""):
        print("Could not authenticate to Twitch. Exiting.")
        quit()

    headers = {"Client-Id": CLIENT_ID, "Authorization": "Bearer " + token}
    # Set up IRC connection
    irc = miniirc.IRC('irc.dtek.se', 6697, 'PhixxBot', ['#dtek'], verify_ssl=False)
    irc.send('PRIVMSG', '#dtek', "I'm alive!")

    while(True):
        try:
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
                    CHANNELS[channel] = False

                # Twitch error
                elif(not response.ok):
                    print("Twitch error:", response.text)

                # None of the selected channels are live
                else:
                    print("Channel twitch.tv/" + channel + " is not live. *cricket noise*")
            time.sleep(45)
        except KeyboardInterrupt:
            print("Keyboard interrupt detected. Exiting.")
            irc.send('PRIVMSG', '#dtek', "Bye bye!")
            quit()

def authenticate():
    parameters={ "client_id" : CLIENT_ID, "client_secret":  CLIENT_SECRET, "grant_type": "client_credentials" }
    try:
        response = requests.request("POST", TWITCH_TOKEN_API, params=parameters)
    except Exception as e:
                print(e)
                return ""
    if(response.status_code == 200):
        json = response.json()
        return json["access_token"]
    else:
        print("Error during authentication:", response.status_code, response.reason)
        return ""

if(__name__ == "__main__"):
    main()
