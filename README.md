## Thanatos tourney stats for osu!
Tool to create a CSV table of player scores from matches

### Setup
You need to have a working osu oauth application (you can create one (here)[https://osu.ppy.sh/home/account/edit#new-oauth-application])
Set up the credentials `.env` file as
```
CLIENT_ID=xxxx
CLIENT_SECRET=xxxx
```

Using the uv python package manger and a bash shell (venv activation depends on shell),
you can start the application with these commands:
```sh
uv sync
source .venv/bin/activate
flask run
```
Then open the [site](http://127.0.0.1:5000) in your browser.
Add links to the multiplayer matches.
Submit without "download CSV file" enabled to see a preview of the table in your browser.
