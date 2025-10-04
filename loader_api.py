import os
import sys
import json
import time
import random
import uuid
import base64
import hashlib
import threading
import ctypes
import socket
import shutil
import platform
import requests
import psutil
import subprocess
from datetime import datetime
from PyQt5.QtWidgets import (
    QMessageBox, QFileDialog, QPushButton,
    QWidget, QVBoxLayout, QLabel, QTabWidget, QInputDialog
)

try:
    import GPUtil
except ImportError:
    GPUtil = None

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    Observer = None

try:
    import websocket
except ImportError:
    websocket = None


# 启动器实例（main.py 会注入）
launcher = None


# ======================================================
# 1. 日志 / 控制台
# ======================================================
_log_level = 1
_log_subscribers = []


def _do_log(level: str, msg: str):
    text = f"[{datetime.now().isoformat()}] [{level}] {msg}"
    if launcher:
        launcher.log(level, text)
    else:
        print(text)
    for cb in _log_subscribers:
        try:
            cb(text.encode())
        except Exception:
            pass


def api_sysc_out_info(msg: bytes): _do_log("INFO", msg.decode())
def api_sysc_out_log(msg: bytes): _do_log("LOG", msg.decode())
def api_sysc_out_warn(msg: bytes): _do_log("WARN", msg.decode())
def api_sysc_out_error(msg: bytes): _do_log("ERROR", msg.decode())
def api_sysc_out_debug(msg: bytes): _do_log("DEBUG", msg.decode())


def api_sysc_out_printf(fmt: bytes, *args):
    try:
        _do_log("PRINTF", fmt.decode() % args)
    except Exception:
        _do_log("PRINTF", fmt.decode())


def api_sysc_out_clear():
    if launcher:
        launcher.log_panel.clear()


def api_sysc_out_set_level(level: int):
    global _log_level
    _log_level = level
    _do_log("SYSTEM", f"日志等级设置为 {level}")


def api_sysc_out_export(path: bytes):
    p = path.decode()
    if launcher:
        with open(p, "w", encoding="utf-8") as f:
            f.write(launcher.log_panel.toPlainText())
    _do_log("SYSTEM", f"日志导出到 {p}")


def api_sysc_out_subscribe(handler):
    _log_subscribers.append(handler)
    _do_log("SYSTEM", "日志订阅成功")


# ======================================================
# 2. 存储 Storage
# ======================================================
_storage_file = "storage.json"
_storage = {}
_storage_watchers = {}

if os.path.exists(_storage_file):
    try:
        _storage = json.load(open(_storage_file, "r", encoding="utf-8"))
    except Exception:
        _storage = {}


def _save_storage():
    with open(_storage_file, "w", encoding="utf-8") as f:
        json.dump(_storage, f, ensure_ascii=False, indent=2)


def api_storage_set(ns, key, value):
    ns, key, value = ns.decode(), key.decode(), value.decode()
    _storage.setdefault(ns, {})[key] = value
    _save_storage()
    if (ns, key) in _storage_watchers:
        _storage_watchers[(ns, key)](value.encode())


def api_storage_get(ns, key):
    return _storage.get(ns.decode(), {}).get(key.decode(), "").encode()


def api_storage_remove(ns, key):
    if ns.decode() in _storage and key.decode() in _storage[ns.decode()]:
        _storage[ns.decode()].pop(key.decode(), None)
        _save_storage()


def api_storage_keys(ns, count):
    ks = list(_storage.get(ns.decode(), {}).keys())
    count[0] = len(ks)
    arr = (ctypes.c_char_p * len(ks))()
    for i, k in enumerate(ks):
        arr[i] = k.encode()
    return arr


def api_storage_clear(ns):
    _storage[ns.decode()] = {}
    _save_storage()


def api_storage_save(ns): _save_storage()


def api_storage_load(ns):
    global _storage
    if os.path.exists(_storage_file):
        _storage = json.load(open(_storage_file, "r", encoding="utf-8"))


def api_storage_contains(ns, key): return int(key.decode() in _storage.get(ns.decode(), {}))
def api_storage_size(ns): return len(_storage.get(ns.decode(), {}))
def api_storage_watch(ns, key, handler): _storage_watchers[(ns.decode(), key.decode())] = handler


# ======================================================
# 3. 调度 Scheduler
# ======================================================
_tasks = {}
_task_status = {}


def _wrap_task(name, func, repeat=False, interval_ms=0):
    def runner():
        if _task_status.get(name, (1, 0, 0))[0] == 1:
            try:
                func()
            except Exception as e:
                print(f"[SCHED ERROR] {e}")
            if repeat:
                t = threading.Timer(interval_ms / 1000, runner)
                _tasks[name] = t
                t.start()
    return runner


def api_scheduler_schedule(name, func):
    n = name.decode()
    t = threading.Timer(0, _wrap_task(n, func))
    _tasks[n] = t
    _task_status[n] = (1, 0, 0)
    t.start()


def api_scheduler_schedule_delay(name, delay_ms, func):
    n = name.decode()
    t = threading.Timer(delay_ms / 1000, _wrap_task(n, func))
    _tasks[n] = t
    _task_status[n] = (1, 0, 0)
    t.start()


def api_scheduler_schedule_repeat(name, interval_ms, func):
    n = name.decode()
    runner = _wrap_task(n, func, True, interval_ms)
    t = threading.Timer(interval_ms / 1000, runner)
    _tasks[n] = t
    _task_status[n] = (1, 0, 0)
    t.start()


def api_scheduler_cancel(name):
    n = name.decode()
    if n in _tasks:
        _tasks[n].cancel()
        del _tasks[n]
        _task_status[n] = (0, 0, 0)


def api_scheduler_cancel_all():
    for n, t in list(_tasks.items()):
        t.cancel()
    _tasks.clear()
    _task_status.clear()


def api_scheduler_is_running(name): return int(_task_status.get(name.decode(), (0, 0, 0))[0] == 1)


def api_scheduler_list_tasks(count_ptr):
    names = list(_tasks.keys())
    count_ptr[0] = len(names)
    arr = (ctypes.c_char_p * len(names))()
    for i, k in enumerate(names):
        arr[i] = k.encode()
    return arr


def api_scheduler_pause(name):
    n = name.decode()
    if n in _task_status:
        running, paused, pri = _task_status[n]
        _task_status[n] = (0, 1, pri)


def api_scheduler_resume(name):
    n = name.decode()
    if n in _task_status:
        _, paused, pri = _task_status[n]
        _task_status[n] = (1, 0, pri)


def api_scheduler_set_priority(name, func, level: int):
    n = name.decode()
    if n in _task_status:
        running, paused, _ = _task_status[n]
        _task_status[n] = (running, paused, level)


# ======================================================
# 4. 系统信息
# ======================================================
def api_system_os_name(): return platform.system().encode()
def api_system_arch(): return platform.machine().encode()
def api_system_jvm_version(): return b"SpectrumJVM-1.0"
def api_system_python_version(): return platform.python_version().encode()
def api_system_memory_usage(): return psutil.virtual_memory().used
def api_system_cpu_count(): return psutil.cpu_count(logical=True)


def api_system_disk_usage(path: bytes):
    try:
        usage = psutil.disk_usage(path.decode())
        data = {
            "total": usage.total,
            "used": usage.used,
            "free": usage.free,
            "percent": usage.percent
        }
        return str(data).encode()
    except Exception:
        return b"{}"


def api_system_uptime(): return int(datetime.now().timestamp() - psutil.boot_time())


def api_system_process_list(count_ptr):
    procs = [p.info["name"] for p in psutil.process_iter(["name"]) if p.info["name"]]
    count_ptr[0] = len(procs)
    arr = (ctypes.c_char_p * len(procs))()
    for i, n in enumerate(procs):
        arr[i] = n.encode()
    return arr


def api_system_gpu_info():
    if GPUtil:
        try:
            gpus = GPUtil.getGPUs()
            info = []
            for g in gpus:
                info.append({
                    "id": g.id,
                    "name": g.name,
                    "load": f"{g.load * 100:.1f}%",
                    "mem_free": f"{g.memoryFree}MB",
                    "mem_used": f"{g.memoryUsed}MB",
                    "driver": g.driver
                })
            return str(info).encode()
        except Exception:
            return b"[]"
    return b"GPU info unavailable"
# ======================================================
# 5. 版本管理
# ======================================================
_versions_file = "versions.json"
_versions = {"installed": ["1.20.1", "1.19.4"], "default": "1.20.1"}

if os.path.exists(_versions_file):
    try:
        with open(_versions_file, "r", encoding="utf-8") as f:
            _versions = json.load(f)
    except Exception:
        pass


def _save_versions():
    with open(_versions_file, "w", encoding="utf-8") as f:
        json.dump(_versions, f, ensure_ascii=False, indent=2)


def api_versions_all(count_ptr):
    all_versions = ["1.20.1", "1.19.4", "1.18.2", "1.16.5"]
    count_ptr[0] = len(all_versions)
    arr = (ctypes.c_char_p * len(all_versions))()
    for i, v in enumerate(all_versions):
        arr[i] = v.encode()
    return arr


def api_versions_latest(): return b"1.20.1"


def api_versions_filter(pred, count_ptr):
    all_versions = ["1.20.1", "1.19.4", "1.18.2", "1.16.5"]
    filtered = [v for v in all_versions if pred(v.encode())]
    count_ptr[0] = len(filtered)
    arr = (ctypes.c_char_p * len(filtered))()
    for i, v in enumerate(filtered):
        arr[i] = v.encode()
    return arr


def api_versions_for_each(consumer):
    for v in _versions["installed"]:
        consumer(v.encode())


def api_versions_installed(count_ptr):
    installed = _versions["installed"]
    count_ptr[0] = len(installed)
    arr = (ctypes.c_char_p * len(installed))()
    for i, v in enumerate(installed):
        arr[i] = v.encode()
    return arr


def api_versions_download(version: bytes):
    v = version.decode()
    if v not in _versions["installed"]:
        _versions["installed"].append(v)
        _save_versions()
    return 1


def api_versions_remove(version: bytes):
    v = version.decode()
    if v in _versions["installed"]:
        _versions["installed"].remove(v)
        if _versions["default"] == v:
            _versions["default"] = _versions["installed"][0] if _versions["installed"] else ""
        _save_versions()
    return 1


def api_versions_is_installed(version: bytes): return int(version.decode() in _versions["installed"])
def api_versions_size(version: bytes): return 123456789
def api_versions_set_default(version: bytes):
    v = version.decode()
    if v in _versions["installed"]:
        _versions["default"] = v
        _save_versions()


# ======================================================
# 6. 网络
# ======================================================
def api_net_http_get(url: bytes):
    try:
        r = requests.get(url.decode())
        return r.text.encode()
    except Exception as e:
        return str(e).encode()


def api_net_http_post(url: bytes, body: bytes):
    try:
        r = requests.post(url.decode(), data=body.decode())
        return r.text.encode()
    except Exception as e:
        return str(e).encode()


def api_net_download(url: bytes, path: bytes):
    try:
        u, p = url.decode(), path.decode()
        r = requests.get(u, stream=True)
        with open(p, "wb") as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
        return 1
    except Exception:
        return 0


def api_net_ping(host: bytes):
    h = host.decode()
    try:
        if platform.system().lower() == "windows":
            output = subprocess.check_output(["ping", "-n", "1", h], stderr=subprocess.STDOUT, universal_newlines=True)
        else:
            output = subprocess.check_output(["ping", "-c", "1", h], stderr=subprocess.STDOUT, universal_newlines=True)
        for line in output.splitlines():
            if "时间=" in line or "time=" in line:
                return int("".join([c for c in line if c.isdigit()]))
    except Exception:
        return -1
    return -1


def api_net_websocket(url: bytes, on_message):
    if not websocket: return
    def run():
        ws = websocket.WebSocketApp(url.decode(), on_message=lambda ws, msg: on_message(msg.encode()))
        ws.run_forever()
    threading.Thread(target=run, daemon=True).start()


def api_net_http_put(url: bytes, body: bytes):
    try:
        r = requests.put(url.decode(), data=body.decode())
        return r.text.encode()
    except Exception as e:
        return str(e).encode()


def api_net_http_delete(url: bytes):
    try:
        r = requests.delete(url.decode())
        return r.text.encode()
    except Exception as e:
        return str(e).encode()


def api_net_dns_lookup(host: bytes):
    try:
        return socket.gethostbyname(host.decode()).encode()
    except Exception:
        return b""


def api_net_speed_test():
    try:
        url = "http://speedtest.tele2.net/1MB.zip"
        start = time.time()
        r = requests.get(url, stream=True)
        total = 0
        for chunk in r.iter_content(1024):
            total += len(chunk)
            if total >= 1024 * 1024:
                break
        elapsed = time.time() - start
        return int(total / 1024 / elapsed)
    except Exception:
        return -1


def api_net_open_browser(url: bytes):
    try:
        import webbrowser
        webbrowser.open(url.decode())
        return 1
    except Exception:
        return 0


# ======================================================
# 7. 文件系统
# ======================================================
_fs_watchers = {}


def api_fs_read(path: bytes):
    try:
        with open(path.decode(), "r", encoding="utf-8") as f:
            return f.read().encode()
    except Exception:
        return b""


def api_fs_write(path: bytes, content: bytes):
    try:
        with open(path.decode(), "w", encoding="utf-8") as f:
            f.write(content.decode())
        return 1
    except Exception:
        return 0


def api_fs_exists(path: bytes): return int(os.path.exists(path.decode()))
def api_fs_delete(path: bytes):
    try:
        os.remove(path.decode()); return 1
    except Exception:
        return 0


def api_fs_mkdirs(path: bytes):
    try: os.makedirs(path.decode(), exist_ok=True); return 1
    except Exception: return 0


def api_fs_copy(src: bytes, dst: bytes):
    try: shutil.copy(src.decode(), dst.decode()); return 1
    except Exception: return 0


def api_fs_move(src: bytes, dst: bytes):
    try: shutil.move(src.decode(), dst.decode()); return 1
    except Exception: return 0


def api_fs_size(path: bytes):
    try: return os.path.getsize(path.decode())
    except Exception: return -1


def api_fs_list_dir(path: bytes, count_ptr):
    try:
        files = os.listdir(path.decode())
        count_ptr[0] = len(files)
        arr = (ctypes.c_char_p * len(files))()
        for i, f in enumerate(files):
            arr[i] = f.encode()
        return arr
    except Exception:
        count_ptr[0] = 0
        return (ctypes.c_char_p * 0)()


def api_fs_watch(path: bytes, handler):
    if not Observer: return
    p = path.decode()
    class WatchHandler(FileSystemEventHandler):
        def on_modified(self, event): handler(event.src_path.encode())
        def on_created(self, event): handler(event.src_path.encode())
        def on_deleted(self, event): handler(event.src_path.encode())
    observer = Observer()
    observer.schedule(WatchHandler(), p, recursive=True)
    observer.start()
    _fs_watchers[p] = observer


# ======================================================
# 8. 事件系统
# ======================================================
_events = {}
def _sort_handlers(event): _events[event].sort(key=lambda x: -x[0])


def api_events_register(event: bytes, handler):
    e = event.decode(); _events.setdefault(e, []).append((0, handler)); _sort_handlers(e)


def api_events_unregister(event: bytes, handler):
    e = event.decode()
    if e in _events:
        _events[e] = [(pri, h) for pri, h in _events[e] if h != handler]


def api_events_fire(event: bytes, data: bytes):
    e, d = event.decode(), data.decode()
    if e in _events:
        for _, h in _events[e]:
            try: h(d.encode())
            except Exception as ex: print(f"[EVENT ERROR] {ex}")


def api_events_list(count_ptr):
    events = list(_events.keys())
    count_ptr[0] = len(events)
    arr = (ctypes.c_char_p * len(events))()
    for i, ev in enumerate(events): arr[i] = ev.encode()
    return arr


def api_events_has(event: bytes): return int(event.decode() in _events and len(_events[event.decode()]) > 0)
def api_events_clear_all(): _events.clear()


def api_events_once(event: bytes, handler):
    e = event.decode()
    def wrapper(data: bytes): handler(data); api_events_unregister(event, wrapper)
    _events.setdefault(e, []).append((0, wrapper)); _sort_handlers(e)


def api_events_priority(event: bytes, handler, level: int):
    e = event.decode(); _events.setdefault(e, []).append((level, handler)); _sort_handlers(e)


def api_events_cancel(event: bytes, handler): api_events_unregister(event, handler)
def api_events_emit_async(event: bytes, data: bytes): threading.Thread(target=api_events_fire, args=(event, data), daemon=True).start()


# ======================================================
# 9. 玩家系统
# ======================================================
_players = {}; _banlist = set()


def api_player_login(username: bytes, password: bytes):
    u = username.decode()
    if u in _banlist: return 0
    _players[u] = {"online": True, "banned": False}; print(f"[PLAYER] {u} 登录成功 ✅"); return 1


def api_player_logout(username: bytes):
    u = username.decode()
    if u in _players: _players[u]["online"] = False; print(f"[PLAYER] {u} 已登出 ❌"); return 1
    return 0


def api_player_list(count_ptr):
    names = list(_players.keys()); count_ptr[0] = len(names)
    arr = (ctypes.c_char_p * len(names))()
    for i, n in enumerate(names): arr[i] = n.encode()
    return arr


def api_player_get(username: bytes): return str(_players.get(username.decode(), {})).encode()
def api_player_is_online(username: bytes): return int(username.decode() in _players and _players[username.decode()]["online"])
def api_player_ban(username: bytes):
    u = username.decode(); _banlist.add(u)
    if u in _players: _players[u]["banned"] = True; _players[u]["online"] = False
    print(f"[PLAYER] {u} 已封禁 🚫"); return 1


def api_player_unban(username: bytes):
    u = username.decode()
    if u in _banlist: _banlist.remove(u)
    if u in _players: _players[u]["banned"] = False
    print(f"[PLAYER] {u} 已解封 ✅"); return 1


def api_player_kick(username: bytes, reason: bytes):
    u, r = username.decode(), reason.decode()
    if u in _players and _players[u]["online"]: _players[u]["online"] = False; print(f"[PLAYER] {u} 被踢出，原因: {r}")


def api_player_send_message(username: bytes, msg: bytes):
    u, m = username.decode(), msg.decode()
    if u in _players and _players[u]["online"]: print(f"[CHAT] 给 {u}: {m}")


def api_player_broadcast(msg: bytes):
    m = msg.decode()
    for u, info in _players.items():
        if info["online"]: print(f"[BROADCAST] {u} <- {m}")


# ======================================================
# 10. 启动器 UI
# ======================================================
def api_ui_show_message(msg: bytes): QMessageBox.information(launcher, "提示", msg.decode())
def api_ui_show_error(msg: bytes): QMessageBox.critical(launcher, "错误", msg.decode())
def api_ui_confirm(msg: bytes): return 1 if QMessageBox.question(launcher, "确认", msg.decode()) == QMessageBox.Yes else 0
def api_ui_input(prompt: bytes):
    text, ok = QInputDialog.getText(launcher, "输入", prompt.decode()); return text.encode() if ok else b""


def api_ui_add_button(label: bytes, func):
    btn = QPushButton(label.decode(), launcher); btn.clicked.connect(lambda: func()); launcher.centralWidget().layout().addWidget(btn)


def api_ui_add_tab(name: bytes):
    if not hasattr(launcher, "tabs"):
        launcher.tabs = QTabWidget(); launcher.centralWidget().layout().addWidget(launcher.tabs)
    tab = QWidget(); tab.setLayout(QVBoxLayout()); launcher.tabs.addTab(tab, name.decode()); return tab


def api_ui_add_panel(name: bytes):
    panel = QWidget(); panel.setLayout(QVBoxLayout()); panel.layout().addWidget(QLabel(name.decode()))
    launcher.centralWidget().layout().addWidget(panel); return panel


def api_ui_notify(title: bytes, msg: bytes): QMessageBox.information(launcher, title.decode(), msg.decode())
def api_ui_open_file_dialog(): fname, _ = QFileDialog.getOpenFileName(launcher, "选择文件"); return fname.encode() if fname else b""
def api_ui_open_folder_dialog(): folder = QFileDialog.getExistingDirectory(launcher, "选择文件夹"); return folder.encode() if folder else b""


# ======================================================
# 11. Utils 工具
# ======================================================
def api_util_random_int(min_: int, max_: int):
    return random.randint(min_, max_)

def api_util_random_uuid():
    return str(uuid.uuid4()).encode()

def api_util_sha256(data: bytes):
    return hashlib.sha256(data).hexdigest().encode()

def api_util_base64_encode(data: bytes):
    return base64.b64encode(data)

def api_util_base64_decode(data: bytes):
    try:
        return base64.b64decode(data)
    except Exception:
        return b""

def api_util_timestamp():
    return int(time.time())

def api_util_now_iso():
    return time.strftime("%Y-%m-%dT%H:%M:%S").encode()

def api_util_sleep(ms: int):
    time.sleep(ms / 1000)

def api_util_thread(func):
    threading.Thread(target=func, daemon=True).start()

def api_util_benchmark(func):
    s = time.time()
    func()
    return int((time.time() - s) * 1000)
def bind_all(lib):
    """
    把 DLL 里的导出函数绑定到 Python 的 api_map
    """
    for name, func in api_map.items():
        try:
            setattr(lib, name, func)
        except Exception as e:
            print(f"[bind_all] 跳过 {name}: {e}")