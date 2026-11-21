import requests

api_key = "AC05E31A1272198CF4F8C8FD92220D91"
steam_id = "76561198963435803"

url = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/"
params = {
    "key": api_key,
    "steamid": steam_id,
    "include_appinfo": 1,
    "include_played_free_games": 1,
    "format": "json"
}

response = requests.get(url, params=params)
data = response.json()

if 'response' in data and 'games' in data['response']:
    user_games = data['response']['games']
    print(f"Найдено игр: {len(user_games)}")
    for game in user_games:
        print(f"ID: {game['appid']}, Название: {game['name']}, Часы: {game['playtime_forever']/60:.1f}")
else:
    print("Профиль закрыт или игр нет.")
    print("Ответ Steam:", data)
