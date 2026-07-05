import json
import os
import re
from dataclasses import dataclass
from typing import Any, override

import requests as httpclient
from dotenv import load_dotenv
from flask import Flask, make_response, redirect, render_template, request

load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

TEST_MATCHES = [
    "https://osu.ppy.sh/community/matches/121380887",
    "https://osu.ppy.sh/community/matches/121376300",
    "https://osu.ppy.sh/community/matches/121403400",
    "https://osu.ppy.sh/community/matches/121374117",
]

app = Flask(__name__)

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
        def write_token(token: str, file="token.txt"):
            with open(file, "w", encoding="utf-8") as f:
                f.write(token)

        @staticmethod
        def read_token(file="token.txt") -> str:
            with open(file, "r", encoding="utf-8") as f:
                return f.read()


@dataclass
class OsuPlayer:
    username: str
    user_id: int

    @override
    def __hash__(self):
        return self.user_id


@dataclass
class OsuScore:
    beatmap_id: int
    score: int
    user_id: int


class JsonMethods:
    @staticmethod
    def write_json(dict, json_file="test.json"):
        json_str = json.dumps(dict, indent=4)
        with open(json_file, "w") as f:
            f.write(json_str)

    @staticmethod
    def read_json(json_file="test.json") -> dict[Any, Any]:
        json_str = ""
        with open(json_file, "r") as f:
            for line in f:
                json_str = json_str + line
        data = json.loads(json_str)
        return data


class OsuMatch:
    data: dict[Any, Any]

    def __init__(self, match_link):
        match_id = OsuMatch.get_match_id(match_link)
        json_file = "multi_" + match_id + ".json"
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

        self.data = match_data

    @staticmethod
    def get_match_id(match_link: str) -> str:
        match_link = match_link.strip()
        result = re.fullmatch(
            r"(https://osu\.ppy\.sh/community/matches/)(\d+)", match_link
        )
        if result:
            match_id = result.group(2)
            return match_id
        elif re.fullmatch(r"\d+", match_link):
            return match_link
        else:
            raise

    def get_scores(self) -> list[OsuScore]:
        player_scores: list[OsuScore] = []
        for event in self.data["events"]:
            if "game" not in event:
                continue
            if event["game"]["scores"] == []:
                continue

            beatmap_id = event["game"]["beatmap_id"]
            for game_score in event["game"]["scores"]:
                score = game_score["score"]
                user_id = game_score["user_id"]
                player_scores.append(
                    OsuScore(
                        beatmap_id,
                        score,
                        user_id,
                    )
                )
        return player_scores

    def get_players(self) -> list[OsuPlayer]:
        players = []
        for player in self.data["users"]:
            players.append(OsuPlayer(player["username"], player["id"]))
        return players


ScoreData = dict[OsuPlayer, list[OsuScore | None]]


class OsuMatchSet:
    matches: list[OsuMatch]

    def __init__(self, matches: list[OsuMatch]):
        self.matches = matches

    def get_score_data(self, map_ids: list[int]) -> ScoreData:
        result: ScoreData = {}

        all_scores = self.get_scores()
        for player in self.get_players():
            result[player] = []
            player_scores: list[OsuScore] = list(
                filter(lambda score: score.user_id == player.user_id, all_scores)
            )
            if map_ids != []:
                for map_id in map_ids:
                    added = False
                    for score in player_scores:
                        if score.beatmap_id == map_id:
                            added = True
                            result[player].append(score)
                            break
                    if not added:
                        result[player].append(None)
            else:
                for score in player_scores:
                    result[player].append(score)
        return result

    def get_players(self) -> list[OsuPlayer]:
        all_players = []
        for match in self.matches:
            all_players.extend(match.get_players())
        return all_players

    def get_scores(self) -> list[OsuScore]:
        all_scores = []
        for match in self.matches:
            all_scores.extend(match.get_scores())
        return all_scores

    def get_csv(self, map_ids: list[int]) -> str:
        score_data = self.get_score_data(map_ids)
        ret = ",".join(FIELDS) + "\n"
        for player, scores in score_data.items():
            scores_str = ",".join(
                map(lambda s: str(s.score) if s is not None else "", scores)
            )
            ret += f'"{player.username}",{scores_str}\n'

        return ret


class Server:
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/scores")
    def scores():
        match_links = request.args.get("match_links")
        map_links = request.args.get("map_links")
        wants_csv = request.args.get("wants_csv")

        if match_links:
            match_links = match_links.strip().split("\n")
        else:
            return redirect("/")

        matches = list(map(OsuMatch, match_links))
        map_ids = []
        if map_links:
            map_ids = list(map(Server.get_map_id, map_links.strip().split("\n")))

        match_set = OsuMatchSet(matches)
        if wants_csv:
            resp = make_response(match_set.get_csv(map_ids))
            resp.content_type = "text/csv"
            return resp
        else:
            return render_template(
                "submit.html", scores=match_set.get_score_data(map_ids), fields=FIELDS
            )

    @staticmethod
    def get_map_id(map_link: str) -> int:
        map_link = map_link.strip()
        full_link = re.fullmatch(
            r"(https://osu\.ppy\.sh/beatmapsets/\d+#.+/)(\d+)", map_link
        )
        beatmap_link = re.fullmatch(r"(https://osu\.ppy\.sh/beatmaps/)(\d+)", map_link)
        if full_link:
            return int(full_link.group(2))
        elif beatmap_link:
            return int(beatmap_link.group(2))
        elif re.fullmatch(r"\d+", map_link):
            return int(map_link)
        else:
            raise
