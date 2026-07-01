import requests as httpclient
import os
from dotenv import load_dotenv
import json
import re

load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

TEST_MATCHES = [
    "https://osu.ppy.sh/community/matches/121380887",
    "https://osu.ppy.sh/community/matches/121376300",
    "https://osu.ppy.sh/community/matches/121403400",
    "https://osu.ppy.sh/community/matches/121374117",
]

FIELDS = [
    "player",
    "nm1",
    "nm2",
    "nm3",
    "nm4",
    "nm5",
    "hd1",
    "hd2",
    "hr1",
    "hr2",
    "dt1",
    "dt2",
    "dt3",
    "fm1",
    "fm2",
    "fm3",
]


class OsuAPIToken:
    @staticmethod
    def get_token() -> str:
        try:
            token = OsuAPIToken.TokenFile.read_token()
        except FileNotFoundError:
            print("Requesting new token")
            response = httpclient.post(
                url="https://osu.ppy.sh/oauth/token",
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
                json={
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                    "scope": "public",
                    "grant_type": "client_credentials",
                },
            ).json()
            token = response["access_token"]
            OsuAPIToken.TokenFile.write_token(token)
        return token

    class TokenFile:
        @staticmethod
        def write_token(token, file="token.txt"):
            with open(file, "w", encoding="utf-8") as f:
                f.write(token)

        @staticmethod
        def read_token(file="token.txt"):
            with open(file, "r", encoding="utf-8") as f:
                return f.read()


class OsuMatches:
    @staticmethod
    def get_match_id(match_link: str) -> str:
        match_link = match_link.strip()
        result = re.fullmatch(
            r"(https://osu\.ppy\.sh/community/matches/)(\d+)", match_link
        )
        if result:
            match_id = result.group(2)
            return match_id
        else:
            raise

    # @staticmethod
    # def get_match_ids(url_list: list[str]) -> list[str]:
    #     return list(map(OsuMatches.get_match_id, url_list))

    @staticmethod
    def get_match(match_link: str):
        match_id = OsuMatches.get_match_id(match_link)
        json_file = "multi_" + str(match_id) + ".json"
        try:
            match_data = JsonMethods.read_json(json_file)
        except FileNotFoundError:
            print("Downloading match ", match_id)
            token = OsuAPIToken.get_token()
            headersToken = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            }
            url = f"https://osu.ppy.sh/api/v2/matches/{match_id}"
            match_data = httpclient.get(url, headers=headersToken).json()
            JsonMethods.write_json(match_data, json_file)

        return match_data


class JsonMethods:
    @staticmethod
    def write_json(dict, json_file="test.json"):
        json_str = json.dumps(dict, indent=4)
        with open(json_file, "w") as f:
            f.write(json_str)

    @staticmethod
    def read_json(json_file="test.json"):
        json_str = ""
        with open(json_file, "r") as f:
            for line in f:
                json_str = json_str + line
        data = json.loads(json_str)
        return data


def filter_match_for_scores(match_dict):
    data = match_dict

    count = 0
    player_scores_dict = {}
    for event in data["events"]:
        for eventkey, eventvalue in event.items():
            if eventkey == "detail":
                if eventvalue["type"] == "other":
                    count += 1
                    beatmap_id = event["game"]["beatmap_id"]
                    if event["game"]["scores"] != []:
                        for i in range(0, len(event["game"]["scores"])):
                            score = event["game"]["scores"][i]["score"]
                            user_id = event["game"]["scores"][i]["user_id"]
                            player_scores_dict[str(count) + "_" + str(user_id)] = {
                                "beatmap_id": beatmap_id,
                                "score": score,
                                "user_id": user_id,
                            }
                    else:
                        count -= 1
    return player_scores_dict

matches = list(map(OsuMatches.get_match, TEST_MATCHES))

usernames = {}
for match in matches:
    for user in match["users"]:
        usernames[user["id"]] = user["username"]

all_scores = []
for match in matches:
    all_scores.append(filter_match_for_scores(match))

csv_dict = {}

for uid, u in usernames.items():
    csv_dict[uid] = []
for match in all_scores:
    for user_score in match:
        csv_dict[match[user_score]["user_id"]].append(match[user_score]["score"])

csv_username_dict = {}
for user_id in csv_dict:
    username = usernames[user_id]
    csv_username_dict[username] = csv_dict[user_id]

for user, scores in csv_username_dict.items():
    print(f'"{user}",' + ",".join(map(str, scores)))
