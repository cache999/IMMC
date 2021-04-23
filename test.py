import json

# script to calculate winners
with open("tennis.json", "r") as f:
    data = json.load(f)

for game in data["games"]:
    tally = 0 #pos: p1, neg: p2
    for round in game['score']:
        assert round[1] != round[0]
        if round[0] > round[1]:
            tally += 1
        else:
            tally -= 1
    print(tally)
    assert tally != 0
    if tally > 0:
        game['winner'] = "player1"
        game['loser'] = "player2"
    else:
        game['winner'] = "player2"
        game['loser'] = "player1"
    print(game)

with open("tennis.json", "w") as f:
    f.write(json.dumps(data))