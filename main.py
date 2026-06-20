"""
Roblox Grow a Garden 2 Macro Made by yur1o
"""
import webview
import ctypes
import json
import os
import sys
import threading
import time

# -- Autobuy module ----
try:
    import Autobuy
    AUTOBUY_OK = True
except Exception:
    AUTOBUY_OK = False

# -- Win32 ---------------------------------------------------------------------
try:
    import win32gui, win32con, win32process
    WIN32_OK = True
except ImportError:
    WIN32_OK = False

# -- Hotkeys via pynput (no admin required) ------------------------------------
try:
    from pynput import keyboard as pynput_kb
    KB_OK = True
except Exception:
    KB_OK = False

# -- Config --------------------------------------------------------------------
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

def writable_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

CONFIG_FILE = writable_path("config.json")
GUI_PATH    = resource_path(os.path.join("gui", "index.html"))

DEFAULT_CONFIG = {
    "theme": "default",
    "mode": "seeds",  # "seeds" or "gears" - which mode is currently active
    "hotkeys": {
        "Start": "F1",
        "Stop":  "F2",
        "Exit":  "F3",
    },
    "seeds": {},
    "gears": {}
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f:
                data = json.load(f)
                data.setdefault("theme", DEFAULT_CONFIG["theme"])
                data.setdefault("mode", DEFAULT_CONFIG["mode"])
                for k, v in DEFAULT_CONFIG["hotkeys"].items():
                    data.setdefault("hotkeys", {}).setdefault(k, v)
                return data
        except Exception:
            pass
    return json.loads(json.dumps(DEFAULT_CONFIG))

def save_config(c):
    with open(CONFIG_FILE, "w") as f:
        json.dump(c, f, indent=2)

# -- State ---------------------------------------------------------------------
cfg            = load_config()
macro_running  = False
roblox_focused = False
window         = None   # assigned after webview.create_window
_hotkey_listener = None  # the active pynput Listener
_app_hwnd = None
_active_mode = cfg.get("mode", "seeds")  # Track current active mode
_start_stop_lock = threading.Lock()  # guards macro_running against racing start() calls

# -- pynput key normalisation --------------------------------------------------
def _str_to_pynput_key(key_str):
    """
    Convert a string like 'f1', 'a', 'ctrl' to a pynput Key or KeyCode.
    pynput uses Key.f1 for special keys and KeyCode.from_char('a') for chars.
    """
    key_str = key_str.lower().strip()
    # Try named special keys first (f1-f12, esc, space, etc.)
    try:
        return pynput_kb.Key[key_str]          # e.g. Key.f1, Key.esc
    except KeyError:
        pass
    # Single printable character
    if len(key_str) == 1:
        return pynput_kb.KeyCode.from_char(key_str)
    # Fallback - try vk lookup via char (handles 'enter', 'tab', etc.)
    try:
        return pynput_kb.Key[key_str]
    except Exception:
        return None

def _pynput_key_matches(pressed_key, target_key):
    """Return True if the pressed pynput key matches our target."""
    if target_key is None:
        return False
    # Special key comparison
    if isinstance(target_key, pynput_kb.Key):
        return pressed_key == target_key
    # KeyCode char comparison (case-insensitive)
    if isinstance(target_key, pynput_kb.KeyCode):
        if isinstance(pressed_key, pynput_kb.KeyCode):
            return (pressed_key.char or '').lower() == (target_key.char or '').lower()
    return False

# -- Hotkey listener -----------------------------------------------------------
_HOTKEY_DEBOUNCE_SECS = 0.35
_last_hotkey_fire = {}  

def _build_hotkey_map():
    action_fns = {"Start": api_start, "Stop": api_stop, "Exit": api_exit}
    hmap = []
    for action, key_str in cfg["hotkeys"].items():
        pk = _str_to_pynput_key(key_str)
        fn = action_fns.get(action)
        if pk and fn:
            hmap.append((pk, action, fn))
    return hmap

def register_hotkeys():
    global _hotkey_listener
    if not KB_OK:
        return

    if _hotkey_listener:
        try:
            _hotkey_listener.stop()
        except Exception:
            pass
        _hotkey_listener = None

    hotkey_map = _build_hotkey_map()
    if not hotkey_map:
        return

    def on_press(key):
        now = time.monotonic()
        for target_key, action, fn in hotkey_map:
            if _pynput_key_matches(key, target_key):
                last = _last_hotkey_fire.get(action, 0)
                if now - last < _HOTKEY_DEBOUNCE_SECS:
                    return  
                _last_hotkey_fire[action] = now
                threading.Thread(target=fn, daemon=True).start()
                return

    _hotkey_listener = pynput_kb.Listener(on_press=on_press)
    _hotkey_listener.daemon = True
    _hotkey_listener.start()

def stop_hotkeys():
    global _hotkey_listener
    if _hotkey_listener:
        try:
            _hotkey_listener.stop()
        except Exception:
            pass
        _hotkey_listener = None

# -- Roblox window management --------------------------------------------------
APP_WINDOW_TITLE = "Grow a Garden 2 Macro"
ROBLOX_AREA_WIDTH = 800
ROBLOX_AREA_HEIGHT = 568
TITLE_BAR_HEIGHT = 40
WINDOW_BORDER_WIDTH = 1
ROBLOX_BOX_LEFT_INSET = 4
ROBLOX_BOX_BOTTOM_TRIM = 20
ROBLOX_FRAME_LEFT_HIDE = 10
ROBLOX_FRAME_RIGHT_HIDE = 8
ROBLOX_TITLEBAR_HIDE = 32
RGN_DIFF = 4

def _find_visible_window_by_title(match_text, exact=False, exclude_hwnd=None):
    if not WIN32_OK:
        return None

    match_text = match_text.lower()
    found_hwnd = None

    def enum_handler(hwnd, _):
        nonlocal found_hwnd
        if found_hwnd or hwnd == exclude_hwnd or not win32gui.IsWindowVisible(hwnd):
            return

        title = win32gui.GetWindowText(hwnd).strip()
        if not title:
            return

        title_lower = title.lower()
        matched = title_lower == match_text if exact else match_text in title_lower
        if matched:
            found_hwnd = hwnd

    win32gui.EnumWindows(enum_handler, None)
    return found_hwnd

def _get_app_hwnd():
    global _app_hwnd
    if _app_hwnd and win32gui.IsWindow(_app_hwnd):
        return _app_hwnd

    current_pid = os.getpid()
    candidates = []

    def enum_handler(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd):
            return

        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        if pid == current_pid:
            rect = win32gui.GetWindowRect(hwnd)
            width = rect[2] - rect[0]
            height = rect[3] - rect[1]
            title = win32gui.GetWindowText(hwnd).strip()
            if width > 300 and height > 300:
                candidates.append((hwnd, title, width * height))

    win32gui.EnumWindows(enum_handler, None)
    if candidates:
        exact = [item for item in candidates if item[1] == APP_WINDOW_TITLE]
        _app_hwnd = max(exact or candidates, key=lambda item: item[2])[0]
        return _app_hwnd

    hwnd = _find_visible_window_by_title(APP_WINDOW_TITLE, exact=True)
    if hwnd:
        _app_hwnd = hwnd
        return hwnd

    _app_hwnd = _find_visible_window_by_title(APP_WINDOW_TITLE)
    return _app_hwnd

def _get_roblox_hwnd(app_hwnd=None):
    hwnd = win32gui.FindWindow(None, "Roblox")
    if hwnd and hwnd != app_hwnd and win32gui.IsWindowVisible(hwnd):
        return hwnd
    return None

def restore_roblox_window(hwnd):
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

def apply_window_cutout():
    if not WIN32_OK:
        return False

    app_hwnd = _get_app_hwnd()
    if not app_hwnd:
        return False

    rect = win32gui.GetWindowRect(app_hwnd)
    width = rect[2] - rect[0]
    height = rect[3] - rect[1]
    roblox_box_x = WINDOW_BORDER_WIDTH + ROBLOX_BOX_LEFT_INSET
    roblox_box_y = TITLE_BAR_HEIGHT + WINDOW_BORDER_WIDTH
    roblox_box_width = ROBLOX_AREA_WIDTH - ROBLOX_BOX_LEFT_INSET
    roblox_box_height = max(
        100,
        height - TITLE_BAR_HEIGHT - (WINDOW_BORDER_WIDTH * 2) - ROBLOX_BOX_BOTTOM_TRIM,
    )

    full_region = ctypes.windll.gdi32.CreateRectRgn(0, 0, width, height)
    hole_region = ctypes.windll.gdi32.CreateRectRgn(
        roblox_box_x,
        roblox_box_y,
        roblox_box_x + roblox_box_width,
        roblox_box_y + roblox_box_height,
    )
    ctypes.windll.gdi32.CombineRgn(full_region, full_region, hole_region, RGN_DIFF)
    ctypes.windll.user32.SetWindowRgn(app_hwnd, full_region, True)
    ctypes.windll.gdi32.DeleteObject(hole_region)

    win32gui.SetWindowPos(
        app_hwnd,
        win32con.HWND_TOPMOST,
        0,
        0,
        0,
        0,
        win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE,
    )
    return True

def move_roblox():
    global roblox_focused
    if not WIN32_OK or not window:
        return False
    
    try:
        app_hwnd = _get_app_hwnd()
        if not app_hwnd:
            emit_log("Could not find app window", "error")
            return False

        rect = win32gui.GetWindowRect(app_hwnd)
        app_x, app_y = rect[0], rect[1]
        app_height = rect[3] - rect[1]
        
        roblox_box_x = app_x + WINDOW_BORDER_WIDTH + ROBLOX_BOX_LEFT_INSET
        roblox_box_y = app_y + TITLE_BAR_HEIGHT + WINDOW_BORDER_WIDTH
        roblox_box_width = ROBLOX_AREA_WIDTH - ROBLOX_BOX_LEFT_INSET
        roblox_box_height = max(
            100,
            app_height - TITLE_BAR_HEIGHT - (WINDOW_BORDER_WIDTH * 2) - ROBLOX_BOX_BOTTOM_TRIM,
        )

        roblox_x = roblox_box_x - ROBLOX_FRAME_LEFT_HIDE
        roblox_y = roblox_box_y - ROBLOX_TITLEBAR_HIDE
        roblox_width = roblox_box_width + ROBLOX_FRAME_LEFT_HIDE + ROBLOX_FRAME_RIGHT_HIDE
        roblox_height = roblox_box_height + ROBLOX_TITLEBAR_HIDE
        

        hwnd = _get_roblox_hwnd(app_hwnd)
        if not hwnd:
            emit_log("Roblox window not found", "warning")
            time.sleep(10)
            return False
            
        if hwnd and win32gui.IsWindowVisible(hwnd):
            restore_roblox_window(hwnd)
            win32gui.MoveWindow(hwnd, roblox_x, roblox_y, roblox_width, roblox_height, True)
            if not roblox_focused:
                try:
                    win32gui.SetForegroundWindow(hwnd)
                    roblox_focused = True
                except Exception:
                    pass
            return True
    except Exception as e:
        emit_log(f"Error moving Roblox: {str(e)}", "error")
    
    roblox_focused = False
    return False

def poll_roblox_loop():
    last_state = None
    poll_event = threading.Event()
    while True:
        found = move_roblox()
        if found != last_state and window:
            window.evaluate_js(
                f"window.onRobloxStatus && window.onRobloxStatus({str(found).lower()})"
            )
            last_state = found
        poll_event.wait(timeout=0.05)

# -- Log helper ----------------------------------------------------------------
def emit_log(msg, tag="info"):
    if window:
        safe = msg.replace("\\", "\\\\").replace("`", "\\`").replace("'", "\\'")
        window.evaluate_js(f"window.appendLog && window.appendLog(`{safe}`, '{tag}')")

# Initialize Autobuy logger
if AUTOBUY_OK:
    try:
        Autobuy.set_logger(emit_log)
    except Exception:
        pass

# -- API ---------------------------------------------------------
class MacroAPI:
    def get_config(self):
        return json.dumps(cfg)

    def save_config(self, payload):
        global cfg
        data = json.loads(payload)
        cfg.update(data)
        save_config(cfg)
        register_hotkeys()  
        emit_log("Settings saved.", "info")
        return "ok"

    def start(self):
        global macro_running
        with _start_stop_lock:
            if macro_running:
                return
            macro_running = True
        
        if AUTOBUY_OK:
            try:
                Autobuy.set_macro_running(True)
            except Exception:
                pass
        
        app_hwnd = _get_app_hwnd()
        roblox_hwnd = _get_roblox_hwnd(app_hwnd)
        
        if roblox_hwnd and WIN32_OK:
            try:
                restore_roblox_window(roblox_hwnd)
                win32gui.SetForegroundWindow(roblox_hwnd)
                emit_log("Roblox window activated.", "info")
                
                time.sleep(0.5)
            except Exception as e:
                emit_log(f"Warning: Could not activate Roblox: {str(e)}", "warning")
        else:
            emit_log("Roblox window not found - autobuys may not work.", "warning")
        
        self._start_autobuys()
        emit_log("Macro started.", "success")

    def stop(self):
        global macro_running
        macro_running = False
        
        if AUTOBUY_OK:
            try:
                Autobuy.set_macro_running(False)
            except Exception:
                pass
        
        if AUTOBUY_OK:
            try:
                Autobuy.stop_all_autobuys()
            except Exception as e:
                emit_log(f"Error stopping autobuys: {str(e)}", "warning")
        emit_log("Macro stopped.", "warning")

    def exit(self):
        emit_log("Shutting down...", "info")
        stop_hotkeys()
        if window:
            window.destroy()

    def rebind(self, action, key):
        cfg["hotkeys"][action] = key.lower()
        save_config(cfg)
        register_hotkeys()
        emit_log(f"{action} rebound -> {key.upper()}", "info")

    def set_theme(self, theme):
        cfg["theme"] = theme
        save_config(cfg)
        emit_log(f"Theme: {theme}", "success")

    def get_toggle_state(self, category, item):
        if category not in cfg:
            cfg[category] = {}
        return cfg[category].get(item, False)

    def _start_autobuys(self):
        if not AUTOBUY_OK:
            return
        
        try:
            active_mode = cfg.get("mode", "seeds")
            mode_items = cfg.get(active_mode, {})
            
            for item_name, is_active in mode_items.items():
                if is_active:
                    Autobuy.toggle_autobuy(active_mode, item_name, True)
        except Exception as e:
            emit_log(f"Error starting autobuys: {str(e)}", "warning")

    def set_mode(self, mode):
        global _active_mode
        
        if mode not in ("seeds", "gears"):
            emit_log(f"Invalid mode: {mode}", "error")
            return "error"
        
        old_mode = cfg.get("mode", "seeds")
        
        if old_mode != mode and AUTOBUY_OK:
            try:
                Autobuy.stop_all_autobuys()
                emit_log(f"Stopped {old_mode} autobuys.", "info")
            except Exception as e:
                emit_log(f"Error stopping old mode: {str(e)}", "warning")
        
        cfg["mode"] = mode
        _active_mode = mode
        save_config(cfg)
        emit_log(f"Mode switched to: {mode.upper()}", "success")

        return "ok"
        

    def set_toggle_state(self, category, item, is_active):
        if category not in cfg:
            cfg[category] = {}
        cfg[category][item] = bool(is_active)
        save_config(cfg)
        
        state_str = "enabled" if is_active else "disabled"
        emit_log(f"{item} {state_str}.", "info")

        return "ok"

    def get_status(self):
        return json.dumps({
            "win32":   WIN32_OK,
            "hotkeys": KB_OK,
            "config":  cfg
        })

    def clear_log(self):
        if window:
            window.evaluate_js("window.clearLog && window.clearLog()")

    def get_interval(self):
        return cfg.get("interval", 60)

    def set_interval(self, interval_secs):
        interval = max(60, min(300, int(interval_secs)))
        cfg["interval"] = interval
        save_config(cfg)
        return str(interval)

    def sync_roblox(self):
        move_roblox()


# -- Hotkey action targets -----------------------------------------------------
global _api
_api = None   # set after MacroAPI is instantiated

def api_start(): _api and _api.start()
def api_stop():  _api and _api.stop()
def api_exit():  _api and _api.exit()

# -- Entry point ---------------------------------------------------------------
if __name__ == "__main__":
    _api = MacroAPI()

    window = webview.create_window(
        title=APP_WINDOW_TITLE,
        url=f"file://{GUI_PATH}",
        width=1100,
        height=700,
        frameless=True,
        easy_drag=True,
        js_api=_api,
    )

    def on_loaded():
        apply_window_cutout()
        threading.Thread(target=poll_roblox_loop, daemon=True).start()
        if KB_OK:
            register_hotkeys()
            emit_log("Global hotkeys active.", "success")
        else:
            emit_log("pynput not installed - pip install pynput", "error")

    window.events.loaded += on_loaded
    webview.start(debug=False)
