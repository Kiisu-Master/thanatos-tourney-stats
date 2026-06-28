# Here is stuff I have learned from this project:

POST - Upload data
GET - Download data 
DELETE - it exists (idk what it does yet)

You can host local server with this terminal command:
```python3 -m http.server -b 127.0.0.1 4000```

# Regex
```
r"(https://osu\.ppy\.sh/community/matches/)(\d+)"
# This is python spefic regex.
```
()() - those things create groups in regex.
Groups start with 1 and move up.

Useful link: https://regex101.com/. Pick "Flavor: Python."

# To do:
```def get_matches(match_link):```
- Make it check if x.json already exists and if does return that, else just return the request.

Rn it can only make requests and save jsons, which is kinda meh.
- Fix documentation lowkey.

# Dictonaries
```print(test2dict["events"][2]["game"]["scores"][0]["score"])```

[events][which event (ordered)][game][scores][first thingy][score has your score lol]




# Credits
[Kiisu_master](https://github.com/Kiisu-Master) helped me to figure out how to do requests and helped to write some of the logic at end.

