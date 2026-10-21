from ursina import *
import random
import json
import os

# =====================================================
# TROPHY TACTICS - TIC TAC TOE ARENA
# =====================================================

app = Ursina()
window.title = "Trophy Tactics: Tic-Tac-Toe Arena"
window.borderless = False
window.fullscreen = False
window.exit_button.visible = False
window.fps_counter.enabled = True
window.color = color.rgb(0, 0, 0)

SAVE_FILE = "trophy_tactics_save.json"

DEFAULT = {
    "trophies": 0,
    "coins": 0,
    "wins": 0,
    "losses": 0,
    "draws": 0,
    "xp": 0,
    "training": 0,
    "unlocked": 1,
    "streak": 0,
    "best_streak": 0
}

try:
    with open(SAVE_FILE, "r") as f:
        data = DEFAULT.copy()
        data.update(json.load(f))
except:
    data = DEFAULT.copy()

bots = [
    ("ROOKIE BOT", 5, 12, "Random moves"),
    ("SCOUT BOT", 8, 18, "Tries to win"),
    ("TACTICIAN", 12, 25, "Wins and blocks"),
    ("GRANDMASTER", 18, 35, "Unbeatable"),
    ("CHAMPION", 28, 50, "Unbeatable"),
    ("LEGEND", 45, 75, "Unbeatable")
]

bot_colors = [
    color.azure,
    color.lime,
    color.gold,
    color.orange,
    color.magenta,
    color.rgb(0, 0, 0)
]

board = [""] * 9
buttons = []
ui_items = []
world_items = []

screen = "lobby"
bot_number = 1
busy = False
finished = False
status_label = None


# =====================================================
# SAVE SYSTEM
# =====================================================

def save_game():
    try:
        with open(SAVE_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print("Could not save progress:", e)


def level():
    return 1 + data["xp"] // 100


def clear_ui():
    global ui_items

    for item in ui_items[:]:
        if item:
            destroy(item)

    ui_items.clear()


def clear_world():
    global world_items

    for item in world_items[:]:
        if item:
            destroy(item)

    world_items.clear()


def add_ui(item):
    ui_items.append(item)
    return item


def label(text, x=0, y=0, scale=1, tint=color.blue):
    return add_ui(Text(
        text=text,
        x=x,
        y=y,
        scale=scale,
        color=tint,
        origin=(0, 0)
    ))


def button(text, x, y, action, tint=color.rgb(0, 0, 0),
           size=(0.3, 0.07), text_size=0.9):

    b = Button(
        text=text,
        x=x,
        y=y,
        scale=size,
        color=tint,
        highlight_color=color.azure,
        pressed_color=color.rgb(0, 0, 0),
        on_click=action
    )

    b.text_entity.scale = text_size
    add_ui(b)
    return b


def stats_text():
    return (
        f"Trophies: {data['trophies']}    "
        f"Coins: {data['coins']}    "
        f"Level: {level()}"
    )


# =====================================================
# 3D ARENA
# =====================================================

def make_arena():
    clear_world()

    camera.position = (0, 8, -15)
    camera.rotation = (23, 0, 0)
    camera.fov = 75

    floor = Entity(
        model="plane",
        scale=40,
        texture="white_cube",
        texture_scale=(20, 20),
        color=color.rgb(0, 0, 0),
        collider="box"
    )
    world_items.append(floor)

    platform = Entity(
        model="cube",
        position=(0, 0.05, 0),
        scale=(13, 0.3, 12),
        color=color.rgb(13, 44, 1)
    )
    world_items.append(platform)

    for x in (-6, 6):
        for z in (-5, 5):
            pillar = Entity(
                model="cube",
                position=(x, 1.5, z),
                scale=(0.5, 3, 0.5),
                color=color.azure
            )
            world_items.append(pillar)

    trophy = Entity(
        model="sphere",
        position=(-4, 1.4, 0),
        scale=(0.8, 0.9, 0.6),
        color=color.gold
    )
    world_items.append(trophy)

    training = Entity(
        model="cube",
        position=(4, 0.8, 0),
        scale=(1.8, 1.4, 1.8),
        color=color.rgb(13, 44, 1)
    )
    world_items.append(training)


# =====================================================
# LOBBY
# =====================================================

def lobby():
    global screen

    screen = "lobby"
    clear_ui()
    make_arena()

    label("TROPHY TACTICS", y=0.38, scale=2.3, tint=color.azure)
    label("TIC-TAC-TOE ARENA", y=0.30, scale=1.1)
    label(stats_text(), y=0.23, scale=0.9, tint=color.gold)

    label(
        f"Wins: {data['wins']}    "
        f"Losses: {data['losses']}    "
        f"Training: {data['training']}",
        y=0.18, scale=0.75
    )

    button(
        "BATTLE BOTS",
        -0.23, 0.07,
        bot_select,
        color.rgb(13, 44,1),
        size=(0.32, 0.08),
        text_size=1.05
    )

    button(
        "TRAIN",
        0.23, 0.07,
        training_room,
        color.rgb(13, 44, 1),
        size=(0.24, 0.08),
        text_size=1.05
    )

    button(
        "TROPHY ROOM",
        -0.23, -0.045,
        trophy_room,
        color.rgb(13, 44, 1)
    )

    button(
        "HOW TO PLAY",
        0.23, -0.045,
        help_screen,
        color.rgb(13, 44, 1)
    )

    label(
        "Defeat stronger bots to earn bigger rewards!",
        y=-0.19, scale=0.8
    )

    label(
        "Your progress saves automatically.",
        y=-0.24, scale=0.65,
        tint=color.rgb(160, 180, 205)
    )


# =====================================================
# BOT SELECT
# =====================================================

def bot_select():
    global screen

    screen = "select"
    clear_ui()

    label("CHOOSE YOUR OPPONENT", y=0.40, scale=1.6,
          tint=color.azure)
    label(stats_text(), y=0.33, scale=0.8, tint=color.gold)

    for i, bot in enumerate(bots):
        row = i // 3
        col = i % 3

        x = -0.48 + col * 0.48
        y = 0.17 - row * 0.22

        name, trophies, coins, difficulty = bot
        unlocked = i + 1 <= data["unlocked"]

        if unlocked:
            text = (
                f"{name}\n"
                f"{difficulty}\n"
                f"+{trophies} trophies\n"
                f"+{coins} coins"
            )

            button(
                text, x, y,
                lambda n=i + 1: start_match(n),
                bot_colors[i],
                size=(0.43, 0.17),
                text_size=0.65
            )
        else:
            button(
                f"LOCKED BOT {i+1}\n"
                f"Defeat Bot {i}\n"
                f"Earn more trophies",
                x, y,
                lambda: None,
                color.rgb(13, 44, 1),
                size=(0.43, 0.17),
                text_size=0.65
            )

    button("BACK", 0, -0.34, lobby,
           color.rgb(13,44, 1))


# =====================================================
# TRAINING SYSTEM
# =====================================================

def training_room():
    global screen

    screen = "training"
    clear_ui()

    cost = 20 + data["training"] * 15

    label("TRAINING GROUNDS", y=0.38, scale=1.8,
          tint=color.lime)

    label(f"Coins: {data['coins']}", y=0.25, scale=1.1,
          tint=color.gold)

    label(f"Training rank: {data['training']}", y=0.17,
          scale=1.0)

    label(f"Next upgrade costs {cost} coins", y=0.09,
          scale=0.9)

    label(
        f"Coin reward bonus: {data['training'] * 10}%",
        y=0.02, scale=0.9, tint=color.lime
    )

    button(
        "TRAIN NOW",
        0, -0.10,
        lambda: train(cost),
        color.rgb(13, 44, 1),
        size=(0.30, 0.08)
    )

    button("BACK", 0, -0.25, lobby,
           color.rgb(75, 85, 110))


def train(cost):
    if data["coins"] < cost:
        clear_ui()
        label("NOT ENOUGH COINS", y=0.12,
              scale=1.5, tint=color.red)
        label(f"You need {cost} coins.", y=0.02)
        button("BACK", 0, -0.12, training_room)
        return

    data["coins"] -= cost
    data["training"] += 1
    data["xp"] += 15

    save_game()
    training_room()


# =====================================================
# TIC-TAC-TOE LOGIC
# =====================================================

WIN_LINES = [
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6)
]


def has_won(cells, mark):
    return any(
        all(cells[i] == mark for i in line)
        for line in WIN_LINES
    )


def moves(cells):
    return [i for i in range(9) if cells[i] == ""]


def minimax(cells, ai_turn, depth=0):
    if has_won(cells, "O"):
        return 10 - depth

    if has_won(cells, "X"):
        return depth - 10

    available = moves(cells)

    if not available:
        return 0

    if ai_turn:
        best = -100

        for m in available:
            cells[m] = "O"
            score = minimax(cells, False, depth + 1)
            cells[m] = ""
            best = max(best, score)

        return best

    best = 100

    for m in available:
        cells[m] = "X"
        score = minimax(cells, True, depth + 1)
        cells[m] = ""
        best = min(best, score)

    return best


def ai_move():
    available = moves(board)

    if not available:
        return None

    # Bot 1: random moves
    if bot_number == 1:
        return random.choice(available)

    # Bot 2: prioritizes its own winning moves
    if bot_number == 2:
        for m in available:
            board[m] = "O"
            win = has_won(board, "O")
            board[m] = ""

            if win:
                return m

        return random.choice(available)

    # Bot 3: wins, blocks, then takes strategic positions
    if bot_number == 3:
        for mark in ("O", "X"):
            for m in available:
                board[m] = mark
                win = has_won(board, mark)
                board[m] = ""

                if win:
                    return m

        for m in (4, 0, 2, 6, 8, 1, 3, 5, 7):
            if m in available:
                return m

    # Bots 4-6 use perfect-play minimax
    best_score = -100
    best_moves = []

    for m in available:
        board[m] = "O"
        score = minimax(board, False)
        board[m] = ""

        if score > best_score:
            best_score = score
            best_moves = [m]
        elif score == best_score:
            best_moves.append(m)

    return random.choice(best_moves)


# =====================================================
# MATCH SCREEN
# =====================================================

def start_match(number):
    global screen, bot_number, board, buttons
    global busy, finished

    screen = "match"
    bot_number = number
    board = [""] * 9
    buttons = []
    busy = False
    finished = False

    clear_ui()
    make_arena()

    camera.position = (0, 10, -15)
    camera.rotation = (32, 0, 0)

    label(
        f"BATTLE: {bots[number-1][0]}",
        y=0.43, scale=1.3,
        tint=bot_colors[number-1]
    )

    label(
        f"Reward: {bots[number-1][1]} trophies",
        y=0.36, scale=0.75,
        tint=color.gold
    )

    label("YOU = X     BOT = O", y=0.30, scale=0.85)

    for r in range(3):
        for c in range(3):
            index = r * 3 + c

            b = Button(
                text="",
                x=(c - 1) * 0.16,
                y=0.13 - r * 0.16,
                scale=(0.145, 0.145),
                color=color.rgb(65, 85, 125),
                highlight_color=color.azure,
                on_click=lambda i=index: player_move(i)
            )

            b.text_entity.scale = 2
            buttons.append(b)
            add_ui(b)

    global status_label

    status_label = label(
        "Your turn! Click a tile.",
        y=-0.39, scale=0.9,
        tint=color.lime
    )

    button("EXIT MATCH", 0, -0.46, lobby,
           color.rgb(125, 55, 65),
           size=(0.23, 0.05), text_size=0.75)


def redraw():
    for i, b in enumerate(buttons):
        b.text = board[i]
        b.text_entity.color = (
            color.gold if board[i] == "X"
            else color.azure
        )

        b.disabled = (
            board[i] != "" or busy or finished
        )


def player_move(index):
    global busy

    if screen != "match" or finished or busy:
        return

    if board[index] != "":
        return

    board[index] = "X"
    redraw()

    if has_won(board, "X"):
        finish_match("win")
        return

    if not moves(board):
        finish_match("draw")
        return

    busy = True
    redraw()
    status_label.text = "Bot is thinking..."

    invoke(ai_turn, delay=0.45)


def ai_turn():
    global busy

    if screen != "match" or finished:
        return

    move = ai_move()

    if move is not None:
        board[move] = "O"

    busy = False
    redraw()

    if has_won(board, "O"):
        finish_match("loss")
    elif not moves(board):
        finish_match("draw")
    else:
        status_label.text = "Your turn! Click a tile."


# =====================================================
# MATCH REWARDS
# =====================================================

def finish_match(result):
    global finished, busy

    finished = True
    busy = False
    redraw()

    if result == "win":
        trophy_reward = bots[bot_number - 1][1]
        coin_reward = bots[bot_number - 1][2]

        streak_bonus = min(data["streak"], 5) * 2
        training_bonus = int(
            coin_reward * data["training"] * 0.10
        )

        data["trophies"] += trophy_reward + streak_bonus
        data["coins"] += coin_reward + training_bonus
        data["wins"] += 1
        data["streak"] += 1
        data["best_streak"] = max(
            data["best_streak"], data["streak"]
        )

        data["xp"] += 35 + bot_number * 10

        data["unlocked"] = max(
            data["unlocked"],
            min(6, bot_number + 1)
        )

        result_text = "VICTORY!"
        result_color = color.lime

        reward_text = (
            f"+{trophy_reward + streak_bonus} trophies   "
            f"+{coin_reward + training_bonus} coins"
        )

    elif result == "loss":
        data["losses"] += 1
        data["streak"] = 0
        data["xp"] += 8

        result_text = "DEFEAT!"
        result_color = color.red
        reward_text = "Keep practicing and try again!"

    else:
        data["draws"] += 1
        data["streak"] = 0

        coin_reward = 3 + bot_number
        data["coins"] += coin_reward
        data["xp"] += 15

        result_text = "DRAW!"
        result_color = color.gold
        reward_text = f"+{coin_reward} coins"

    save_game()

    # Preserve the board but replace the interface.
    clear_ui()

    label(result_text, y=0.15, scale=2,
          tint=result_color)

    label(reward_text, y=0.05, scale=0.9,
          tint=color.gold)

    label(stats_text(), y=-0.02, scale=0.8)

    button(
        "REMATCH", -0.20, -0.12,
        lambda: start_match(bot_number),
        color.rgb(40, 110, 195)
    )

    button(
        "BOT SELECT", 0.20, -0.12,
        bot_select,
        color.rgb(155, 110, 35)
    )

    button("LOBBY", 0, -0.22, lobby,
           color.rgb(75, 85, 110))


# =====================================================
# TROPHY ROOM
# =====================================================

def trophy_room():
    global screen

    screen = "trophy"
    clear_ui()

    label("TROPHY ROOM", y=0.40, scale=2,
          tint=color.gold)

    label(
        f"Total trophies: {data['trophies']}",
        y=0.29, scale=1.2
    )

    label(
        f"Wins: {data['wins']}   "
        f"Losses: {data['losses']}   "
        f"Draws: {data['draws']}",
        y=0.21, scale=0.8
    )

    label(
        f"Current streak: {data['streak']}   "
        f"Best streak: {data['best_streak']}",
        y=0.15, scale=0.8,
        tint=color.gold
    )

    label(
        f"Player level: {level()}   "
        f"XP: {data['xp'] % 100}/100",
        y=0.09, scale=0.8,
        tint=color.azure
    )

    achievements = [
        (10, "BRONZE BEGINNER"),
        (50, "SILVER STRATEGIST"),
        (100, "GOLD TACTICIAN"),
        (250, "PLATINUM PRO"),
        (500, "DIAMOND CHAMPION"),
        (1000, "ARENA LEGEND")
    ]

    y = 0.01

    for amount, name in achievements:
        earned = data["trophies"] >= amount

        symbol = "UNLOCKED" if earned else "LOCKED"

        label(
            f"{symbol}  {name} - {amount} trophies",
            y=y, scale=0.7,
            tint=color.gold if earned else color.gray
        )

        y -= 0.047

    button("BACK", 0, -0.34, lobby,
           color.rgb(75, 85, 110))


# =====================================================
# HELP
# =====================================================

def help_screen():
    global screen

    screen = "help"
    clear_ui()

    label("HOW TO PLAY", y=0.38, scale=2,
          tint=color.azure)

    instructions = [
        "1. Choose Battle Bots.",
        "2. You play X. The AI plays O.",
        "3. Click a square to place your mark.",
        "4. Get three marks in a row to win.",
        "5. Stronger bots award more trophies.",
        "6. Use coins to train and increase coin rewards.",
        "7. Earn XP to level up.",
        "8. Unlock tougher bots by winning.",
        "9. Your progress saves to a JSON file.",
        "",
        "Perfect bots cannot be beaten if they play perfectly.",
        "Try to win against the easier bots first!"
    ]

    y = 0.23

    for line in instructions:
        label(line, y=y, scale=0.72)
        y -= 0.052

    button("BACK", 0, -0.40, lobby,
           color.rgb(75, 85, 110))


# =====================================================
# KEYBOARD CONTROLS
# =====================================================

def input(key):
    if key == "escape":
        lobby()


# =====================================================
# START GAME
# =====================================================

lobby()
app.run()
