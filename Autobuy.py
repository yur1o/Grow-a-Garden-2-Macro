import threading
import json
import os
import time
import pydirectinput

# ── Configuration ────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

_active_items = [] 

_worker_thread = None
_worker_category = None
_macro_running = False  

_wake_event = threading.Event()

_registry_lock = threading.Lock()

_emit_log = None

def set_logger(emit_log_fn):
    global _emit_log
    _emit_log = emit_log_fn

def log(msg, tag="info"):
    if _emit_log:
        _emit_log(msg, tag)


def _get_interval() -> float:
    # Default: 60 seconds (1 minute)
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE) as f:
                config = json.load(f)
                interval = config.get("interval", 60)
                return max(60, min(300, interval))
    except Exception:
        pass
    return 60


def set_macro_running(is_running: bool):
    global _macro_running
    _macro_running = is_running
    if not is_running:
        _wake_event.set()


def _buy_map_for(category: str) -> dict:
    if category == "seeds":
        return SEED_BUY_MAP
    if category == "gears":
        return GEAR_BUY_MAP
    return {}


def _worker_loop(category: str):

    buy_map = _buy_map_for(category)

    while _macro_running:
        with _registry_lock:
            items_this_cycle = list(_active_items)

        for item_name in items_this_cycle:
            if not _macro_running:
                return

            with _registry_lock:
                still_active = item_name in _active_items

            if not still_active:
                continue

            buy_fn = buy_map.get(item_name)
            if not buy_fn:
                continue

            try:
                buy_fn()
            except Exception as e:
                log(f"Error in {item_name} loop: {e}")

        if not _macro_running:
            return

        interval = _get_interval()
        _wake_event.clear()
        _wake_event.wait(timeout=interval)


def _ensure_worker_running(category: str):
    global _worker_thread, _worker_category
    with _registry_lock:
        if _worker_thread and _worker_thread.is_alive():
            return 
        _worker_category = category
        _worker_thread = threading.Thread(
            target=_worker_loop, args=(category,), daemon=True, name="autobuy-worker"
        )
        _worker_thread.start()


def _stop_worker():
    global _worker_thread
    _wake_event.set()
    if _worker_thread and _worker_thread.is_alive():
        _worker_thread.join(timeout=2)
    _worker_thread = None


# ─────────────────────────────────────────────────────────────────────────────
# SEEDS (25 types)
# ─────────────────────────────────────────────────────────────────────────────

DELAY = 0.15

def buy_carrot():
    log("Buying Carrot seed.", "info")

    time.sleep(DELAY)
    pydirectinput.press('enter')
    time.sleep(DELAY)

    pydirectinput.press('down')

    time.sleep(DELAY)
    pydirectinput.press('enter', presses=5,)
    time.sleep(DELAY)
    log("Carrot purchased.", "info")

    pydirectinput.press('up')
    time.sleep(DELAY)

    pydirectinput.press('enter')
    
    time.sleep(DELAY)

    pass

def buy_strawberry():
    log("Buying Strawberry seed.", "info")

    time.sleep(DELAY)
    pydirectinput.press('down')
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)

    pydirectinput.press('down')
    time.sleep(DELAY)
    pydirectinput.press('enter', presses=5)
    time.sleep(DELAY)
    log("Strawberry purchased.", "info")

    pydirectinput.press('up')
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)
    pydirectinput.press('up')

    pass

def buy_blueberry():
    log("Buying Blueberry seed.", "info")

    time.sleep(DELAY)
    pydirectinput.press('down', presses=2)
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)

    pydirectinput.press('down')
    time.sleep(DELAY)
    pydirectinput.press('enter', presses=5)
    time.sleep(DELAY)
    log("Blueberry purchased.", "info")

    pydirectinput.press('up')
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)
    pydirectinput.press('up', presses=2)

    pass

def buy_tulip():
    log("Buying Tulip seed.", "info")

    time.sleep(DELAY)
    pydirectinput.press('down', presses=3)
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)

    pydirectinput.press('down')
    time.sleep(DELAY)
    pydirectinput.press('enter', presses=5)
    time.sleep(DELAY)
    log("Tulip purchased.", "info")

    pydirectinput.press('up')
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)
    pydirectinput.press('up', presses=3)

    pass

def buy_tomato():
    log("Buying Tomato seed.", "info")

    time.sleep(DELAY)
    pydirectinput.press('down', presses=4)
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)

    pydirectinput.press('down')
    time.sleep(DELAY)
    pydirectinput.press('enter', presses=5)
    time.sleep(DELAY)
    log("Tomato purchased.", "info")

    pydirectinput.press('up')
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)
    pydirectinput.press('up', presses=4)

    pass

def buy_apple():
    log("Buying Apple seed.", "info")

    time.sleep(DELAY)
    pydirectinput.press('down', presses=5)
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)

    pydirectinput.press('down')
    time.sleep(DELAY)
    pydirectinput.press('enter', presses=5)
    time.sleep(DELAY)
    log("Apple purchased.", "info")

    pydirectinput.press('up')
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)
    pydirectinput.press('up', presses=5)

    pass

def buy_bamboo():
    log("Buying Bamboo seed.", "info")

    time.sleep(DELAY)
    pydirectinput.press('down', presses=6)
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)

    pydirectinput.press('down')
    time.sleep(DELAY)
    pydirectinput.press('enter', presses=5)
    time.sleep(DELAY)
    log("Bamboo purchased.", "info")

    pydirectinput.press('up')
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)
    pydirectinput.press('up', presses=6)

    pass

def buy_corn():
    log("Buying Corn seed.", "info")

    time.sleep(DELAY)
    pydirectinput.press('down', presses=7)
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)

    pydirectinput.press('down')
    time.sleep(DELAY)
    pydirectinput.press('enter', presses=5)
    time.sleep(DELAY)
    log("Corn purchased.", "info")

    pydirectinput.press('up')
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)
    pydirectinput.press('up', presses=7)

    pass

def buy_cactus():
    log("Buying Cactus seed.", "info")

    time.sleep(DELAY)
    pydirectinput.press('down', presses=8)
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)

    pydirectinput.press('down')
    time.sleep(DELAY)
    pydirectinput.press('enter', presses=5)
    time.sleep(DELAY)
    log("Cactus purchased.", "info")

    pydirectinput.press('up')
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)
    pydirectinput.press('up', presses=8)

    pass

def buy_pineapple():
    log("Buying Pineapple seed.", "info")

    time.sleep(DELAY)
    pydirectinput.press('down', presses=9)
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)

    pydirectinput.press('down')
    time.sleep(DELAY)
    pydirectinput.press('enter', presses=5)
    time.sleep(DELAY)
    log("Pineapple purchased.", "info")

    pydirectinput.press('up')
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)
    pydirectinput.press('up', presses=9)

    pass

def buy_mushroom():
    log("Buying Mushroom seed.", "info")

    time.sleep(DELAY)
    pydirectinput.press('down', presses=10)
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)

    pydirectinput.press('down')
    time.sleep(DELAY)
    pydirectinput.press('enter', presses=5)
    time.sleep(DELAY)
    log("Mushroom purchased.", "info")

    pydirectinput.press('up')
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)
    pydirectinput.press('up', presses=10)

    pass

def buy_green_bean():
    log("Buying Green Bean seed.", "info")

    time.sleep(DELAY)
    pydirectinput.press('down', presses=11)
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)

    pydirectinput.press('down')
    time.sleep(DELAY)
    pydirectinput.press('enter', presses=5)
    time.sleep(DELAY)
    log("Green Bean purchased.", "info")

    pydirectinput.press('up')
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)
    pydirectinput.press('up', presses=11)

    pass

def buy_banana():
    log("Buying Banana seed.", "info")

    time.sleep(DELAY)
    pydirectinput.press('down', presses=12)
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)

    pydirectinput.press('down')
    time.sleep(DELAY)
    pydirectinput.press('enter', presses=5)
    time.sleep(DELAY)
    log("Banana purchased.", "info")

    pydirectinput.press('up')
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)
    pydirectinput.press('up', presses=12)

    pass

def buy_grape():
    log("Buying Grape seed.", "info")

    time.sleep(DELAY)
    pydirectinput.press('down', presses=13)
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)

    pydirectinput.press('down')
    time.sleep(DELAY)
    pydirectinput.press('enter', presses=5)
    time.sleep(DELAY)
    log("Grape purchased.", "info")

    pydirectinput.press('up')
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)
    pydirectinput.press('up', presses=13)

    pass

def buy_coconut():
    log("Buying Coconut seed.", "info")

    time.sleep(DELAY)
    pydirectinput.press('down', presses=14)
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)

    pydirectinput.press('down')
    time.sleep(DELAY)
    pydirectinput.press('enter', presses=5)
    time.sleep(DELAY)
    log("Coconut purchased.", "info")
    pydirectinput.press('up')
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)
    pydirectinput.press('up', presses=14)

    pass

def buy_mango():
    log("Buying Mango seed.", "info")

    time.sleep(DELAY)
    pydirectinput.press('down', presses=15)
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)

    pydirectinput.press('down')
    time.sleep(DELAY)
    pydirectinput.press('enter', presses=5)
    time.sleep(DELAY)
    log("Mango purchased.", "info")

    pydirectinput.press('up')
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)
    pydirectinput.press('up', presses=15)

    pass

def buy_dragon_fruit():
    log("Buying Dragon Fruit seed.", "info")

    time.sleep(DELAY)
    pydirectinput.press('down', presses=16)
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)

    pydirectinput.press('down')
    time.sleep(DELAY)
    pydirectinput.press('enter', presses=5)
    time.sleep(DELAY)
    log("Dragon Fruit purchased.", "info")

    pydirectinput.press('up')
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)
    pydirectinput.press('up', presses=16)

    pass

def buy_acorn():
    log("Buying Acorn seed.", "info")

    time.sleep(DELAY)
    pydirectinput.press('down', presses=17)
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)

    pydirectinput.press('down')
    time.sleep(DELAY)
    pydirectinput.press('enter', presses=5)
    time.sleep(DELAY)
    log("Acorn purchased.", "info")

    pydirectinput.press('up')
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)
    pydirectinput.press('up', presses=17)

    pass

def buy_cherry():
    log("Buying Cherry seed.", "info")

    time.sleep(DELAY)
    pydirectinput.press('down', presses=18)
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)

    pydirectinput.press('down')
    time.sleep(DELAY)
    pydirectinput.press('enter', presses=5)
    time.sleep(DELAY)
    log("Cherry purchased.", "info")

    pydirectinput.press('up')
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)
    pydirectinput.press('up', presses=18)

    pass

def buy_sunflower():
    log("Buying Sunflower seed.", "info")

    time.sleep(DELAY)
    pydirectinput.press('down', presses=19)
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)

    pydirectinput.press('down')
    time.sleep(DELAY)
    pydirectinput.press('enter', presses=5)
    time.sleep(DELAY)
    log("Sunflower purchased.", "info")

    pydirectinput.press('up')
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)
    pydirectinput.press('up', presses=19)

    pass

def buy_venus_fly_trap():
    log("Buying Venus Fly Trap seed.", "info")

    time.sleep(DELAY)
    pydirectinput.press('down', presses=20)
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)

    pydirectinput.press('down')
    time.sleep(DELAY)
    pydirectinput.press('enter', presses=5)
    time.sleep(DELAY)
    log("Venus Fly Trap purchased.", "info")

    pydirectinput.press('up')
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)
    pydirectinput.press('up', presses=20)

    pass

def buy_pomegranate():
    log("Buying Pomegranate seed.", "info")

    time.sleep(DELAY)
    pydirectinput.press('down', presses=21)
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)

    pydirectinput.press('down')
    time.sleep(DELAY)
    pydirectinput.press('enter', presses=5)
    time.sleep(DELAY)
    log("Pomegranate purchased.", "info")

    pydirectinput.press('up')
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)
    pydirectinput.press('up', presses=21)

    pass

def buy_poison_apple():
    log("Buying Poison Apple seed.", "info")

    time.sleep(DELAY)
    pydirectinput.press('down', presses=22)
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)

    pydirectinput.press('down')
    time.sleep(DELAY)
    pydirectinput.press('enter', presses=5)
    time.sleep(DELAY)
    log("Poison Apple purchased.", "info")

    pydirectinput.press('up')
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)
    pydirectinput.press('up', presses=22)

    pass

def buy_moon_bloom():
    log("Buying Moon Bloom seed.", "info")

    time.sleep(DELAY)
    pydirectinput.press('down', presses=23)
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)

    pydirectinput.press('down')
    time.sleep(DELAY)
    pydirectinput.press('enter', presses=5)
    time.sleep(DELAY)
    log("Moon Bloom purchased.", "info")

    pydirectinput.press('up')
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)
    pydirectinput.press('up', presses=23)

    pass

def buy_dragons_breath():
    log("Buying Dragon's Breath seed.", "info")

    time.sleep(DELAY)
    pydirectinput.press('down', presses=24)
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)

    pydirectinput.press('down')
    time.sleep(DELAY)
    pydirectinput.press('enter', presses=5)
    time.sleep(DELAY)
    log("Dragon's Breath purchased.", "info")

    pydirectinput.press('up')
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)
    pydirectinput.press('up', presses=24)

    pass


# ─────────────────────────────────────────────────────────────────────────────
# GEARS (20 types)
# ─────────────────────────────────────────────────────────────────────────────

def buy_common_watering_can():
    log("Buying Common Watering Can.", "info")

    time.sleep(DELAY)
    pydirectinput.press('enter')
    time.sleep(DELAY)

    pydirectinput.press('down')
    time.sleep(DELAY)
    pydirectinput.press('enter', presses=5)
    time.sleep(DELAY)
    log("Common Watering Can purchased.", "info")

    pydirectinput.press('up')
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)

    pass

def buy_common_sprinkler():
    log("Buying Common Sprinkler.", "info")

    time.sleep(DELAY)
    pydirectinput.press('down', presses=1)
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)

    pydirectinput.press('down')
    time.sleep(DELAY)
    pydirectinput.press('enter', presses=5)
    time.sleep(DELAY)
    log("Common Sprinkler purchased.", "info")

    pydirectinput.press('up')
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)
    pydirectinput.press('up', presses=1)

    pass

def buy_sign():
    log("Buying Sign.", "info")

    time.sleep(DELAY)
    pydirectinput.press('down', presses=2)
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)

    pydirectinput.press('down')
    time.sleep(DELAY)
    pydirectinput.press('enter', presses=5)
    time.sleep(DELAY)
    log("Sign purchased.", "info")

    pydirectinput.press('up')
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)
    pydirectinput.press('up', presses=2)

    pass

def buy_uncommon_sprinkler():
    log("Buying Uncommon Sprinkler.", "info")

    time.sleep(DELAY)
    pydirectinput.press('down', presses=3)
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)

    pydirectinput.press('down')
    time.sleep(DELAY)
    pydirectinput.press('enter', presses=5)
    time.sleep(DELAY)
    log("Uncommon Sprinkler purchased.", "info")

    pydirectinput.press('up')
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)
    pydirectinput.press('up', presses=3)

    pass

def buy_trowel():
    log("Buying Trowel.", "info")

    time.sleep(DELAY)
    pydirectinput.press('down', presses=4)
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)

    pydirectinput.press('down')
    time.sleep(DELAY)
    pydirectinput.press('enter', presses=5)
    time.sleep(DELAY)
    log("Trowel purchased.", "info")

    pydirectinput.press('up')
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)
    pydirectinput.press('up', presses=4)

    pass

def buy_rare_sprinkler():
    log("Buying Rare Sprinkler.", "info")

    time.sleep(DELAY)
    pydirectinput.press('down', presses=5)
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)

    pydirectinput.press('down')
    time.sleep(DELAY)
    pydirectinput.press('enter', presses=5)
    time.sleep(DELAY)
    log("Rare Sprinkler purchased.", "info")

    pydirectinput.press('up')
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)
    pydirectinput.press('up', presses=5)

    pass

def buy_jump_mushroom():
    log("Buying Jump Mushroom.", "info")

    time.sleep(DELAY)
    pydirectinput.press('down', presses=6)
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)

    pydirectinput.press('down')
    time.sleep(DELAY)
    pydirectinput.press('enter', presses=5)
    time.sleep(DELAY)
    log("Jump Mushroom purchased.", "info")

    pydirectinput.press('up')
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)
    pydirectinput.press('up', presses=6)

    pass

def buy_speed_mushroom():
    log("Buying Speed Mushroom.", "info")

    time.sleep(DELAY)
    pydirectinput.press('down', presses=7)
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)

    pydirectinput.press('down')
    time.sleep(DELAY)
    pydirectinput.press('enter', presses=5)
    time.sleep(DELAY)
    log("Speed Mushroom purchased.", "info")

    pydirectinput.press('up')
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)
    pydirectinput.press('up', presses=7)

    pass

def buy_lantern():
    log("Buying Lantern.", "info")

    time.sleep(DELAY)
    pydirectinput.press('down', presses=8)
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)

    pydirectinput.press('down')
    time.sleep(DELAY)
    pydirectinput.press('enter', presses=5)
    time.sleep(DELAY)
    log("Lantern purchased.", "info")

    pydirectinput.press('up')
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)
    pydirectinput.press('up', presses=8)

    pass

def buy_shrink_mushroom():
    log("Buying Shrink Mushroom.", "info")

    time.sleep(DELAY)
    pydirectinput.press('down', presses=9)
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)

    pydirectinput.press('down')
    time.sleep(DELAY)
    pydirectinput.press('enter', presses=5)
    time.sleep(DELAY)
    log("Shrink Mushroom purchased.", "info")

    pydirectinput.press('up')
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)
    pydirectinput.press('up', presses=9)

    pass

def buy_supersize_mushroom():
    log("Buying Supersize Mushroom.", "info")

    time.sleep(DELAY)
    pydirectinput.press('down', presses=10)
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)

    pydirectinput.press('down')
    time.sleep(DELAY)
    pydirectinput.press('enter', presses=5)
    time.sleep(DELAY)
    log("Supersize Mushroom purchased.", "info")

    pydirectinput.press('up')
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)
    pydirectinput.press('up', presses=10)

    pass

def buy_gnome():
    log("Buying Gnome.", "info")

    time.sleep(DELAY)
    pydirectinput.press('down', presses=11)
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)

    pydirectinput.press('down')
    time.sleep(DELAY)
    pydirectinput.press('enter', presses=5)
    time.sleep(DELAY)
    log("Gnome purchased.", "info")

    pydirectinput.press('up')
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)
    pydirectinput.press('up', presses=11)

    pass

def buy_flashbang():
    log("Buying Flashbang.", "info")

    time.sleep(DELAY)
    pydirectinput.press('down', presses=12)
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)

    pydirectinput.press('down')
    time.sleep(DELAY)
    pydirectinput.press('enter', presses=5)
    time.sleep(DELAY)
    log("Flashbang purchased.", "info")

    pydirectinput.press('up')
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)
    pydirectinput.press('up', presses=12)

    pass

def buy_legendary_sprinkler():
    log("Buying Legendary Sprinkler.", "info")

    time.sleep(DELAY)
    pydirectinput.press('down', presses=13)
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)

    pydirectinput.press('down')
    time.sleep(DELAY)
    pydirectinput.press('enter', presses=5)
    time.sleep(DELAY)
    log("Legendary Sprinkler purchased.", "info")

    pydirectinput.press('up')
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)
    pydirectinput.press('up', presses=13)

    pass

def buy_basic_pot():
    log("Buying Basic Pot.", "info")

    time.sleep(DELAY)
    pydirectinput.press('down', presses=14)
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)

    pydirectinput.press('down')
    time.sleep(DELAY)
    pydirectinput.press('enter', presses=5)
    time.sleep(DELAY)
    log("Basic Pot purchased.", "info")

    pydirectinput.press('up')
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)
    pydirectinput.press('up', presses=14)

    pass

def buy_invisibility_mushroom():
    log("Buying Invisibility Mushroom.", "info")

    time.sleep(DELAY)
    pydirectinput.press('down', presses=15)
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)

    pydirectinput.press('down')
    time.sleep(DELAY)
    pydirectinput.press('enter', presses=5)
    time.sleep(DELAY)
    log("Invisibility Mushroom purchased.", "info")

    pydirectinput.press('up')
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)
    pydirectinput.press('up', presses=15)

    pass

def buy_teleporter():
    log("Buying Teleporter.", "info")

    time.sleep(DELAY)
    pydirectinput.press('down', presses=16)
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)

    pydirectinput.press('down')
    time.sleep(DELAY)
    pydirectinput.press('enter', presses=5)
    time.sleep(DELAY)
    log("Teleporter purchased.", "info")

    pydirectinput.press('up')
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)
    pydirectinput.press('up', presses=16)

    pass

def buy_wheelbarrow():
    log("Buying Wheelbarrow.", "info")

    time.sleep(DELAY)
    pydirectinput.press('down', presses=17)
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)

    pydirectinput.press('down')
    time.sleep(DELAY)
    pydirectinput.press('enter', presses=5)
    time.sleep(DELAY)
    log("Wheelbarrow purchased.", "info")

    pydirectinput.press('up')
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)
    pydirectinput.press('up', presses=17)

    pass

def buy_super_watering_can():
    log("Buying Super Watering Can.", "info")

    time.sleep(DELAY)
    pydirectinput.press('down', presses=18)
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)

    pydirectinput.press('down')
    time.sleep(DELAY)
    pydirectinput.press('enter', presses=5)
    time.sleep(DELAY)
    log("Super Watering Can purchased.", "info")

    pydirectinput.press('up')
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)
    pydirectinput.press('up', presses=18)

    pass

def buy_super_sprinkler():
    log("Buying Super Sprinkler.", "info")

    time.sleep(DELAY)
    pydirectinput.press('down', presses=19)
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)

    pydirectinput.press('down')
    time.sleep(DELAY)
    pydirectinput.press('enter', presses=5)
    time.sleep(DELAY)
    log("Super Sprinkler purchased.", "info")

    pydirectinput.press('up')
    time.sleep(DELAY)

    pydirectinput.press('enter')
    time.sleep(DELAY)
    pydirectinput.press('up', presses=19)

    pass

# ─────────────────────────────────────────────────────────────────────────────
# Controls for toggling items on/off
# ─────────────────────────────────────────────────────────────────────────────

# Mapping of seed names (from config.json) to buy functions
SEED_BUY_MAP = {
    "Carrot": buy_carrot,
    "Strawberry": buy_strawberry,
    "Blueberry": buy_blueberry,
    "Tulip": buy_tulip,
    "Tomato": buy_tomato,
    "Apple": buy_apple,
    "Bamboo": buy_bamboo,
    "Corn": buy_corn,
    "Cactus": buy_cactus,
    "Pineapple": buy_pineapple,
    "Mushroom": buy_mushroom,
    "Green Bean": buy_green_bean,
    "Banana": buy_banana,
    "Grape": buy_grape,
    "Coconut": buy_coconut,
    "Mango": buy_mango,
    "Dragon Fruit": buy_dragon_fruit,
    "Acorn": buy_acorn,
    "Cherry": buy_cherry,
    "Sunflower": buy_sunflower,
    "Venus Fly Trap": buy_venus_fly_trap,
    "Pomegranate": buy_pomegranate,
    "Poison Apple": buy_poison_apple,
    "Moon Bloom": buy_moon_bloom,
    "Dragon's Breath": buy_dragons_breath,
}

# Mapping of gear names (from config.json) to buy functions
GEAR_BUY_MAP = {
    "Common Watering Can": buy_common_watering_can,
    "Common Sprinkler": buy_common_sprinkler,
    "Sign": buy_sign,
    "Uncommon Sprinkler": buy_uncommon_sprinkler,
    "Trowel": buy_trowel,
    "Rare Sprinkler": buy_rare_sprinkler,
    "Jump Mushroom": buy_jump_mushroom,
    "Speed Mushroom": buy_speed_mushroom,
    "Lantern": buy_lantern,
    "Shrink Mushroom": buy_shrink_mushroom,
    "Supersize Mushroom": buy_supersize_mushroom,
    "Gnome": buy_gnome,
    "Flashbang": buy_flashbang,
    "Legendary Sprinkler": buy_legendary_sprinkler,
    "Basic Pot": buy_basic_pot,
    "Invisibility Mushroom": buy_invisibility_mushroom,
    "Teleporter": buy_teleporter,
    "Wheelbarrow": buy_wheelbarrow,
    "Super Watering Can": buy_super_watering_can,
    "Super Sprinkler": buy_super_sprinkler,
}


def toggle_autobuy(category: str, item_name: str, is_active: bool):

    buy_map = _buy_map_for(category)
    if not buy_map or item_name not in buy_map:
        return False

    with _registry_lock:
        if is_active:
            if item_name not in _active_items:
                _active_items.append(item_name)
        else:
            if item_name in _active_items:
                _active_items.remove(item_name)

    if is_active:
        _ensure_worker_running(category)

    return True


def stop_all_autobuys():
    global _active_items
    _stop_worker()
    with _registry_lock:
        _active_items = []


def get_active_items() -> list:
    with _registry_lock:
        return list(_active_items)
