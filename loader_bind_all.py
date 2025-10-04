import ctypes
import loader_api

# 保持 CFUNCTYPE 包装后的回调引用，防止被 Python GC 回收
_injected_cfuncs = {}

def inject_all_api(dll):
    """
    把 loader_api 中实现的 Python 函数按 loader_bind_all.api_signatures 注入到 dll 中。
    要求：dll 有导出函数 `inject_api(const char* name, void* func)`。
    调用时请保证：在 create_plugin() 之前调用 inject_all_api(dll)。
    """
    # 验证 dll.inject_api 存在
    if not hasattr(dll, "inject_api"):
        raise RuntimeError("目标 DLL 没有导出 inject_api，请确认已在 C SDK 中添加并编译。")

    # 设置签名
    try:
        dll.inject_api.argtypes = [ctypes.c_char_p, ctypes.c_void_p]
        dll.inject_api.restype = None
    except Exception as e:
        raise RuntimeError(f"设置 inject_api 签名失败: {e}")

    bound = 0
    for name, cf_type in api_signatures.items():
        # 仅注入 loader_api 有实现的函数
        py_impl = getattr(loader_api, name, None)
        if py_impl is None:
            # loader_api 没实现这个 API，跳过
            continue

        try:
            # 把 Python 实现包装成 C 回调
            cfunc = cf_type(py_impl)
        except Exception as e:
            print(f"[inject_all_api] wrap failed for {name}: {e}")
            continue

        # 保活引用，防止 GC；并记录原始 python 实现（便于调试）
        _injected_cfuncs[name] = (cfunc, py_impl)

        # 注入到 dll（将函数指针传给 inject_api）
        try:
            dll.inject_api(name.encode("utf-8"), ctypes.cast(cfunc, ctypes.c_void_p))
            bound += 1
        except Exception as e:
            print(f"[inject_all_api] inject failed for {name}: {e}")

    print(f"[inject_all_api] 注入完成：共注入 {bound} 个 API（loader_api 中有实现的项）")

# 常用类型别名
c_str = ctypes.c_char_p
c_int = ctypes.c_int
c_int_p = ctypes.POINTER(c_int)
c_long = ctypes.c_long
c_void_p = ctypes.c_void_p

# ======================================================
# API 签名（和 spectrum_sdk.h 一一对应）
# 注意：凡是返回 const char** 的，都用 c_void_p
# ======================================================

api_signatures = {
    # 日志系统
    "api_sysc_out_info": ctypes.CFUNCTYPE(None, c_str),
    "api_sysc_out_log": ctypes.CFUNCTYPE(None, c_str),
    "api_sysc_out_warn": ctypes.CFUNCTYPE(None, c_str),
    "api_sysc_out_error": ctypes.CFUNCTYPE(None, c_str),
    "api_sysc_out_debug": ctypes.CFUNCTYPE(None, c_str),
    "api_sysc_out_printf": ctypes.CFUNCTYPE(None, c_str),  # 变参简化
    "api_sysc_out_clear": ctypes.CFUNCTYPE(None),
    "api_sysc_out_set_level": ctypes.CFUNCTYPE(None, c_int),
    "api_sysc_out_export": ctypes.CFUNCTYPE(None, c_str),
    "api_sysc_out_subscribe": ctypes.CFUNCTYPE(None, c_void_p),

    # Storage
    "api_storage_set": ctypes.CFUNCTYPE(None, c_str, c_str, c_str),
    "api_storage_get": ctypes.CFUNCTYPE(c_str, c_str, c_str),
    "api_storage_remove": ctypes.CFUNCTYPE(None, c_str, c_str),
    "api_storage_keys": ctypes.CFUNCTYPE(c_void_p, c_str, c_int_p),
    "api_storage_clear": ctypes.CFUNCTYPE(None, c_str),
    "api_storage_save": ctypes.CFUNCTYPE(None, c_str),
    "api_storage_load": ctypes.CFUNCTYPE(None, c_str),
    "api_storage_contains": ctypes.CFUNCTYPE(c_int, c_str, c_str),
    "api_storage_size": ctypes.CFUNCTYPE(c_int, c_str),
    "api_storage_watch": ctypes.CFUNCTYPE(None, c_str, c_str, c_void_p),

    # Scheduler
    "api_scheduler_schedule": ctypes.CFUNCTYPE(None, c_str, c_void_p),
    "api_scheduler_schedule_delay": ctypes.CFUNCTYPE(None, c_str, c_int, c_void_p),
    "api_scheduler_schedule_repeat": ctypes.CFUNCTYPE(None, c_str, c_int, c_void_p),
    "api_scheduler_cancel": ctypes.CFUNCTYPE(None, c_str),
    "api_scheduler_cancel_all": ctypes.CFUNCTYPE(None),
    "api_scheduler_is_running": ctypes.CFUNCTYPE(c_int, c_str),
    "api_scheduler_list_tasks": ctypes.CFUNCTYPE(c_void_p, c_int_p),
    "api_scheduler_pause": ctypes.CFUNCTYPE(None, c_str),
    "api_scheduler_resume": ctypes.CFUNCTYPE(None, c_str),
    "api_scheduler_set_priority": ctypes.CFUNCTYPE(None, c_str, c_void_p, c_int),

    # System
    "api_system_os_name": ctypes.CFUNCTYPE(c_str),
    "api_system_arch": ctypes.CFUNCTYPE(c_str),
    "api_system_jvm_version": ctypes.CFUNCTYPE(c_str),
    "api_system_python_version": ctypes.CFUNCTYPE(c_str),
    "api_system_memory_usage": ctypes.CFUNCTYPE(c_long),
    "api_system_cpu_count": ctypes.CFUNCTYPE(c_int),
    "api_system_disk_usage": ctypes.CFUNCTYPE(c_str, c_str),
    "api_system_uptime": ctypes.CFUNCTYPE(c_int),
    "api_system_process_list": ctypes.CFUNCTYPE(c_void_p, c_int_p),
    "api_system_gpu_info": ctypes.CFUNCTYPE(c_str),

    # Versions
    "api_versions_all": ctypes.CFUNCTYPE(c_void_p, c_int_p),
    "api_versions_latest": ctypes.CFUNCTYPE(c_str),
    "api_versions_filter": ctypes.CFUNCTYPE(c_void_p, c_void_p, c_int_p),
    "api_versions_for_each": ctypes.CFUNCTYPE(None, c_void_p),
    "api_versions_installed": ctypes.CFUNCTYPE(c_void_p, c_int_p),
    "api_versions_download": ctypes.CFUNCTYPE(c_int, c_str),
    "api_versions_remove": ctypes.CFUNCTYPE(c_int, c_str),
    "api_versions_is_installed": ctypes.CFUNCTYPE(c_int, c_str),
    "api_versions_size": ctypes.CFUNCTYPE(c_long, c_str),
    "api_versions_set_default": ctypes.CFUNCTYPE(None, c_str),

    # File system
    "api_fs_read": ctypes.CFUNCTYPE(c_str, c_str),
    "api_fs_write": ctypes.CFUNCTYPE(c_int, c_str, c_str),
    "api_fs_exists": ctypes.CFUNCTYPE(c_int, c_str),
    "api_fs_delete": ctypes.CFUNCTYPE(c_int, c_str),
    "api_fs_mkdirs": ctypes.CFUNCTYPE(c_int, c_str),
    "api_fs_copy": ctypes.CFUNCTYPE(c_int, c_str, c_str),
    "api_fs_move": ctypes.CFUNCTYPE(c_int, c_str, c_str),
    "api_fs_size": ctypes.CFUNCTYPE(c_long, c_str),
    "api_fs_list_dir": ctypes.CFUNCTYPE(c_void_p, c_str, c_int_p),
    "api_fs_watch": ctypes.CFUNCTYPE(None, c_str, c_void_p),

    # Events
    "api_events_register": ctypes.CFUNCTYPE(None, c_str, c_void_p),
    "api_events_unregister": ctypes.CFUNCTYPE(None, c_str, c_void_p),
    "api_events_fire": ctypes.CFUNCTYPE(None, c_str, c_str),
    "api_events_list": ctypes.CFUNCTYPE(c_void_p, c_int_p),
    "api_events_has": ctypes.CFUNCTYPE(c_int, c_str),
    "api_events_clear_all": ctypes.CFUNCTYPE(None),
    "api_events_once": ctypes.CFUNCTYPE(None, c_str, c_void_p),
    "api_events_priority": ctypes.CFUNCTYPE(None, c_str, c_void_p, c_int),
    "api_events_cancel": ctypes.CFUNCTYPE(None, c_str, c_void_p),
    "api_events_emit_async": ctypes.CFUNCTYPE(None, c_str, c_str),

    # Player
    "api_player_login": ctypes.CFUNCTYPE(c_int, c_str, c_str),
    "api_player_logout": ctypes.CFUNCTYPE(c_int, c_str),
    "api_player_list": ctypes.CFUNCTYPE(c_void_p, c_int_p),
    "api_player_get": ctypes.CFUNCTYPE(c_str, c_str),
    "api_player_is_online": ctypes.CFUNCTYPE(c_int, c_str),
    "api_player_ban": ctypes.CFUNCTYPE(c_int, c_str),
    "api_player_unban": ctypes.CFUNCTYPE(c_int, c_str),
    "api_player_kick": ctypes.CFUNCTYPE(None, c_str, c_str),
    "api_player_send_message": ctypes.CFUNCTYPE(None, c_str, c_str),
    "api_player_broadcast": ctypes.CFUNCTYPE(None, c_str),

    # UI
    "api_ui_show_message": ctypes.CFUNCTYPE(None, c_str),
    "api_ui_show_error": ctypes.CFUNCTYPE(None, c_str),
    "api_ui_confirm": ctypes.CFUNCTYPE(c_int, c_str),
    "api_ui_input": ctypes.CFUNCTYPE(c_str, c_str),
    "api_ui_add_button": ctypes.CFUNCTYPE(None, c_str, c_void_p),
    "api_ui_add_tab": ctypes.CFUNCTYPE(c_void_p, c_str),
    "api_ui_add_panel": ctypes.CFUNCTYPE(c_void_p, c_str),
    "api_ui_notify": ctypes.CFUNCTYPE(None, c_str, c_str),
    "api_ui_open_file_dialog": ctypes.CFUNCTYPE(c_str),
    "api_ui_open_folder_dialog": ctypes.CFUNCTYPE(c_str),

    # Utils
    "api_util_random_int": ctypes.CFUNCTYPE(c_int, c_int, c_int),
    "api_util_random_uuid": ctypes.CFUNCTYPE(c_str),
    "api_util_sha256": ctypes.CFUNCTYPE(c_str, c_str),
    "api_util_base64_encode": ctypes.CFUNCTYPE(c_str, c_str),
    "api_util_base64_decode": ctypes.CFUNCTYPE(c_str, c_str),
    "api_util_timestamp": ctypes.CFUNCTYPE(c_long),
    "api_util_now_iso": ctypes.CFUNCTYPE(c_str),
    "api_util_sleep": ctypes.CFUNCTYPE(None, c_int),
    "api_util_thread": ctypes.CFUNCTYPE(None, c_void_p),
    "api_util_benchmark": ctypes.CFUNCTYPE(c_long, c_void_p),
}

# ======================================================
# 绑定函数
# ======================================================
def bind_all(lib):
    """
    把 Python 实现函数绑定到 DLL 的函数指针
    """
    for name, cfunc in api_signatures.items():
        if hasattr(loader_api, name):
            py_func = getattr(loader_api, name)
            cb = cfunc(py_func)
            setattr(lib, name, cb)
            print(f"[bind_all] 已绑定 {name}")
        else:
            print(f"[bind_all] 跳过 {name} (Python 里没实现)")
