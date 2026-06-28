import requests as httpclient
import os
from dotenv import load_dotenv
import json as javason
import re
import rich
import csv
from time import sleep

load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
headers = {
    "Accept": "application/json",
    "Content-Type": "application/x-www-form-urlencoded",
}


class OsuApi:  # everything is used here
    @staticmethod
    def get_token():
        token = OsuApi.TokenFile.read_token()
        if token == "":
            token_post_data = {
                "client_id": client_id,
                "client_secret": client_secret,
                "scope": "public",
                "grant_type": "client_credentials",
            }
            url = "https://osu.ppy.sh/oauth/token"
            response = httpclient.post(url, headers=headers, data=token_post_data)
            response_dict = response.json()  # json to pydict
            token = response_dict["access_token"]
            OsuApi.TokenFile.write_token(token)
        return token

    class TokenFile:
        @staticmethod
        def write_token(token, file="token.txt"):
            with open(file, "w", encoding="utf-8") as f:
                f.write(token)

        @staticmethod
        def read_token(file="token.txt"):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    token = f.read()
            except FileNotFoundError:
                return ""
            return token


class OsuMatches:  # everything is used here
    @staticmethod
    def get_match_id(match_link="https://osu.ppy.sh/community/matches/121374117"):
        match_link = str(match_link)
        kaabu = re.fullmatch(
            r"(https://osu\.ppy\.sh/community/matches/)(\d+)", match_link
        )
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
            "Authorization": f"Bearer {token}",
        }
        url = f"https://osu.ppy.sh/api/v2/matches/{match_id}"
        response_dict = httpclient.get(url, headers=headersToken).json()

        json_file = "multi_" + str(match_id) + ".json"
        json_str = javason.dumps(response_dict, indent=4)
        with open(json_file, "w") as f:
            f.write(json_str)
        return response_dict

    @staticmethod
    def make_matchsids_list(file="multimatches.txt"):
        mutli_ids = []
        with open(file, "r") as f:
            for line in f:
                line = line.strip()
                mutli_ids.append(OsuMatches.get_match_id(line))
        return mutli_ids


class OsuUsers:  # basically useless class
    @staticmethod
    def get_ids_from_my_dict(my_dict):  # vihkan seda
        user_id = my_dict[1]["user_id"]
        user_ids = []
        for line in my_dict:
            if user_id not in user_ids:
                user_ids.append(user_id)
        return user_ids

    @staticmethod
    def get_users(user_ids):  # töötab, aga pole mõtet kasutada
        token = OsuApi.get_token()
        url = "https://osu.ppy.sh/api/v2/users"
        params = {"ids[]": user_ids}
        headersToken = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        response_dict = httpclient.get(url, headers=headersToken, params=params).json()

        json_file = "Users_" + str(user_ids) + ".json"
        json_str = javason.dumps(response_dict, indent=4)
        with open(json_file, "w") as f:
            f.write(json_str)
        return response_dict

    # def make_users_dict():


class JsonMethods:
    @staticmethod
    def write_json(json_str, json_file="test.json"):  # not used, it's aura farming
        with open(json_file, "w") as f:
            f.write(json_str)

    @staticmethod
    def read_json(json_file="test.json"):  # useful
        json_str = ""
        with open(json_file, "r") as f:
            for line in f:
                json_str = json_str + line

        return json_str


# OsuApi.get_token()
# OsuMatches.get_matches("https://osu.ppy.sh/community/matches/121380887")

# test1 = OsuMatches.get_matches("https://osu.ppy.sh/community/matches/121376300")

# csv_file = "tabel.csv"
# with open(csv_file, "w") as new_file:
#     filednames = ["player","nm1","nm2","nm3","nm4","nm5","hd1","hd2","hr1","hr2","dt1","dt2","dt3","fm1","fm2","fm3"]

#     csv_writer = csv.DictWriter(new_file, filednames=filednames)
#     csv_writer.writeheader()

#     for line in


class DictonaryMaker:
    @staticmethod
    def make_scores_dict(json_file="multi_121380887.json"):  # Legacy code kappa
        test2 = JsonMethods.read_json(json_file)
        test2dict = javason.loads(test2)

        # rich.print(test2dict)

        player_scores_dict = {}
        # print(player_scores_dict)
        count = 0

        for event in test2dict["events"]:
            for eventkey, eventvalue in event.items():
                if eventkey == "detail":
                    if eventvalue["type"] == "other":
                        count += 1

                        beatmap_id = event["game"]["beatmap_id"]
                        if event["game"]["scores"] != []:
                            score = event["game"]["scores"][0]["score"]
                            user_id = event["game"]["scores"][0]["user_id"]
                        else:
                            score = None
                            user_id = None
                        player_scores_dict[count] = {
                            "beatmap_id": beatmap_id,
                            "score": score,
                            "user_id": user_id,
                        }

        return player_scores_dict

    @staticmethod
    def make_user_id_dict(json_file="multi_121403400.json"):  # doesn't work as intended
        java_str = JsonMethods.read_json(json_file)
        java_dump = javason.loads(java_str)

        for user in java_dump["users"]:
            for eventkey, eventvalue in user.items():
                if eventkey == "id":
                    print(user["username"])
        return

    @staticmethod
    # better verison of make_scores_dict()
    def make_scores_dict_better(json_file="multi_121403400.json"):
        java_str = JsonMethods.read_json(json_file)
        java_dump = javason.loads(java_str)

        count = 0
        player_scores_dict = {}
        for event in java_dump["events"]:
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

    @staticmethod
    def make_user_ids_dict(json_file="Users_[12401523, 14061950].json"):  # not useful
        users_dict = JsonMethods.read_json(json_file)
        users_dict = javason.loads(users_dict)
        # rich.print(Users_dict)
        users_ids_dict = {}
        for line in users_dict["users"]:
            userid = line["id"]
            username = line["userkey"]
            users_ids_dict[userid] = username

        return users_ids_dict


matchs_ids = OsuMatches.make_matchsids_list()
usernames = {}
for match_id in matchs_ids:
    match_id = match_id
    json_file = f"multi_{match_id}.json"
    java_str = JsonMethods.read_json(json_file)
    java_dump = javason.loads(java_str)

    for user in java_dump["users"]:
        usernames[user["id"]] = user["username"]

all_matches = []
for match_id in matchs_ids:
    all_matches.append(
        DictonaryMaker.make_scores_dict_better("multi_" + str(match_id) + ".json")
    )
# rich.print(Scores)

csv_style_dict = {}


# for match in Scores:
#     listike = []
#     for count in match:
#         listike.append(match[count]["score"])
#         user_id = match[count]["user_id"]
#         username = Usernames[user_id]
#     csv_style_dict[username] = listike
# rich.print(csv_style_dict)

csv_dict = {}

for uid, u in usernames.items():
    csv_dict[uid] = []
for match in all_matches:
    for user_score in match:
        csv_dict[match[user_score]["user_id"]].append(match[user_score]["score"])

csv_username_dict = {}
for user_id in csv_dict:
    username = usernames[user_id]
    csv_username_dict[username] = csv_dict[user_id]

# rich.print(csv_username_dict)


for user, scores in csv_username_dict.items():
    print(f'"{user}",' + ",".join(map(str, scores)))
