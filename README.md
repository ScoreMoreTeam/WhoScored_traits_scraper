import soccerdata as sd
import pandas as pd 
ws = sd.WhoScored(leagues="ENG-Premier League", seasons=2021) #przykladowy sezon 
schedule = ws.read_schedule() #terminarz - stad bierzemy id meczy 
match_ids = schedule["game_id"].unique() #unikalne id meczy z terminarza 

results = [] #to jest tabela z unikalnymi id z sezonu

for game_id in match_ids:
    try:
        print(f"Pobieram dane dla meczu {game_id}...")
        data = sd.scrape_match_story(game_id)  #wywołujemy z soccerdata
        data["game_id"] = game_id
        results.append(data)
    except Exception as e:
        print(f"Błąd przy meczu {game_id}: {e}")
