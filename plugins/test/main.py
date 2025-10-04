# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtCore
import loader_api as api

class PluginMenuTab(QtWidgets.QWidget):
    def __init__(self, plugin_manager, parent=None):
        super().__init__(parent)
        self.pm = plugin_manager

        layout = QtWidgets.QVBoxLayout(self)

        # 顶部刷新按钮
        self.refresh_btn = QtWidgets.QPushButton("刷新插件列表")
        self.refresh_btn.clicked.connect(self.refresh_plugins)
        layout.addWidget(self.refresh_btn)

        # 插件列表
        self.table = QtWidgets.QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["插件名", "状态", "操作"])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        self.refresh_plugins()

    def refresh_plugins(self):
        plugins = self.pm.list_plugins()
        self.table.setRowCount(len(plugins))

        for row, (name, info) in enumerate(plugins.items()):
            # 插件名
            self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(name))

            # 状态
            state = "已启用 ✅" if info["enabled"] else "未启用 ❌"
            self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(state))

            # 操作按钮
            btn = QtWidgets.QPushButton("启用" if not info["enabled"] else "禁用")
            def make_toggle(n):
                def toggle():
                    if self.pm.plugins[n].enabled:
                        api.api_sysc_out_warn(f"禁用插件 {n}".encode("utf-8"))
                        self.pm.unload_plugin(n)
                    else:
                        api.api_sysc_out_info(f"启用插件 {n}".encode("utf-8"))
                        self.pm.load_plugin(n)
                    self.refresh_plugins()
                return toggle
            btn.clicked.connect(make_toggle(name))
            self.table.setCellWidget(row, 2, btn)


class MyPlugin:
    def __init__(self):
        self.tab = None

    def on_enable(self):
        api.api_sysc_out_info("插件菜单 Tab 已启动".encode("utf-8"))

        app = QtWidgets.QApplication.instance()
        if not app:
            api.api_sysc_out_error("Qt 应用未初始化".encode("utf-8"))
            return

        # 找到主窗口
        main_win = None
        for w in app.topLevelWidgets():
            if isinstance(w, QtWidgets.QMainWindow):
                main_win = w
                break
        if not main_win:
            api.api_sysc_out_error("未找到主窗口".encode("utf-8"))
            return

        if not hasattr(api, "plugin_manager"):
            api.api_sysc_out_warn("未找到 plugin_manager".encode("utf-8"))
            return

        # 获取主窗口中的 TabWidget
        tab_widget = main_win.findChild(QtWidgets.QTabWidget, "mainTabWidget")
        if not tab_widget:
            api.api_sysc_out_error("未找到 mainTabWidget".encode("utf-8"))
            return

        # 创建并添加 Tab
        self.tab = PluginMenuTab(api.plugin_manager)
        tab_widget.addTab(self.tab, "插件管理")

    def on_disable(self):
        api.api_sysc_out_info("插件菜单 Tab 已卸载".encode("utf-8"))
        if self.tab:
            self.tab.setParent(None)
            self.tab = None
