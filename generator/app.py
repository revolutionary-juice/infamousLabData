import os
import time
import random
from datetime import datetime, timezone

import psycopg2
from psycopg2.extras import DictCursor

DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "analytics")
DB_USER = os.getenv("DB_USER", "app")
DB_PASS = os.getenv("DB_PASS", "app_pass")

PLAYER = os.getenv("PLAYER_NAME", "Cole_MacGrath")
PERIOD_SEC = float(os.getenv("PERIOD_SEC", "1.0"))

ACTIONS = [
    "kill_enemy",
    "kill_civilian",
    "moral_choice",
    "recharge",
    "mission_complete",
    "ability_upgrade",
]

ACTION_WEIGHTS = {
    "kill_enemy": 55,
    "kill_civilian": 8,
    "moral_choice": 10,
    "recharge": 15,
    "mission_complete": 8,
    "ability_upgrade": 4,
}

ENERGY_SOURCES = ["generator", "car", "power_station", "transformer_box"]

def compute_rank(karma_total: int) -> str:
    if karma_total >= 300:
        return "Hero_3"
    if karma_total >= 150:
        return "Hero_2"
    if karma_total >= 50:
        return "Hero_1"
    if karma_total <= -300:
        return "Infamous_3"
    if karma_total <= -150:
        return "Infamous_2"
    if karma_total <= -50:
        return "Infamous_1"
    return "Neutral"

def pick_action() -> str:
    population = list(ACTION_WEIGHTS.keys())
    weights = [ACTION_WEIGHTS[a] for a in population]
    return random.choices(population, weights=weights, k=1)[0]

def generate_event():
    action = pick_action()

    xp_delta = 0
    karma_delta = 0
    energy_source = None

    if action == "kill_enemy":
        xp_delta = random.randint(10, 40)
        karma_delta = random.choice([0, 0, 0, 1, -1])  # чаще 0
    elif action == "kill_civilian":
        xp_delta = random.randint(0, 8)
        karma_delta = -random.randint(20, 50)
    elif action == "moral_choice":
        xp_delta = random.randint(5, 20)
        karma_delta = random.choice([random.randint(30, 60), -random.randint(30, 60)])
    elif action == "recharge":
        xp_delta = 0
        karma_delta = 0
        energy_source = random.choice(ENERGY_SOURCES)
    elif action == "mission_complete":
        xp_delta = random.randint(80, 200)
        karma_delta = random.choice([random.randint(5, 20), -random.randint(5, 20), 0])
    elif action == "ability_upgrade":
        xp_delta = 0
        karma_delta = 0

    return action, xp_delta, karma_delta, energy_source

def wait_for_db(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT 1;")

def get_last_karma_total(conn) -> int:
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute("SELECT karma_total FROM game_events ORDER BY id DESC LIMIT 1;")
        row = cur.fetchone()
        return int(row["karma_total"]) if row else 0

def insert_event(conn, player, action, xp_delta, karma_delta, karma_total, rank, energy_source):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO game_events (ts, player, action, xp_delta, karma_delta, karma_total, rank, energy_source)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """,
            (datetime.now(timezone.utc), player, action, xp_delta, karma_delta, karma_total, rank, energy_source),
        )
    conn.commit()

def main():
    while True:
        try:
            conn = psycopg2.connect(
                host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASS
            )
            break
        except Exception as e:
            print("[GEN] DB not ready, retrying...", repr(e))
            time.sleep(2)

    print("[GEN] Connected to DB")

    while True:
        try:
            wait_for_db(conn)
            break
        except Exception as e:
            print("[GEN] Waiting for DB...", repr(e))
            time.sleep(2)

    while True:
        try:
            last_total = get_last_karma_total(conn)
            action, xp_delta, karma_delta, energy_source = generate_event()

            karma_total = last_total + karma_delta
            rank = compute_rank(karma_total)

            insert_event(conn, PLAYER, action, xp_delta, karma_delta, karma_total, rank, energy_source)

            print(f"[GEN] {action:15s} xp={xp_delta:3d} karma={karma_delta:4d} total={karma_total:5d} rank={rank}")
            time.sleep(PERIOD_SEC)
        except Exception as e:
            print("[GEN] error:", repr(e))
            try:
                conn.close()
            except Exception:
                pass
            time.sleep(2)
            conn = psycopg2.connect(
                host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASS
            )

if __name__ == "__main__":
    main()
