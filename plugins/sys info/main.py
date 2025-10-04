# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets
import loader_api as api

class SystemInfoTab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QtWidgets.QVBoxLayout(self)

        self.info_label = QtWidgets.QLabel("点击按钮获取系统信息")
        layout.addWidget(self.info_label)

        self.refresh_btn = QtWidgets.QPushButton("刷新系统信息")
        self.refresh_btn.clicked.connect(self.refresh_info)
        layout.addWidget(self.refresh_btn)

    def refresh_info(self):
        try:
            os_name = api.api_system_os_name()
            cpu_count = api.api_system_cpu_count()
            mem_usage = api.api_system_memory_usage()
            py_ver = api.api_system_python_version()

            text = (
                f"操作系统: {os_name.decode('utf-8') if os_name else '未知'}\n"
                f"CPU 核心数: {cpu_count}\n"
                f"内存使用: {mem_usage} bytes\n"
                f"Python 版本: {py_ver.decode('utf-8') if py_ver else '未知'}"
            )
            self.info_label.setText(text)
            api.api_sysc_out_info("system_info 插件已刷新系统信息".encode("utf-8"))
        except Exception as e:
            api.api_sysc_out_error(f"system_info 插件刷新失败: {e}".encode("utf-8"))


class MyPlugin:
    def __init__(self):
        self.tab = None

    def on_enable(self):
        api.api_sysc_out_info("system_info 插件已启用".encode("utf-8"))

        app = QtWidgets.QApplication.instance()
        if not app:
            api.api_sysc_out_error("Qt 应用未初始化".encode("utf-8"))
            return

        main_win = None
        for w in app.topLevelWidgets():
            if isinstance(w, QtWidgets.QMainWindow):
                main_win = w
                break
        if not main_win:
            api.api_sysc_out_error("未找到主窗口".encode("utf-8"))
            return

        tab_widget = main_win.findChild(QtWidgets.QTabWidget, "mainTabWidget")
        if not tab_widget:
            api.api_sysc_out_error("未找到 mainTabWidget".encode("utf-8"))
            return

        self.tab = SystemInfoTab()
        tab_widget.addTab(self.tab, "系统信息")

    def on_disable(self):
        api.api_sysc_out_warn("system_info 插件已卸载".encode("utf-8"))
        if self.tab:
            self.tab.setParent(None)
            self.tab = None
