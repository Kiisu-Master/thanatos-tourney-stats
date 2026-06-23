import requests as httpclient
import os
from dotenv import load_dotenv
import json as javason
import re, rich

load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
headers = {
    "Accept": "application/json",
    "Content-Type": "application/x-www-form-urlencoded"
}

class OsuApi:
    def get_token():
        token = OsuApi.TokenFile.read_token()
        if token == "":
            token_post_data = {
                "client_id": client_id,
                "client_secret": client_secret,
                "scope": "public",
                "grant_type": "client_credentials"
            }
            url="https://osu.ppy.sh/oauth/token"
            response = httpclient.post(url, headers=headers, data=token_post_data)
            response_dict = response.json() # json to pydict
            token = response_dict["access_token"]
            OsuApi.TokenFile.write_token(token)
        return token

    class TokenFile:
        def write_token(token, file="token.txt"):
            with open(file, "w", encoding="utf-8") as f:
                f.write(token)

        def read_token(file="token.txt"):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    token = f.read()
            except FileNotFoundError:
                return ""
            return token

class OsuMatches:
    @staticmethod
    def get_match_id(match_link="https://osu.ppy.sh/community/matches/121374117"):
        match_link = str(match_link)
        kaabu = re.fullmatch(r"(https://osu\.ppy\.sh/community/matches/)(\d+)", match_link)
        if kaabu:
            match_id = kaabu.group(2)
            return match_id
        elif re.fullmatch(r"\d+", match_link):
            return match_link
        else:
            print("Invalid osu! match url")

    @staticmethod
    def get_matches(match_link):
        match_id = OsuMatches.get_match_id(match_link)
        token = OsuApi.get_token()
        headersToken = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        url = f"https://osu.ppy.sh/api/v2/matches/{match_id}"
        response_dict = httpclient.get(url, headers=headersToken).json()

        json_file = "multi_" + str(match_id) + ".json"
        json_str = javason.dumps(response_dict, indent=4)
        with open(json_file, "w") as f:
            f.write(json_str)
        # print("json_str in OsuMatches: ", json_str) # temp
        return response_dict


class JsonMethods:
    def write_json(json_str, json_file="test.json"):
        with open(json_file, "w") as f:
            f.write(json_str)
    
    def read_json(json_file="test.json"):
        json_str = ""
        with open(json_file, "r") as f:
            for line in f:
                json_str = json_str + line
        
        return json_str



# test1 = OsuMatches.get_matches("https://osu.ppy.sh/community/matches/121376300")
test2 = JsonMethods.read_json("multi_121374117.json")
test2dict = javason.loads(test2)

# rich.print(test2dict)

# print(test2dict["events"][2]["game"]["scores"][0]["score"])

# for key, value in test2dict["events"].items():
#     # print(key, value)
#     if key == "detail":
#         print(value)

player_scores_dict = {}
print(player_scores_dict)
count = 0

for event in test2dict["events"]:
    for eventkey, eventvalue in event.items():
        if eventkey == "detail":
            if eventvalue["type"] == "other":
                count += 1

                beatmap_id = {"beatmap_id" : event["game"]["beatmap_id"]}
                if event["game"]["scores"] != []:
                    print(event["game"]["scores"][0]["score"])
                    score = {"score" : event["game"]["scores"][0]["score"]}
                    user_id = {"user_id" : event["game"]["scores"][0]["user_id"]}
                else:
                    score = {"score" : None}
                    user_id = {"user_id" : None}
                player_scores_dict[count] = [beatmap_id, score, user_id]

rich.print(player_scores_dict)

