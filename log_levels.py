# log_levels.py

_LEVELS = {"DEBUG": 10, "INFO": 20, "ERROR": 30}
DEBUG_LEVEL = "DEBUG"   # 預設等級，可在程式裡動態改

def _log(level: str, msg: str, *args, **kwargs):
    if _LEVELS[level] >= _LEVELS.get(DEBUG_LEVEL, 0):
        try:
            msg = msg.format(*args, **kwargs)
        except Exception:
            pass
        print(f"[{level}] {msg}")

def DEBUG(msg: str, *args, **kwargs):
    _log("DEBUG", msg, *args, **kwargs)
def INFO(msg: str, *args, **kwargs):
    _log("INFO", msg, *args, **kwargs)
def ERROR(msg: str, *args, **kwargs):
    _log("ERROR", msg, *args, **kwargs)
