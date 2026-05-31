#!/usr/bin/env python3
"""
Puzzle Arcade - A puzzle system for the crew
Built by Jax on Day 2

Commands:
  python arcade.py riddle              - Get a random riddle
  python arcade.py riddle easy|medium|hard  - Get riddle by difficulty
  python arcade.py logic               - Get a logic puzzle
  python arcade.py sequence            - Get a number sequence
  python arcade.py word                - Get a word puzzle
  python arcade.py answer <id>         - Get the answer for a puzzle
  python arcade.py stats               - Show crew scores
  python arcade.py solve <id> <player> - Record that someone solved a puzzle
  python arcade.py daily               - Get today's daily challenge
"""

import json
import random
import os
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PUZZLES_FILE = SCRIPT_DIR / "puzzles.json"
SCORES_FILE = SCRIPT_DIR / "scores.json"
DAILY_FILE = SCRIPT_DIR / "daily.json"

def load_puzzles():
    with open(PUZZLES_FILE) as f:
        return json.load(f)

def load_scores():
    if SCORES_FILE.exists():
        with open(SCORES_FILE) as f:
            return json.load(f)
    return {"players": {}, "solved": {}}

def save_scores(scores):
    with open(SCORES_FILE, "w") as f:
        json.dump(scores, f, indent=2)

def load_daily():
    if DAILY_FILE.exists():
        with open(DAILY_FILE) as f:
            return json.load(f)
    return {}

def save_daily(daily):
    with open(DAILY_FILE, "w") as f:
        json.dump(daily, f, indent=2)

def get_points(difficulty):
    return {"easy": 1, "medium": 2, "hard": 3}.get(difficulty, 1)

def get_random_riddle(difficulty=None):
    puzzles = load_puzzles()
    riddles = puzzles["riddles"]
    if difficulty:
        riddles = [r for r in riddles if r["difficulty"] == difficulty]
    if not riddles:
        return "No riddles found for that difficulty."

    riddle = random.choice(riddles)
    return f"""🎭 **RIDDLE** [{riddle['difficulty'].upper()}] (ID: {riddle['id']})

{riddle['question']}

Points: {get_points(riddle['difficulty'])} | Use `arcade.py answer {riddle['id']}` to reveal"""

def get_logic_puzzle():
    puzzles = load_puzzles()
    puzzle = random.choice(puzzles["logic_puzzles"])
    return f"""🧠 **LOGIC PUZZLE** [{puzzle['difficulty'].upper()}] (ID: {puzzle['id']})

{puzzle['question']}

Points: {get_points(puzzle['difficulty'])} | Use `arcade.py answer {puzzle['id']}` to reveal"""

def get_sequence():
    puzzles = load_puzzles()
    seq = random.choice(puzzles["number_sequences"])
    sequence_str = ", ".join(str(x) for x in seq["sequence"])
    return f"""🔢 **NUMBER SEQUENCE** [{seq['difficulty'].upper()}] (ID: {seq['id']})

What comes next?
{sequence_str}

Points: {get_points(seq['difficulty'])} | Use `arcade.py answer {seq['id']}` to reveal"""

def get_word_puzzle():
    puzzles = load_puzzles()
    puzzle = random.choice(puzzles["word_puzzles"])
    return f"""📝 **WORD PUZZLE** [{puzzle['difficulty'].upper()}] (ID: {puzzle['id']})

{puzzle['question']}

Points: {get_points(puzzle['difficulty'])} | Use `arcade.py answer {puzzle['id']}` to reveal"""

def get_answer(puzzle_id):
    puzzles = load_puzzles()

    for category in ["riddles", "logic_puzzles", "number_sequences", "word_puzzles"]:
        for p in puzzles.get(category, []):
            if p["id"] == puzzle_id:
                result = f"**Answer for {puzzle_id}:** {p['answer']}"
                if "explanation" in p:
                    result += f"\n\n*{p['explanation']}*"
                return result

    return f"Puzzle {puzzle_id} not found."

def record_solve(puzzle_id, player):
    scores = load_scores()
    puzzles = load_puzzles()

    puzzle = None
    for category in ["riddles", "logic_puzzles", "number_sequences", "word_puzzles"]:
        for p in puzzles.get(category, []):
            if p["id"] == puzzle_id:
                puzzle = p
                break
        if puzzle:
            break

    if not puzzle:
        return f"Puzzle {puzzle_id} not found."

    solve_key = f"{player}:{puzzle_id}"
    if solve_key in scores["solved"]:
        return f"{player} already solved {puzzle_id}!"

    points = get_points(puzzle["difficulty"])
    if player not in scores["players"]:
        scores["players"][player] = {"points": 0, "solved": 0}

    scores["players"][player]["points"] += points
    scores["players"][player]["solved"] += 1
    scores["solved"][solve_key] = datetime.now().isoformat()

    save_scores(scores)
    return f"✅ {player} solved {puzzle_id}! +{points} points (Total: {scores['players'][player]['points']})"

def show_stats():
    scores = load_scores()
    if not scores["players"]:
        return "No scores yet! Start solving puzzles."

    sorted_players = sorted(
        scores["players"].items(),
        key=lambda x: x[1]["points"],
        reverse=True
    )

    result = "🏆 **PUZZLE ARCADE LEADERBOARD**\n\n"
    for i, (player, data) in enumerate(sorted_players, 1):
        emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
        result += f"{emoji} **{player}**: {data['points']} points ({data['solved']} solved)\n"

    return result

def get_daily_challenge():
    today = datetime.now().strftime("%Y-%m-%d")
    daily = load_daily()

    if daily.get("date") == today:
        puzzle_id = daily["puzzle_id"]
        puzzles = load_puzzles()
        for category in ["riddles", "logic_puzzles", "number_sequences", "word_puzzles"]:
            for p in puzzles.get(category, []):
                if p["id"] == puzzle_id:
                    emoji = {"riddles": "🎭", "logic_puzzles": "🧠", "number_sequences": "🔢", "word_puzzles": "📝"}[category]
                    return f"📅 **DAILY CHALLENGE** ({today})\n\n{emoji} {p['question']}\n\nID: {p['id']} | Points: {get_points(p['difficulty']) * 2} (2x for daily!)"

    puzzles = load_puzzles()
    all_puzzles = []
    for category in ["riddles", "logic_puzzles"]:
        for p in puzzles.get(category, []):
            all_puzzles.append((category, p))

    category, puzzle = random.choice(all_puzzles)
    daily = {"date": today, "puzzle_id": puzzle["id"], "category": category}
    save_daily(daily)

    points = get_points(puzzle["difficulty"]) * 2

    if category == "riddles":
        return f"""📅 **DAILY CHALLENGE** ({today})

🎭 {puzzle['question']}

ID: {puzzle['id']} | Points: {points} (2x for daily!) | Difficulty: {puzzle['difficulty'].upper()}"""
    else:
        return f"""📅 **DAILY CHALLENGE** ({today})

🧠 {puzzle['question']}

ID: {puzzle['id']} | Points: {points} (2x for daily!) | Difficulty: {puzzle['difficulty'].upper()}"""

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1].lower()

    if cmd == "riddle":
        difficulty = sys.argv[2].lower() if len(sys.argv) > 2 else None
        print(get_random_riddle(difficulty))
    elif cmd == "logic":
        print(get_logic_puzzle())
    elif cmd == "sequence":
        print(get_sequence())
    elif cmd == "word":
        print(get_word_puzzle())
    elif cmd == "answer":
        if len(sys.argv) < 3:
            print("Usage: arcade.py answer <puzzle_id>")
            return
        print(get_answer(sys.argv[2]))
    elif cmd == "solve":
        if len(sys.argv) < 4:
            print("Usage: arcade.py solve <puzzle_id> <player>")
            return
        print(record_solve(sys.argv[2], sys.argv[3]))
    elif cmd == "stats":
        print(show_stats())
    elif cmd == "daily":
        print(get_daily_challenge())
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)

if __name__ == "__main__":
    main()
