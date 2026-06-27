# My classes
## OsuApi
```OsuApi.get_token()``` <br />
This will make get token request. <br />
You need to define client_id and client_secret.
### OsuApi.TokenFile
```OsuApi.TokenFile.write_token(token)``` <br />
This will write token to ```token.txt```.  <br />
```OsuApi.TokenFile.read_token()``` <br />
This will read the token.

## OsuMatches
```OsuMatches.get_match_id()```  
It will return match id. (For example: ```1234567```)  
```OsuMatches.get_matches()```  
This will make get matches request.
You will need unexperied token.
It also writes local json file.

## OsuUsers
```OsuUsers.get_ids_from_MyDict()```  
Returns user_ids in a list. It looks them from your dictonary.
```OsuUsers.get_users()```  
This will make get users request.
You will need unexperied token.
It also writes local json file.

## JsonMethods
```JsonMethods.write_json(json_str, json_file)```  
Gotta use `json_str = javason.dumps(dictonary, indent=4)`
```JsonMethods.read_json(json_file)```  
Returns `json_str`  
You have to use `x = javason.loads(json_str)` to get dictonary.

## DictonaryMaker
```DictonaryMaker.Make_scoresDict()```  
Returns player_scores_dict.
```DictonaryMaker.Make_UserIdsDict()```  
Returns Users_Ids_dict.
