#ifndef SPECTRUM_SDK_H
#define SPECTRUM_SDK_H

#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT
#endif

#ifdef __cplusplus
extern "C" {
#endif

#include <stddef.h>

/* --------------------
   基本 typedefs
   -------------------- */
typedef void (*task_func)(void* userdata);
typedef int  (*predicate_func)(const char* v);
typedef void (*consumer_func)(const char* v);

/* ================================
   1. 日志 / 控制台输出
   ================================ */
typedef void (*fn_api_sysc_out_info)(const char* msg);
typedef void (*fn_api_sysc_out_log)(const char* msg);
typedef void (*fn_api_sysc_out_warn)(const char* msg);
typedef void (*fn_api_sysc_out_error)(const char* msg);
typedef void (*fn_api_sysc_out_debug)(const char* msg);
typedef void (*fn_api_sysc_out_printf)(const char* fmt, ...);
typedef void (*fn_api_sysc_out_clear)();
typedef void (*fn_api_sysc_out_set_level)(int level);
typedef void (*fn_api_sysc_out_export)(const char* path);
typedef void (*fn_api_sysc_out_subscribe)(void (*handler)(const char* msg));

extern fn_api_sysc_out_info api_sysc_out_info;
extern fn_api_sysc_out_log api_sysc_out_log;
extern fn_api_sysc_out_warn api_sysc_out_warn;
extern fn_api_sysc_out_error api_sysc_out_error;
extern fn_api_sysc_out_debug api_sysc_out_debug;
extern fn_api_sysc_out_printf api_sysc_out_printf;
extern fn_api_sysc_out_clear api_sysc_out_clear;
extern fn_api_sysc_out_set_level api_sysc_out_set_level;
extern fn_api_sysc_out_export api_sysc_out_export;
extern fn_api_sysc_out_subscribe api_sysc_out_subscribe;

/* ================================
   2. 存储 Storage
   ================================ */
typedef void (*fn_api_storage_set)(const char* ns, const char* key, const char* value);
typedef const char* (*fn_api_storage_get)(const char* ns, const char* key);
typedef void (*fn_api_storage_remove)(const char* ns, const char* key);
typedef const char** (*fn_api_storage_keys)(const char* ns, int* count);
typedef void (*fn_api_storage_clear)(const char* ns);
typedef void (*fn_api_storage_save)(const char* ns);
typedef void (*fn_api_storage_load)(const char* ns);
typedef int  (*fn_api_storage_contains)(const char* ns, const char* key);
typedef int  (*fn_api_storage_size)(const char* ns);
typedef void (*fn_api_storage_watch)(const char* ns, const char* key, void (*handler)(const char* value));

extern fn_api_storage_set api_storage_set;
extern fn_api_storage_get api_storage_get;
extern fn_api_storage_remove api_storage_remove;
extern fn_api_storage_keys api_storage_keys;
extern fn_api_storage_clear api_storage_clear;
extern fn_api_storage_save api_storage_save;
extern fn_api_storage_load api_storage_load;
extern fn_api_storage_contains api_storage_contains;
extern fn_api_storage_size api_storage_size;
extern fn_api_storage_watch api_storage_watch;

/* ================================
   3. 调度 Scheduler
   ================================ */
typedef void (*fn_task_func)(void* userdata);
typedef void (*fn_api_scheduler_schedule)(const char* name, fn_task_func func);
typedef void (*fn_api_scheduler_schedule_delay)(const char* name, int delay_ms, fn_task_func func);
typedef void (*fn_api_scheduler_schedule_repeat)(const char* name, int interval_ms, fn_task_func func);
typedef void (*fn_api_scheduler_cancel)(const char* name);
typedef void (*fn_api_scheduler_cancel_all)();
typedef int  (*fn_api_scheduler_is_running)(const char* name);
typedef const char** (*fn_api_scheduler_list_tasks)(int* count);
typedef void (*fn_api_scheduler_pause)(const char* name);
typedef void (*fn_api_scheduler_resume)(const char* name);
typedef void (*fn_api_scheduler_set_priority)(const char* name, int level);

extern fn_api_scheduler_schedule api_scheduler_schedule;
extern fn_api_scheduler_schedule_delay api_scheduler_schedule_delay;
extern fn_api_scheduler_schedule_repeat api_scheduler_schedule_repeat;
extern fn_api_scheduler_cancel api_scheduler_cancel;
extern fn_api_scheduler_cancel_all api_scheduler_cancel_all;
extern fn_api_scheduler_is_running api_scheduler_is_running;
extern fn_api_scheduler_list_tasks api_scheduler_list_tasks;
extern fn_api_scheduler_pause api_scheduler_pause;
extern fn_api_scheduler_resume api_scheduler_resume;
extern fn_api_scheduler_set_priority api_scheduler_set_priority;

/* ================================
   4. 系统信息 SystemInfo
   ================================ */
typedef const char* (*fn_api_system_os_name)();
typedef const char* (*fn_api_system_arch)();
typedef const char* (*fn_api_system_jvm_version)();
typedef const char* (*fn_api_system_python_version)();
typedef long (*fn_api_system_memory_usage)();
typedef int  (*fn_api_system_cpu_count)();
typedef const char* (*fn_api_system_disk_usage)(const char* path);
typedef long (*fn_api_system_uptime)();
typedef const char** (*fn_api_system_process_list)(int* count);
typedef const char* (*fn_api_system_gpu_info)();

extern fn_api_system_os_name api_system_os_name;
extern fn_api_system_arch api_system_arch;
extern fn_api_system_jvm_version api_system_jvm_version;
extern fn_api_system_python_version api_system_python_version;
extern fn_api_system_memory_usage api_system_memory_usage;
extern fn_api_system_cpu_count api_system_cpu_count;
extern fn_api_system_disk_usage api_system_disk_usage;
extern fn_api_system_uptime api_system_uptime;
extern fn_api_system_process_list api_system_process_list;
extern fn_api_system_gpu_info api_system_gpu_info;

/* ================================
   5. 版本管理 Versions
   ================================ */
typedef const char** (*fn_api_versions_all)(int* count);
typedef const char*  (*fn_api_versions_latest)();
typedef const char** (*fn_api_versions_filter)(predicate_func pred, int* count);
typedef void (*fn_api_versions_for_each)(consumer_func consumer);
typedef const char** (*fn_api_versions_installed)(int* count);
typedef int  (*fn_api_versions_download)(const char* version);
typedef int  (*fn_api_versions_remove)(const char* version);
typedef int  (*fn_api_versions_is_installed)(const char* version);
typedef long (*fn_api_versions_size)(const char* version);
typedef void (*fn_api_versions_set_default)(const char* version);

extern fn_api_versions_all api_versions_all;
extern fn_api_versions_latest api_versions_latest;
extern fn_api_versions_filter api_versions_filter;
extern fn_api_versions_for_each api_versions_for_each;
extern fn_api_versions_installed api_versions_installed;
extern fn_api_versions_download api_versions_download;
extern fn_api_versions_remove api_versions_remove;
extern fn_api_versions_is_installed api_versions_is_installed;
extern fn_api_versions_size api_versions_size;
extern fn_api_versions_set_default api_versions_set_default;

/* ================================
   6. 网络 Net
   ================================ */
typedef const char* (*fn_api_net_http_get)(const char* url);
typedef const char* (*fn_api_net_http_post)(const char* url, const char* body);
typedef int  (*fn_api_net_download)(const char* url, const char* path);
typedef int  (*fn_api_net_ping)(const char* host);
typedef void (*fn_api_net_websocket)(const char* url, consumer_func on_message);
typedef const char* (*fn_api_net_http_put)(const char* url, const char* body);
typedef const char* (*fn_api_net_http_delete)(const char* url);
typedef const char* (*fn_api_net_dns_lookup)(const char* host);
typedef int  (*fn_api_net_speed_test)();
typedef void (*fn_api_net_open_browser)(const char* url);

extern fn_api_net_http_get api_net_http_get;
extern fn_api_net_http_post api_net_http_post;
extern fn_api_net_download api_net_download;
extern fn_api_net_ping api_net_ping;
extern fn_api_net_websocket api_net_websocket;
extern fn_api_net_http_put api_net_http_put;
extern fn_api_net_http_delete api_net_http_delete;
extern fn_api_net_dns_lookup api_net_dns_lookup;
extern fn_api_net_speed_test api_net_speed_test;
extern fn_api_net_open_browser api_net_open_browser;

/* ================================
   7. 文件系统 FS
   ================================ */
typedef const char* (*fn_api_fs_read)(const char* path);
typedef int  (*fn_api_fs_write)(const char* path, const char* content);
typedef int  (*fn_api_fs_exists)(const char* path);
typedef int  (*fn_api_fs_delete)(const char* path);
typedef int  (*fn_api_fs_mkdirs)(const char* path);
typedef int  (*fn_api_fs_copy)(const char* src, const char* dst);
typedef int  (*fn_api_fs_move)(const char* src, const char* dst);
typedef long (*fn_api_fs_size)(const char* path);
typedef const char** (*fn_api_fs_list_dir)(const char* path, int* count);
typedef void (*fn_api_fs_watch)(const char* path, void (*handler)(const char* file));

extern fn_api_fs_read api_fs_read;
extern fn_api_fs_write api_fs_write;
extern fn_api_fs_exists api_fs_exists;
extern fn_api_fs_delete api_fs_delete;
extern fn_api_fs_mkdirs api_fs_mkdirs;
extern fn_api_fs_copy api_fs_copy;
extern fn_api_fs_move api_fs_move;
extern fn_api_fs_size api_fs_size;
extern fn_api_fs_list_dir api_fs_list_dir;
extern fn_api_fs_watch api_fs_watch;

/* ================================
   8. 事件 Events
   ================================ */
typedef void (*fn_api_events_register)(const char* event, consumer_func handler);
typedef void (*fn_api_events_unregister)(const char* event, consumer_func handler);
typedef void (*fn_api_events_fire)(const char* event, const char* data);
typedef const char** (*fn_api_events_list)(int* count);
typedef int  (*fn_api_events_has)(const char* event);
typedef void (*fn_api_events_clear_all)();
typedef void (*fn_api_events_once)(const char* event, consumer_func handler);
typedef void (*fn_api_events_priority)(const char* event, consumer_func handler, int level);
typedef void (*fn_api_events_cancel)(const char* event);
typedef void (*fn_api_events_emit_async)(const char* event, const char* data);

extern fn_api_events_register api_events_register;
extern fn_api_events_unregister api_events_unregister;
extern fn_api_events_fire api_events_fire;
extern fn_api_events_list api_events_list;
extern fn_api_events_has api_events_has;
extern fn_api_events_clear_all api_events_clear_all;
extern fn_api_events_once api_events_once;
extern fn_api_events_priority api_events_priority;
extern fn_api_events_cancel api_events_cancel;
extern fn_api_events_emit_async api_events_emit_async;

/* ================================
   9. 玩家 Player
   ================================ */
typedef int  (*fn_api_player_login)(const char* username, const char* password);
typedef int  (*fn_api_player_logout)(const char* username);
typedef const char** (*fn_api_player_list)(int* count);
typedef const char*  (*fn_api_player_get)(const char* uuid);
typedef int  (*fn_api_player_is_online)(const char* username);
typedef int  (*fn_api_player_ban)(const char* username);
typedef int  (*fn_api_player_unban)(const char* username);
typedef int  (*fn_api_player_kick)(const char* username, const char* reason);
typedef void (*fn_api_player_send_message)(const char* username, const char* msg);
typedef void (*fn_api_player_broadcast)(const char* msg);

extern fn_api_player_login api_player_login;
extern fn_api_player_logout api_player_logout;
extern fn_api_player_list api_player_list;
extern fn_api_player_get api_player_get;
extern fn_api_player_is_online api_player_is_online;
extern fn_api_player_ban api_player_ban;
extern fn_api_player_unban api_player_unban;
extern fn_api_player_kick api_player_kick;
extern fn_api_player_send_message api_player_send_message;
extern fn_api_player_broadcast api_player_broadcast;

/* ================================
   10. UI
   ================================ */
typedef void (*fn_api_ui_show_message)(const char* msg);
typedef void (*fn_api_ui_show_error)(const char* msg);
typedef int  (*fn_api_ui_confirm)(const char* msg);
typedef const char* (*fn_api_ui_input)(const char* prompt);
typedef void (*fn_api_ui_add_button)(const char* label, task_func func);
typedef void (*fn_api_ui_add_tab)(const char* name);
typedef void (*fn_api_ui_add_panel)(const char* name);
typedef void (*fn_api_ui_notify)(const char* title, const char* msg);
typedef const char* (*fn_api_ui_open_file_dialog)();
typedef const char* (*fn_api_ui_open_folder_dialog)();

extern fn_api_ui_show_message api_ui_show_message;
extern fn_api_ui_show_error api_ui_show_error;
extern fn_api_ui_confirm api_ui_confirm;
extern fn_api_ui_input api_ui_input;
extern fn_api_ui_add_button api_ui_add_button;
extern fn_api_ui_add_tab api_ui_add_tab;
extern fn_api_ui_add_panel api_ui_add_panel;
extern fn_api_ui_notify api_ui_notify;
extern fn_api_ui_open_file_dialog api_ui_open_file_dialog;
extern fn_api_ui_open_folder_dialog api_ui_open_folder_dialog;

/* ================================
   11. 工具 Utils
   ================================ */
typedef int  (*fn_api_util_random_int)(int min, int max);
typedef const char* (*fn_api_util_random_uuid)();
typedef const char* (*fn_api_util_sha256)(const char* data);
typedef const char* (*fn_api_util_base64_encode)(const char* data);
typedef const char* (*fn_api_util_base64_decode)(const char* data);
typedef long (*fn_api_util_timestamp)();
typedef const char* (*fn_api_util_now_iso)();
typedef void (*fn_api_util_sleep)(int ms);
typedef void (*fn_api_util_thread)(task_func func);
typedef long (*fn_api_util_benchmark)(task_func func);

extern fn_api_util_random_int api_util_random_int;
extern fn_api_util_random_uuid api_util_random_uuid;
extern fn_api_util_sha256 api_util_sha256;
extern fn_api_util_base64_encode api_util_base64_encode;
extern fn_api_util_base64_decode api_util_base64_decode;
extern fn_api_util_timestamp api_util_timestamp;
extern fn_api_util_now_iso api_util_now_iso;
extern fn_api_util_sleep api_util_sleep;
extern fn_api_util_thread api_util_thread;
extern fn_api_util_benchmark api_util_benchmark;

/* ================================
   插件生命周期
   ================================ */
typedef struct {
    void (*start)(void* launcher);
    void (*stop)();
    void (*reload)();
} PluginBase;

EXPORT PluginBase* create_plugin();

/* 注入单个 API（快速法） */
EXPORT void inject_api(const char* name, void* func);

#ifdef __cplusplus
}
#endif

#endif /* SPECTRUM_SDK_H */
