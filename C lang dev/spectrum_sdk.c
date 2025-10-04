#include "spectrum_sdk.h"
#include <string.h>
#include <stddef.h>

#ifdef _WIN32
#define NULLPTR NULL
#else
#define NULLPTR NULL
#endif

/* ---------------------------
   在此文件中定义所有 extern 指针并初始化为 NULL
   --------------------------- */

/* 1. 日志 */
fn_api_sysc_out_info api_sysc_out_info = NULLPTR;
fn_api_sysc_out_log api_sysc_out_log = NULLPTR;
fn_api_sysc_out_warn api_sysc_out_warn = NULLPTR;
fn_api_sysc_out_error api_sysc_out_error = NULLPTR;
fn_api_sysc_out_debug api_sysc_out_debug = NULLPTR;
fn_api_sysc_out_printf api_sysc_out_printf = NULLPTR;
fn_api_sysc_out_clear api_sysc_out_clear = NULLPTR;
fn_api_sysc_out_set_level api_sysc_out_set_level = NULLPTR;
fn_api_sysc_out_export api_sysc_out_export = NULLPTR;
fn_api_sysc_out_subscribe api_sysc_out_subscribe = NULLPTR;

/* 2. 存储 */
fn_api_storage_set api_storage_set = NULLPTR;
fn_api_storage_get api_storage_get = NULLPTR;
fn_api_storage_remove api_storage_remove = NULLPTR;
fn_api_storage_keys api_storage_keys = NULLPTR;
fn_api_storage_clear api_storage_clear = NULLPTR;
fn_api_storage_save api_storage_save = NULLPTR;
fn_api_storage_load api_storage_load = NULLPTR;
fn_api_storage_contains api_storage_contains = NULLPTR;
fn_api_storage_size api_storage_size = NULLPTR;
fn_api_storage_watch api_storage_watch = NULLPTR;

/* 3. 调度 */
fn_api_scheduler_schedule api_scheduler_schedule = NULLPTR;
fn_api_scheduler_schedule_delay api_scheduler_schedule_delay = NULLPTR;
fn_api_scheduler_schedule_repeat api_scheduler_schedule_repeat = NULLPTR;
fn_api_scheduler_cancel api_scheduler_cancel = NULLPTR;
fn_api_scheduler_cancel_all api_scheduler_cancel_all = NULLPTR;
fn_api_scheduler_is_running api_scheduler_is_running = NULLPTR;
fn_api_scheduler_list_tasks api_scheduler_list_tasks = NULLPTR;
fn_api_scheduler_pause api_scheduler_pause = NULLPTR;
fn_api_scheduler_resume api_scheduler_resume = NULLPTR;
fn_api_scheduler_set_priority api_scheduler_set_priority = NULLPTR;

/* 4. 系统信息 */
fn_api_system_os_name api_system_os_name = NULLPTR;
fn_api_system_arch api_system_arch = NULLPTR;
fn_api_system_jvm_version api_system_jvm_version = NULLPTR;
fn_api_system_python_version api_system_python_version = NULLPTR;
fn_api_system_memory_usage api_system_memory_usage = NULLPTR;
fn_api_system_cpu_count api_system_cpu_count = NULLPTR;
fn_api_system_disk_usage api_system_disk_usage = NULLPTR;
fn_api_system_uptime api_system_uptime = NULLPTR;
fn_api_system_process_list api_system_process_list = NULLPTR;
fn_api_system_gpu_info api_system_gpu_info = NULLPTR;

/* 5. 版本管理 */
fn_api_versions_all api_versions_all = NULLPTR;
fn_api_versions_latest api_versions_latest = NULLPTR;
fn_api_versions_filter api_versions_filter = NULLPTR;
fn_api_versions_for_each api_versions_for_each = NULLPTR;
fn_api_versions_installed api_versions_installed = NULLPTR;
fn_api_versions_download api_versions_download = NULLPTR;
fn_api_versions_remove api_versions_remove = NULLPTR;
fn_api_versions_is_installed api_versions_is_installed = NULLPTR;
fn_api_versions_size api_versions_size = NULLPTR;
fn_api_versions_set_default api_versions_set_default = NULLPTR;

/* 6. 网络 */
fn_api_net_http_get api_net_http_get = NULLPTR;
fn_api_net_http_post api_net_http_post = NULLPTR;
fn_api_net_download api_net_download = NULLPTR;
fn_api_net_ping api_net_ping = NULLPTR;
fn_api_net_websocket api_net_websocket = NULLPTR;
fn_api_net_http_put api_net_http_put = NULLPTR;
fn_api_net_http_delete api_net_http_delete = NULLPTR;
fn_api_net_dns_lookup api_net_dns_lookup = NULLPTR;
fn_api_net_speed_test api_net_speed_test = NULLPTR;
fn_api_net_open_browser api_net_open_browser = NULLPTR;

/* 7. 文件系统 */
fn_api_fs_read api_fs_read = NULLPTR;
fn_api_fs_write api_fs_write = NULLPTR;
fn_api_fs_exists api_fs_exists = NULLPTR;
fn_api_fs_delete api_fs_delete = NULLPTR;
fn_api_fs_mkdirs api_fs_mkdirs = NULLPTR;
fn_api_fs_copy api_fs_copy = NULLPTR;
fn_api_fs_move api_fs_move = NULLPTR;
fn_api_fs_size api_fs_size = NULLPTR;
fn_api_fs_list_dir api_fs_list_dir = NULLPTR;
fn_api_fs_watch api_fs_watch = NULLPTR;

/* 8. 事件 */
fn_api_events_register api_events_register = NULLPTR;
fn_api_events_unregister api_events_unregister = NULLPTR;
fn_api_events_fire api_events_fire = NULLPTR;
fn_api_events_list api_events_list = NULLPTR;
fn_api_events_has api_events_has = NULLPTR;
fn_api_events_clear_all api_events_clear_all = NULLPTR;
fn_api_events_once api_events_once = NULLPTR;
fn_api_events_priority api_events_priority = NULLPTR;
fn_api_events_cancel api_events_cancel = NULLPTR;
fn_api_events_emit_async api_events_emit_async = NULLPTR;

/* 9. 玩家 */
fn_api_player_login api_player_login = NULLPTR;
fn_api_player_logout api_player_logout = NULLPTR;
fn_api_player_list api_player_list = NULLPTR;
fn_api_player_get api_player_get = NULLPTR;
fn_api_player_is_online api_player_is_online = NULLPTR;
fn_api_player_ban api_player_ban = NULLPTR;
fn_api_player_unban api_player_unban = NULLPTR;
fn_api_player_kick api_player_kick = NULLPTR;
fn_api_player_send_message api_player_send_message = NULLPTR;
fn_api_player_broadcast api_player_broadcast = NULLPTR;

/* 10. UI */
fn_api_ui_show_message api_ui_show_message = NULLPTR;
fn_api_ui_show_error api_ui_show_error = NULLPTR;
fn_api_ui_confirm api_ui_confirm = NULLPTR;
fn_api_ui_input api_ui_input = NULLPTR;
fn_api_ui_add_button api_ui_add_button = NULLPTR;
fn_api_ui_add_tab api_ui_add_tab = NULLPTR;
fn_api_ui_add_panel api_ui_add_panel = NULLPTR;
fn_api_ui_notify api_ui_notify = NULLPTR;
fn_api_ui_open_file_dialog api_ui_open_file_dialog = NULLPTR;
fn_api_ui_open_folder_dialog api_ui_open_folder_dialog = NULLPTR;

/* 11. Utils */
fn_api_util_random_int api_util_random_int = NULLPTR;
fn_api_util_random_uuid api_util_random_uuid = NULLPTR;
fn_api_util_sha256 api_util_sha256 = NULLPTR;
fn_api_util_base64_encode api_util_base64_encode = NULLPTR;
fn_api_util_base64_decode api_util_base64_decode = NULLPTR;
fn_api_util_timestamp api_util_timestamp = NULLPTR;
fn_api_util_now_iso api_util_now_iso = NULLPTR;
fn_api_util_sleep api_util_sleep = NULLPTR;
fn_api_util_thread api_util_thread = NULLPTR;
fn_api_util_benchmark api_util_benchmark = NULLPTR;

/* ---------------------------
   inject_api 实现：将 name -> 相应指针填充（C 插件在运行时调用）
   注：当你新增 API 时同时在此处添加映射
   --------------------------- */
EXPORT void inject_api(const char* name, void* func) {
    if (!name || !func) return;

    /* 使用 strcmp 链式比对并进行强制类型转换 */
    if (strcmp(name, "api_sysc_out_info") == 0) { api_sysc_out_info = (fn_api_sysc_out_info)func; return; }
    if (strcmp(name, "api_sysc_out_log") == 0) { api_sysc_out_log = (fn_api_sysc_out_log)func; return; }
    if (strcmp(name, "api_sysc_out_warn") == 0) { api_sysc_out_warn = (fn_api_sysc_out_warn)func; return; }
    if (strcmp(name, "api_sysc_out_error") == 0) { api_sysc_out_error = (fn_api_sysc_out_error)func; return; }
    if (strcmp(name, "api_sysc_out_debug") == 0) { api_sysc_out_debug = (fn_api_sysc_out_debug)func; return; }
    if (strcmp(name, "api_sysc_out_printf") == 0) { api_sysc_out_printf = (fn_api_sysc_out_printf)func; return; }
    if (strcmp(name, "api_sysc_out_clear") == 0) { api_sysc_out_clear = (fn_api_sysc_out_clear)func; return; }
    if (strcmp(name, "api_sysc_out_set_level") == 0) { api_sysc_out_set_level = (fn_api_sysc_out_set_level)func; return; }
    if (strcmp(name, "api_sysc_out_export") == 0) { api_sysc_out_export = (fn_api_sysc_out_export)func; return; }
    if (strcmp(name, "api_sysc_out_subscribe") == 0) { api_sysc_out_subscribe = (void(*)(void(*)(const char*)))func; return; }

    if (strcmp(name, "api_storage_set") == 0) { api_storage_set = (fn_api_storage_set)func; return; }
    if (strcmp(name, "api_storage_get") == 0) { api_storage_get = (fn_api_storage_get)func; return; }
    if (strcmp(name, "api_storage_remove") == 0) { api_storage_remove = (fn_api_storage_remove)func; return; }
    if (strcmp(name, "api_storage_keys") == 0) { api_storage_keys = (fn_api_storage_keys)func; return; }
    if (strcmp(name, "api_storage_clear") == 0) { api_storage_clear = (fn_api_storage_clear)func; return; }
    if (strcmp(name, "api_storage_save") == 0) { api_storage_save = (fn_api_storage_save)func; return; }
    if (strcmp(name, "api_storage_load") == 0) { api_storage_load = (fn_api_storage_load)func; return; }
    if (strcmp(name, "api_storage_contains") == 0) { api_storage_contains = (fn_api_storage_contains)func; return; }
    if (strcmp(name, "api_storage_size") == 0) { api_storage_size = (fn_api_storage_size)func; return; }
    if (strcmp(name, "api_storage_watch") == 0) { api_storage_watch = (fn_api_storage_watch)func; return; }

    if (strcmp(name, "api_scheduler_schedule") == 0) { api_scheduler_schedule = (fn_api_scheduler_schedule)func; return; }
    if (strcmp(name, "api_scheduler_schedule_delay") == 0) { api_scheduler_schedule_delay = (fn_api_scheduler_schedule_delay)func; return; }
    if (strcmp(name, "api_scheduler_schedule_repeat") == 0) { api_scheduler_schedule_repeat = (fn_api_scheduler_schedule_repeat)func; return; }
    if (strcmp(name, "api_scheduler_cancel") == 0) { api_scheduler_cancel = (fn_api_scheduler_cancel)func; return; }
    if (strcmp(name, "api_scheduler_cancel_all") == 0) { api_scheduler_cancel_all = (fn_api_scheduler_cancel_all)func; return; }
    if (strcmp(name, "api_scheduler_is_running") == 0) { api_scheduler_is_running = (fn_api_scheduler_is_running)func; return; }
    if (strcmp(name, "api_scheduler_list_tasks") == 0) { api_scheduler_list_tasks = (fn_api_scheduler_list_tasks)func; return; }
    if (strcmp(name, "api_scheduler_pause") == 0) { api_scheduler_pause = (fn_api_scheduler_pause)func; return; }
    if (strcmp(name, "api_scheduler_resume") == 0) { api_scheduler_resume = (fn_api_scheduler_resume)func; return; }
    if (strcmp(name, "api_scheduler_set_priority") == 0) { api_scheduler_set_priority = (fn_api_scheduler_set_priority)func; return; }

    if (strcmp(name, "api_system_os_name") == 0) { api_system_os_name = (fn_api_system_os_name)func; return; }
    if (strcmp(name, "api_system_arch") == 0) { api_system_arch = (fn_api_system_arch)func; return; }
    if (strcmp(name, "api_system_jvm_version") == 0) { api_system_jvm_version = (fn_api_system_jvm_version)func; return; }
    if (strcmp(name, "api_system_python_version") == 0) { api_system_python_version = (fn_api_system_python_version)func; return; }
    if (strcmp(name, "api_system_memory_usage") == 0) { api_system_memory_usage = (fn_api_system_memory_usage)func; return; }
    if (strcmp(name, "api_system_cpu_count") == 0) { api_system_cpu_count = (fn_api_system_cpu_count)func; return; }
    if (strcmp(name, "api_system_disk_usage") == 0) { api_system_disk_usage = (fn_api_system_disk_usage)func; return; }
    if (strcmp(name, "api_system_uptime") == 0) { api_system_uptime = (fn_api_system_uptime)func; return; }
    if (strcmp(name, "api_system_process_list") == 0) { api_system_process_list = (fn_api_system_process_list)func; return; }
    if (strcmp(name, "api_system_gpu_info") == 0) { api_system_gpu_info = (fn_api_system_gpu_info)func; return; }

    if (strcmp(name, "api_versions_all") == 0) { api_versions_all = (fn_api_versions_all)func; return; }
    if (strcmp(name, "api_versions_latest") == 0) { api_versions_latest = (fn_api_versions_latest)func; return; }
    if (strcmp(name, "api_versions_filter") == 0) { api_versions_filter = (fn_api_versions_filter)func; return; }
    if (strcmp(name, "api_versions_for_each") == 0) { api_versions_for_each = (fn_api_versions_for_each)func; return; }
    if (strcmp(name, "api_versions_installed") == 0) { api_versions_installed = (fn_api_versions_installed)func; return; }
    if (strcmp(name, "api_versions_download") == 0) { api_versions_download = (fn_api_versions_download)func; return; }
    if (strcmp(name, "api_versions_remove") == 0) { api_versions_remove = (fn_api_versions_remove)func; return; }
    if (strcmp(name, "api_versions_is_installed") == 0) { api_versions_is_installed = (fn_api_versions_is_installed)func; return; }
    if (strcmp(name, "api_versions_size") == 0) { api_versions_size = (fn_api_versions_size)func; return; }
    if (strcmp(name, "api_versions_set_default") == 0) { api_versions_set_default = (fn_api_versions_set_default)func; return; }

    if (strcmp(name, "api_net_http_get") == 0) { api_net_http_get = (fn_api_net_http_get)func; return; }
    if (strcmp(name, "api_net_http_post") == 0) { api_net_http_post = (fn_api_net_http_post)func; return; }
    if (strcmp(name, "api_net_download") == 0) { api_net_download = (fn_api_net_download)func; return; }
    if (strcmp(name, "api_net_ping") == 0) { api_net_ping = (fn_api_net_ping)func; return; }
    if (strcmp(name, "api_net_websocket") == 0) { api_net_websocket = (fn_api_net_websocket)func; return; }
    if (strcmp(name, "api_net_http_put") == 0) { api_net_http_put = (fn_api_net_http_put)func; return; }
    if (strcmp(name, "api_net_http_delete") == 0) { api_net_http_delete = (fn_api_net_http_delete)func; return; }
    if (strcmp(name, "api_net_dns_lookup") == 0) { api_net_dns_lookup = (fn_api_net_dns_lookup)func; return; }
    if (strcmp(name, "api_net_speed_test") == 0) { api_net_speed_test = (fn_api_net_speed_test)func; return; }
    if (strcmp(name, "api_net_open_browser") == 0) { api_net_open_browser = (fn_api_net_open_browser)func; return; }

    if (strcmp(name, "api_fs_read") == 0) { api_fs_read = (fn_api_fs_read)func; return; }
    if (strcmp(name, "api_fs_write") == 0) { api_fs_write = (fn_api_fs_write)func; return; }
    if (strcmp(name, "api_fs_exists") == 0) { api_fs_exists = (fn_api_fs_exists)func; return; }
    if (strcmp(name, "api_fs_delete") == 0) { api_fs_delete = (fn_api_fs_delete)func; return; }
    if (strcmp(name, "api_fs_mkdirs") == 0) { api_fs_mkdirs = (fn_api_fs_mkdirs)func; return; }
    if (strcmp(name, "api_fs_copy") == 0) { api_fs_copy = (fn_api_fs_copy)func; return; }
    if (strcmp(name, "api_fs_move") == 0) { api_fs_move = (fn_api_fs_move)func; return; }
    if (strcmp(name, "api_fs_size") == 0) { api_fs_size = (fn_api_fs_size)func; return; }
    if (strcmp(name, "api_fs_list_dir") == 0) { api_fs_list_dir = (fn_api_fs_list_dir)func; return; }
    if (strcmp(name, "api_fs_watch") == 0) { api_fs_watch = (fn_api_fs_watch)func; return; }

    if (strcmp(name, "api_events_register") == 0) { api_events_register = (fn_api_events_register)func; return; }
    if (strcmp(name, "api_events_unregister") == 0) { api_events_unregister = (fn_api_events_unregister)func; return; }
    if (strcmp(name, "api_events_fire") == 0) { api_events_fire = (fn_api_events_fire)func; return; }
    if (strcmp(name, "api_events_list") == 0) { api_events_list = (fn_api_events_list)func; return; }
    if (strcmp(name, "api_events_has") == 0) { api_events_has = (fn_api_events_has)func; return; }
    if (strcmp(name, "api_events_clear_all") == 0) { api_events_clear_all = (fn_api_events_clear_all)func; return; }
    if (strcmp(name, "api_events_once") == 0) { api_events_once = (fn_api_events_once)func; return; }
    if (strcmp(name, "api_events_priority") == 0) { api_events_priority = (fn_api_events_priority)func; return; }
    if (strcmp(name, "api_events_cancel") == 0) { api_events_cancel = (fn_api_events_cancel)func; return; }
    if (strcmp(name, "api_events_emit_async") == 0) { api_events_emit_async = (fn_api_events_emit_async)func; return; }

    if (strcmp(name, "api_player_login") == 0) { api_player_login = (fn_api_player_login)func; return; }
    if (strcmp(name, "api_player_logout") == 0) { api_player_logout = (fn_api_player_logout)func; return; }
    if (strcmp(name, "api_player_list") == 0) { api_player_list = (fn_api_player_list)func; return; }
    if (strcmp(name, "api_player_get") == 0) { api_player_get = (fn_api_player_get)func; return; }
    if (strcmp(name, "api_player_is_online") == 0) { api_player_is_online = (fn_api_player_is_online)func; return; }
    if (strcmp(name, "api_player_ban") == 0) { api_player_ban = (fn_api_player_ban)func; return; }
    if (strcmp(name, "api_player_unban") == 0) { api_player_unban = (fn_api_player_unban)func; return; }
    if (strcmp(name, "api_player_kick") == 0) { api_player_kick = (fn_api_player_kick)func; return; }
    if (strcmp(name, "api_player_send_message") == 0) { api_player_send_message = (fn_api_player_send_message)func; return; }
    if (strcmp(name, "api_player_broadcast") == 0) { api_player_broadcast = (fn_api_player_broadcast)func; return; }

    if (strcmp(name, "api_ui_show_message") == 0) { api_ui_show_message = (fn_api_ui_show_message)func; return; }
    if (strcmp(name, "api_ui_show_error") == 0) { api_ui_show_error = (fn_api_ui_show_error)func; return; }
    if (strcmp(name, "api_ui_confirm") == 0) { api_ui_confirm = (fn_api_ui_confirm)func; return; }
    if (strcmp(name, "api_ui_input") == 0) { api_ui_input = (fn_api_ui_input)func; return; }
    if (strcmp(name, "api_ui_add_button") == 0) { api_ui_add_button = (fn_api_ui_add_button)func; return; }
    if (strcmp(name, "api_ui_add_tab") == 0) { api_ui_add_tab = (fn_api_ui_add_tab)func; return; }
    if (strcmp(name, "api_ui_add_panel") == 0) { api_ui_add_panel = (fn_api_ui_add_panel)func; return; }
    if (strcmp(name, "api_ui_notify") == 0) { api_ui_notify = (fn_api_ui_notify)func; return; }
    if (strcmp(name, "api_ui_open_file_dialog") == 0) { api_ui_open_file_dialog = (fn_api_ui_open_file_dialog)func; return; }
    if (strcmp(name, "api_ui_open_folder_dialog") == 0) { api_ui_open_folder_dialog = (fn_api_ui_open_folder_dialog)func; return; }

    if (strcmp(name, "api_util_random_int") == 0) { api_util_random_int = (fn_api_util_random_int)func; return; }
    if (strcmp(name, "api_util_random_uuid") == 0) { api_util_random_uuid = (fn_api_util_random_uuid)func; return; }
    if (strcmp(name, "api_util_sha256") == 0) { api_util_sha256 = (fn_api_util_sha256)func; return; }
    if (strcmp(name, "api_util_base64_encode") == 0) { api_util_base64_encode = (fn_api_util_base64_encode)func; return; }
    if (strcmp(name, "api_util_base64_decode") == 0) { api_util_base64_decode = (fn_api_util_base64_decode)func; return; }
    if (strcmp(name, "api_util_timestamp") == 0) { api_util_timestamp = (fn_api_util_timestamp)func; return; }
    if (strcmp(name, "api_util_now_iso") == 0) { api_util_now_iso = (fn_api_util_now_iso)func; return; }
    if (strcmp(name, "api_util_sleep") == 0) { api_util_sleep = (fn_api_util_sleep)func; return; }
    if (strcmp(name, "api_util_thread") == 0) { api_util_thread = (fn_api_util_thread)func; return; }
    if (strcmp(name, "api_util_benchmark") == 0) { api_util_benchmark = (fn_api_util_benchmark)func; return; }

    /* 如果未命中，忽略（可扩展） */
}
