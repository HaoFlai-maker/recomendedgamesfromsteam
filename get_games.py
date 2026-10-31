import csv

games_data = [
    {"id": 1, "name": "Stardew Valley", "genres": "Simulation, RPG", "playtime_hours": 50, "has_coop": True,
     "rating": 4.8},
    {"id": 2, "name": "Portal 2", "genres": "Puzzle, Platformer", "playtime_hours": 12, "has_coop": True,
     "rating": 4.9},
    {"id": 3, "name": "Cyberpunk 2077", "genres": "RPG, Action", "playtime_hours": 60, "has_coop": False,
     "rating": 4.2},
    {"id": 4, "name": "It Takes Two", "genres": "Adventure, Platformer", "playtime_hours": 14, "has_coop": True,
     "rating": 4.7},
    {"id": 5, "name": "The Witcher 3", "genres": "RPG, Adventure", "playtime_hours": 100, "has_coop": False,
     "rating": 4.9},
    {"id": 6, "name": "Among Us", "genres": "Party, Casual", "playtime_hours": 10, "has_coop": True, "rating": 4.0},
    {"id": 7, "name": "Hades", "genres": "Roguelike, Action", "playtime_hours": 25, "has_coop": False, "rating": 4.7},
    {"id": 8, "name": "Don't Starve Together", "genres": "Survival, Adventure", "playtime_hours": 40, "has_coop": True,
     "rating": 4.4},
    {"id": 9, "name": "Hollow Knight", "genres": "Metroidvania, Action", "playtime_hours": 30, "has_coop": False,
     "rating": 4.8},
    {"id": 10, "name": "Terraria", "genres": "Sandbox, Adventure", "playtime_hours": 80, "has_coop": True,
     "rating": 4.6}
]

filename = "games_data.csv"

fieldnames = ["id", "name", "genres", "playtime_hours", "has_coop", "rating"]

with open(filename, mode='w', newline='', encoding='utf-8-sig') as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)

    writer.writeheader()

    for game in games_data:
        writer.writerow(game)

print(f"Готово! Файл создан.")