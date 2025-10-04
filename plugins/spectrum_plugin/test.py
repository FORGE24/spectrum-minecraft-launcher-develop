import spectrum_plugin as sp

sp.plugin_start()
sp.ui_add_button("点我测试C扩展按钮")
sp.ui_show_message("Hello from C!")
print("文件存在?", sp.fs_exists("main.py"))
print("最新版本:", sp.versions_latest())
print("CPU 核:", sp.system_cpu_count())
sp.scheduler_schedule("test_task", 2000)
sp.storage_set("player", "Steve")
sp.sysc_out_log("测试日志")
sp.plugin_stop()