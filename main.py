from mclauncher_core.tool_funcs import get_java_version

USE_OS_SYSTEM_TO_EXECUTE = 0
version = '3.5.0'
from ctypes import Structure, c_void_p, CFUNCTYPE, POINTER, cast
import ctypes
import sys
import os
from PyQt5.QtCore import Qt, QStringListModel, QProcess
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog
from PyQt5.QtGui import QStandardItemModel, QIcon, QStandardItem
import re
import json
from mclauncher_core.javawrapper import download_javawrapper
import mclauncher_core.launcher_funcs as launcher
import mclauncher_core.manager as manager
import mclauncher_core.download_funcs as downloader
import mclauncher_core.java as java
import mclauncher_core.modloader_fabric as fabric
import mclauncher_core.modloader_forge as forge
import mclauncher_core.modloader_neoforge as neoforge

import shutil
import zipfile as z
import requests
from ui import Ui_MainWindow

import loader_api as api

import importlib.util
import pathlib

import loader_bind_all


from plugin_manager import PluginManager
import loader_api as api

# 初始化插件管理器
pm = PluginManager()
pm.load_all()

# 注入到 api
api.plugin_manager = pm


# 保存插件引用，防止 GC
_loaded_plugins = []


def load_stylesheet(app, filename="style.qss"):
    """从外部 QSS 文件加载主题"""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except Exception as e:
        print(f"无法加载样式表 {filename}: {e}")

# 定义 PluginBase 与 C 端一致
class PluginBaseStruct(Structure):
    _fields_ = [
        ("start", c_void_p),   # void (*start)(void* launcher)
        ("stop", c_void_p),    # void (*stop)()
        ("reload", c_void_p)   # void (*reload)()
    ]

def load_dll_plugins():
    plugins_dir = os.path.join(app_path(), "plugins")
    if not os.path.exists(plugins_dir):
        os.makedirs(plugins_dir)

    dll_files = [f for f in os.listdir(plugins_dir) if f.lower().endswith(".dll")]
    if not dll_files:
        print("[DLL Loader] 未在 plugins/ 下找到 DLL 插件")
        return

    for dll_file in dll_files:
        dll_path = os.path.join(plugins_dir, dll_file)
        try:
            dll = ctypes.CDLL(dll_path)
            print(f"[DLL Loader] 成功加载 DLL 插件: {dll_file}")

            # 注入 API
            try:
                loader_bind_all.inject_all_api(dll)
                print(f"[DLL Loader] API 注入完成: {dll_file}")
            except Exception as e:
                print(f"[DLL Loader] 注入 API 失败: {dll_file} -> {e}")

            # 调用 create_plugin
            try:
                if hasattr(dll, "create_plugin"):
                    dll.create_plugin.restype = c_void_p
                    plugin_ptr = dll.create_plugin()
                    print(f"[DLL Loader] create_plugin 调用完成 ({dll_file}) -> 实例指针 {plugin_ptr}")

                    if plugin_ptr:
                        plugin_struct = cast(plugin_ptr, POINTER(PluginBaseStruct)).contents

                        # 转换函数指针
                        start_fn = None
                        stop_fn = None
                        reload_fn = None

                        if plugin_struct.start:
                            START_CTYPE = CFUNCTYPE(None, c_void_p)
                            start_fn = START_CTYPE(plugin_struct.start)
                        if plugin_struct.stop:
                            STOP_CTYPE = CFUNCTYPE(None)
                            stop_fn = STOP_CTYPE(plugin_struct.stop)
                        if plugin_struct.reload:
                            RELOAD_CTYPE = CFUNCTYPE(None)
                            reload_fn = RELOAD_CTYPE(plugin_struct.reload)

                        # 保存引用
                        _loaded_plugins.append({
                            "dll_file": dll_file,
                            "dll": dll,
                            "plugin_ptr": plugin_ptr,
                            "start": start_fn,
                            "stop": stop_fn,
                            "reload": reload_fn
                        })

                        # 调用 start()
                        if start_fn:
                            try:
                                start_fn(None)  # launcher 参数传 NULL
                                print(f"[DLL Loader] 调用 start() 成功 ({dll_file})")
                            except Exception as e:
                                print(f"[DLL Loader] 调用 start() 失败 ({dll_file}) -> {e}")
                        else:
                            print(f"[DLL Loader] {dll_file} 的 start 函数为空")

                else:
                    print(f"[DLL Loader] {dll_file} 未导出 create_plugin")
            except Exception as e:
                print(f"[DLL Loader] 调用 create_plugin 失败 ({dll_file}) -> {e}")

        except Exception as e:
            print(f"[DLL Loader] 无法加载 DLL: {dll_file} -> {e}")

def load_dll_plugins():
    # 插件目录
    plugins_dir = os.path.join(app_path(), "plugins")
    if not os.path.exists(plugins_dir):
        os.makedirs(plugins_dir)

    # 遍历 plugins 文件夹里的所有 DLL 文件
    dll_files = [f for f in os.listdir(plugins_dir) if f.lower().endswith(".dll")]
    if not dll_files:
        print("[DLL Loader] 未在 plugins/ 下找到 DLL 插件")
        return

    for dll_file in dll_files:
        dll_path = os.path.join(plugins_dir, dll_file)
        try:
            dll = ctypes.CDLL(dll_path)
            print(f"[DLL Loader] 成功加载 DLL 插件: {dll_file}")

            # 注入所有 API
            try:
                loader_bind_all.inject_all_api(dll)
                print(f"[DLL Loader] API 注入完成: {dll_file}")
            except Exception as e:
                print(f"[DLL Loader] 注入 API 失败: {dll_file} -> {e}")

            # 调用 create_plugin（如果存在）
            try:
                if hasattr(dll, "create_plugin"):
                    dll.create_plugin.restype = ctypes.c_void_p
                    plugin_ptr = dll.create_plugin()
                    print(f"[DLL Loader] create_plugin 调用完成 ({dll_file}) -> 实例指针 {plugin_ptr}")
                else:
                    print(f"[DLL Loader] {dll_file} 未导出 create_plugin")
            except Exception as e:
                print(f"[DLL Loader] 调用 create_plugin 失败 ({dll_file}) -> {e}")

        except Exception as e:
            print(f"[DLL Loader] 无法加载 DLL: {dll_file} -> {e}")

class PluginLoader:
    def __init__(self, plugin_dir="plugins"):
        self.plugin_dir = pathlib.Path(plugin_dir)
        self.plugins = {}

    def load_plugins(self):
        if not self.plugin_dir.exists():
            return
        for plugin_path in self.plugin_dir.glob("*/main.py"):
            name = plugin_path.parent.name
            spec = importlib.util.spec_from_file_location(name, plugin_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if hasattr(module, "MyPlugin"):
                plugin = module.MyPlugin()
                self.plugins[name] = plugin
                plugin.on_enable()
                print(f"[Plugin] {name} 已加载 ")

    def unload_plugins(self):
        for name, plugin in self.plugins.items():
            if hasattr(plugin, "on_disable"):
                plugin.on_disable()
        self.plugins.clear()
def check_update():
    pass
    # 可以以后扩展 GitHub Release 检查


def app_path():
    if getattr(sys, 'frozen', False):
        path = os.path.dirname(sys.executable)
    else:
        path = os.path.dirname(os.path.abspath(__file__))

    path = path.replace('\\', '/')
    if path[-1] == '/':
        path = path[:-1]

    return str(path)


def fpath(path):
    path = path.replace('\\', '/')
    if path[-1] == '/':
        path = path[:-1]
    return path


default_icon = app_path() + '/assets/default_icon.png'

if not os.path.exists(default_icon):
    QMessageBox.critical(None, 'Assets load fail', default_icon)


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        check_update()

        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        # Stuff
        self.using_mc_login = False
        self.mc_token = None
        self.autodl_fabric_api = False

        # 设置版本列表
        self.model = QStringListModel()
        data = downloader.get_version_list()
        self.model.setStringList(data)
        self.listView.setModel(self.model)  # 版本列表

        self.checkBox.stateChanged.connect(self.update_version_list)
        self.checkBox_2.stateChanged.connect(self.update_version_list)
        self.checkBox_3.stateChanged.connect(self.update_version_list)
        self.checkBox_4.stateChanged.connect(self.update_version_list)

        self.pushButton_15.clicked.connect(self.save_config)
        self.pushButton_3.clicked.connect(self.download)
        self.lineEdit.editingFinished.connect(self.update_installed_versions)
        self.LaunchBtn.clicked.connect(self.launch)
        self.comboBox.currentTextChanged.connect(self.update_ml_version_list)
        self.mainTabWidget.currentChanged.connect(self.page_process)
        self.comboBox_5.currentTextChanged.connect(self.switch_manager_select_version)

        self.pushButton_4.clicked.connect(self.remove_version)
        self.pushButton_5.clicked.connect(self.remove_save)
        self.pushButton_6.clicked.connect(self.remove_respack)
        self.DownloadFixBtn.clicked.connect(self.download_fix)
        self.pushButton_2.clicked.connect(self.oauth)
        self.lineEdit_6.textChanged.connect(self.disable_mslogin)
        self.checkBox_5.clicked.connect(self.toggle_fabric_api_autodownload)

        self.pushButton_10.clicked.connect(lambda: self.download_java(8, callback=self.progressBar_3.setValue))
        self.pushButton_11.clicked.connect(lambda: self.download_java(17, callback=self.progressBar_3.setValue))
        self.pushButton_12.clicked.connect(lambda: self.download_java(21, callback=self.progressBar_3.setValue))
        self.pushButton_9.clicked.connect(self.rename_version)
        self.pushButton_13.clicked.connect(lambda: self.lineEdit.setText(self.open_folder()))

        self.load_config()
        self.update_installed_versions()

    # ================= UI 操作 =================

    def open_folder(self):
        return QFileDialog.getExistingDirectory(self, "选择文件夹", app_path())

    def open_file(self):
        return QFileDialog.getOpenFileName(self, self, "选择文件", app_path())

    def rename_version(self):
        if self.lineEdit_5.text() == "":
            QMessageBox.warning(None, 'Spectrum 启动器', '你必须输入一个名称。')
        new_name = self.lineEdit_5.text()
        version_name = self.comboBox_5.currentText()
        minecraft_dir = self.lineEdit.text().replace('\\', '/')
        if minecraft_dir[-1] == '/':
            minecraft_dir = minecraft_dir[:-1]
        if not os.path.exists(minecraft_dir):
            return 1
        manager.rename_version(minecraft_dir, version_name, new_name)
        self.update_installed_versions()

    # ================= Java 下载 =================

    def download_java(self, major_version: int, callback=None):
        print('Retrieving url')
        url = java.get_url(major_version, 'jdk', tuna=False).replace('https://github.com/',
                                                                     'https://ghfast.top/https://github.com/')
        print('Trying: ' + url)
        try:
            response = requests.get(url, stream=True)
            if response.status_code != 200:
                raise Exception('Download failed: ' + str(response.status_code))

            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0

            with open('java_installer.msi', 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)

                        if total_size > 0:
                            progress = (downloaded_size / total_size) * 100
                            progress_percent = round(progress, 1)

                            if callback:
                                callback(int(progress_percent))
                            else:
                                print(f"\r下载进度: {progress_percent}%", end='', flush=True)

            if callback:
                callback(100)
            else:
                print("\r下载进度: 100% - 下载完成!")

        except Exception as e:
            print(f"下载过程中出现错误: {e}")
            raise

        os.system(f'cmd /c start msiexec /i {app_path()}/java_installer.msi')
    def toggle_fabric_api_autodownload(self, stat=''):
        self.autodl_fabric_api = stat

    def debug_print(self, b=''):
        print(b)
        print(self.using_mc_login)
        print(self.mc_token)

    def disable_mslogin(self):
        self.using_mc_login = False

    def oauth(self):
        try:
            self.using_mc_login = True
            self.mc_token = launcher.get_mc_token()
        except Exception as e:
            input('EXCEPTION: ' + str(e))
            self.using_mc_login = False
            self.mc_token = None

    # ================= 删除操作 =================

    def remove_version(self):
        minecraft_dir = self.lineEdit.text().replace('\\', '/')
        if minecraft_dir[-1] == '/':
            minecraft_dir = minecraft_dir[:-1]
        if not os.path.exists(minecraft_dir):
            return 1
        if len(str(self.comboBox_5.currentText())) == 0:
            QMessageBox.critical(None, 'Spectrum 启动器', '你必须选择一个版本。')
            return 1
        ver = str(self.comboBox_5.currentText())

        QMessageBox.information(None, 'Spectrum 启动器', f'“{ver}”将会永久消失！（真的很久！）')
        launcher.remove_version(minecraft_dir, ver)
        self.update_installed_versions()

    def remove_save(self):
        minecraft_dir = self.lineEdit.text().replace('\\', '/')
        if minecraft_dir[-1] == '/':
            minecraft_dir = minecraft_dir[:-1]
        if not os.path.exists(minecraft_dir):
            return 1

        ver = self.comboBox_5.currentText()
        if ver == '':
            QMessageBox.critical(None, 'Spectrum 启动器', '你必须选择一个版本。')
            return 1
        if len(self.listView_saves.selectionModel().selectedIndexes()) == 0:
            QMessageBox.critical(None, 'Spectrum 启动器', '你必须选择一个存档。')
            return 1
        save = self.listView_saves.selectionModel().selectedIndexes()[0].data()

        QMessageBox.information(None, 'Spectrum 启动器', f'“{save}”将会永久消失！（真的很久！）')
        manager.remove_save(minecraft_dir, ver, save)
        self.switch_manager_select_version(version_name=ver)

    def remove_respack(self):
        minecraft_dir = self.lineEdit.text().replace('\\', '/')
        if minecraft_dir[-1] == '/':
            minecraft_dir = minecraft_dir[:-1]
        if not os.path.exists(minecraft_dir):
            return 1

        ver = self.comboBox_5.currentText()
        if ver == '':
            QMessageBox.critical(None, 'Spectrum 启动器', '你必须选择一个版本。')
            return 1
        if len(self.listView_respacks.selectionModel().selectedIndexes()) == 0:
            QMessageBox.critical(None, 'Spectrum 启动器', '你必须选择一个资源包。')
            return 1
        respack = self.listView_respacks.selectionModel().selectedIndexes()[0].data()

        QMessageBox.information(None, 'Spectrum 启动器', f'“{respack}”将会永久消失！（真的很久！）')
        manager.remove_resourcepack(minecraft_dir, ver, respack)
        self.switch_manager_select_version(version_name=ver)

    # ================= 切换版本 UI =================

    def switch_manager_select_version(self, version_name):
        minecraft_dir = self.lineEdit.text().replace('\\', '/')
        if minecraft_dir[-1] == '/':
            minecraft_dir = minecraft_dir[:-1]
        if not os.path.exists(minecraft_dir):
            return 1

        if self.comboBox_5.currentText() == '':
            return 1
        version_name = self.comboBox_5.currentText()

        # 存档
        self.model_saves = QStandardItemModel()
        data = manager.get_saves(minecraft_dir, version_name)
        for i in data:
            save_icon = f'{minecraft_dir}/versions/{version_name}/saves/{i}/icon.png'
            icon = QIcon(save_icon) if os.path.exists(save_icon) else QIcon(default_icon)
            self.model_saves.appendRow(QStandardItem(icon, i))
        self.listView_saves.setModel(self.model_saves)

        # 资源包
        self.model_respacks = QStandardItemModel()
        data = manager.get_resourcepacks(minecraft_dir, version_name)
        for i in data:
            pack_icon = f'{minecraft_dir}/versions/{version_name}/resourcepacks/{i}/pack.png'
            icon = QIcon(pack_icon) if os.path.exists(pack_icon) else QIcon(default_icon)
            self.model_respacks.appendRow(QStandardItem(icon, i))
        self.listView_respacks.setModel(self.model_respacks)

        # Mod
        self.model_mods = QStandardItemModel()
        data = manager.get_mods(minecraft_dir, version_name)
        for i in data:
            self.model_mods.appendRow(QStandardItem(QIcon(default_icon), i))
        self.listView_mods.setModel(self.model_mods)

        # 光影
        self.model_shaderpacks = QStandardItemModel()
        data = manager.get_shaderpacks(minecraft_dir, version_name)
        for i in data:
            self.model_shaderpacks.appendRow(QStandardItem(QIcon(default_icon), i))
        self.listView_shaderpacks.setModel(self.model_shaderpacks)

    # ================= 拖拽事件 =================

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        minecraft_dir = self.lineEdit.text().replace('\\', '/')
        if minecraft_dir[-1] == '/':
            minecraft_dir = minecraft_dir[:-1]
        if not os.path.exists(minecraft_dir):
            return 1

        if self.comboBox_5.currentText() == '':
            return 1
        version_name = self.comboBox_5.currentText()
        saves_path = f'{minecraft_dir}/versions/{version_name}/saves'

        if not os.path.exists(saves_path):
            return 1
        pos = event.pos()
        widget_under_cursor = self.childAt(pos)
        while widget_under_cursor and widget_under_cursor.metaObject().className() == 'QWidget':
            widget_under_cursor = widget_under_cursor.parent()

        if not event.mimeData().hasUrls():
            event.ignore()

        elif widget_under_cursor.objectName() == 'listView_saves':
            files = [url.toLocalFile() for url in event.mimeData().urls()]
            for file in files:
                file = fpath(file)
                if os.path.isdir(file) and os.path.exists(file + '/level.dat'):
                    dirname = file.split('/')[-1]
                    shutil.copytree(file, saves_path + '/' + dirname)
                else:
                    try:
                        with z.ZipFile(file) as f:
                            dirname = '.'.join(file.split('.')[:-1]).split('/')[-1]
                            f.extractall(saves_path + '/' + dirname)
                            if not os.path.exists(saves_path + '/' + dirname + '/level.dat'):
                                QMessageBox.warning(None, 'Spectrum 启动器', '文件不是存档')
                                shutil.rmtree(saves_path + '/' + dirname)
                    except z.BadZipFile:
                        QMessageBox.warning(None, 'Spectrum 启动器', '文件不是有效存档 zip')

            event.accept()

        elif widget_under_cursor.objectName() == 'listView_respacks':
            files = [url.toLocalFile() for url in event.mimeData().urls()]
            for file in files:
                file = fpath(file)
                if os.path.isdir(file) and os.path.exists(file + '/pack.mcmeta'):
                    dirname = file.split('/')[-1]
                    shutil.copytree(file, saves_path + '/' + dirname)
                else:
                    try:
                        with z.ZipFile(file) as f:
                            dirname = '.'.join(file.split('.')[:-1]).split('/')[-1]
                            f.extractall(saves_path + '/' + dirname)
                            if not os.path.exists(saves_path + '/' + dirname + '/pack.mcmeta'):
                                QMessageBox.warning(None, 'Spectrum 启动器', '文件不是资源包')
                                shutil.rmtree(saves_path + '/' + dirname)
                    except z.BadZipFile:
                        QMessageBox.warning(None, 'Spectrum 启动器', '文件不是有效资源包 zip')

            event.accept()

    def page_process(self, page_index):
        if page_index == 2:
            self.setAcceptDrops(True)
        else:
            self.setAcceptDrops(False)
    # ================= 安装版本更新 =================
    def update_installed_versions(self):
        minecraft_dir = self.lineEdit.text().replace('\\', '/')
        if minecraft_dir == '':
            return 1
        if minecraft_dir[-1] == '/':
            minecraft_dir = minecraft_dir[:-1]
        if os.path.exists(minecraft_dir + '/versions'):
            versions = os.listdir(minecraft_dir + '/versions')

            self.comboBox_3.clear()
            for ver in versions:
                self.comboBox_3.addItem(ver)

            self.comboBox_5.clear()
            for ver in versions:
                self.comboBox_5.addItem(ver)

    # ================= 启动游戏 =================
    def launch(self):
        minecraft_dir = self.lineEdit.text().replace('\\', '/')
        if minecraft_dir[-1] == '/':
            minecraft_dir = minecraft_dir[:-1]
        if not os.path.exists(minecraft_dir):
            QMessageBox.critical(None, 'Spectrum 启动器', 'Minecraft路径不存在。')
            return 1

        if self.comboBox_3.currentText() == '':
            QMessageBox.critical(None, 'Spectrum 启动器', '你必须选择一个版本来启动。')
            return 1
        version_name = self.comboBox_3.currentText()

        java_major_version = launcher.get_required_java_version(minecraft_dir, version_name)
        if java_major_version == 21:
            javaw = self.lineEdit_4.text()
        elif java_major_version == 17:
            javaw = self.lineEdit_3.text()
        elif java_major_version == 8:
            javaw = self.lineEdit_2.text()
        else:
            javaw = self.lineEdit_8.text()

        xmx = self.comboBox_4.currentText()
        username = self.lineEdit_6.text()

        if len(username) > 16:
            QMessageBox.warning(None, 'Spectrum 启动器', '玩家名称长度>16，可能出现问题。')
        pattern = re.compile(r'[\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af\uff00-\uffef\s!\"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~]')
        if bool(pattern.search(username)):
            QMessageBox.warning(None, 'Spectrum 启动器', '玩家名称含有非法字符，可能出现问题。')

        if launcher.native() == 'windows':
            javawrapper = './JavaWrapper.jar'
            if not os.path.exists(javawrapper):
                QMessageBox.critical(None, 'Spectrum 启动器', 'JavaWrapper路径不存在。')
                return 1
        else:
            javawrapper = None

        cmd = launcher.launch(
            javaw=javaw,
            xmx=xmx,
            minecraft_dir=minecraft_dir,
            version_name=version_name,
            javawrapper=javawrapper,
            username=username,
            ms_login=self.using_mc_login,
            access_token=self.mc_token
        )

        with open('launch.bat', 'w') as f:
            f.write(cmd)

        if USE_OS_SYSTEM_TO_EXECUTE:
            os.system(cmd)
        else:
            self.minecraft_process = QProcess()
            self.minecraft_process.readyReadStandardOutput.connect(self.handle_minecraft_output)
            self.minecraft_process.readyReadStandardError.connect(self.handle_minecraft_error)
            self.minecraft_process.finished.connect(self.handle_minecraft_finished)

            if launcher.native() == 'windows':
                self.minecraft_process.start(app_path() + '/launch.bat')
            else:
                self.minecraft_process.start('bash', ['-c', cmd])

    def handle_minecraft_output(self):
        data = self.minecraft_process.readAllStandardOutput()
        stdout = bytes(data).decode("gbk", errors='ignore')
        print(f"Minecraft输出: {stdout}")

    def handle_minecraft_error(self):
        data = self.minecraft_process.readAllStandardError()
        stderr = bytes(data).decode("gbk", errors='ignore')
        print(f"Minecraft错误: {stderr}")

    def handle_minecraft_finished(self, exit_code, exit_status):
        print(f"Minecraft进程结束，退出码: {exit_code}")

    # ================= 下载版本 =================
    def download(self):
        if len(self.listView.selectionModel().selectedIndexes()) == 0:
            QMessageBox.critical(None, 'Spectrum 启动器', '你必须选择一个版本来下载。')
            return 1
        version = self.listView.selectionModel().selectedIndexes()[0].data()

        minecraft_dir = self.lineEdit.text().replace('\\', '/')
        if minecraft_dir[-1] == '/':
            minecraft_dir = minecraft_dir[:-1]
        if not os.path.exists(minecraft_dir):
            QMessageBox.critical(None, 'Spectrum 启动器', 'Minecraft路径不存在。')
            return 1

        version_name = self.lineEdit_7.text()
        os.makedirs(minecraft_dir + '/versions', exist_ok=True)
        if version_name in os.listdir(minecraft_dir + '/versions'):
            QMessageBox.critical(None, 'Spectrum 启动器', '已存在同名版本。')
            return 1

        modloader = self.comboBox.currentText().lower()
        if modloader == '无':
            modloader = 'vanilla'

        modloader_version = self.comboBox_2.currentText()
        if modloader_version == '' and modloader != 'vanilla':
            QMessageBox.critical(None, 'Spectrum 启动器', '请选择模组加载器版本。')
            return 1

        r = downloader.auto_download(
            minecraft_dir=minecraft_dir,
            version=version,
            version_name=version_name,
            modloader=modloader,
            modloader_version=modloader_version,
            progress_callback=self.progress_callback
        )
        if self.autodl_fabric_api:
            fabric.download_fabric_api(minecraft_dir, version, version_name)
        if r == 721:
            QMessageBox.warning(None, 'Spectrum 启动器', '下载的modloader与版本不兼容')
        self.update_installed_versions()

    def download_fix(self):
        if len(self.comboBox_3.currentText()) == 0:
            QMessageBox.critical(None, 'Spectrum 启动器', '请选择版本来补全。')
            return 1
        version_name = self.comboBox_3.currentText()

        minecraft_dir = self.lineEdit.text().replace('\\', '/')
        if minecraft_dir[-1] == '/':
            minecraft_dir = minecraft_dir[:-1]
        if not os.path.exists(minecraft_dir):
            QMessageBox.critical(None, 'Spectrum 启动器', 'Minecraft路径不存在。')
            return 1

        r = downloader.auto_download(
            minecraft_dir=minecraft_dir,
            version=launcher.get_minecraft_version(minecraft_dir, version_name),
            version_name=version_name,
            progress_callback=self.progress_callback
        )
        if r == 721:
            QMessageBox.warning(None, 'Spectrum 启动器', '下载的modloader与版本不兼容')
        self.update_installed_versions()

    def progress_callback(self, current, total, description):
        if description[1:-1].split('][')[0] == 'LIB':
            self.progressBar.setValue(int(current / total * 100))
        elif description[1:-1].split('][')[0] == 'AST':
            self.progressBar_2.setValue(int(current / total * 100))

    # ================= 配置管理 =================
    def load_config(self):
        cfg_path = app_path() + '/cfg.json'
        if os.path.exists(cfg_path):
            with open(cfg_path, 'r') as f:
                config = json.loads(f.read())
            self.lineEdit.setText(config['minecraftPath'])
            self.lineEdit_2.setText(config['java8'])
            self.lineEdit_3.setText(config['java17'])
            self.lineEdit_4.setText(config['java21'])
        else:
            self.lineEdit.setText('.minecraft')
            javas = java.find_javas()
            for java_exe in javas:
                java_ver = get_java_version(java_exe)[0]
                if java_ver == 21:
                    self.lineEdit_4.setText(java_exe)
                elif java_ver == 17:
                    self.lineEdit_3.setText(java_exe)
                elif java_ver == 8:
                    self.lineEdit_2.setText(java_exe)

    def save_config(self):
        jsonfile = {
            'minecraftPath': self.lineEdit.text(),
            'java8': self.lineEdit_2.text(),
            'java17': self.lineEdit_3.text(),
            'java21': self.lineEdit_4.text(),
            'wrapperPath': './JavaWrapper.jar'
        }
        with open(app_path() + '/cfg.json', 'w') as f:
            f.write(json.dumps(jsonfile))

    # ================= 版本列表更新 =================
    def update_version_list(self, state):
        current_list = downloader.get_version_list(
            self.checkBox_2.isChecked(),
            self.checkBox_3.isChecked(),
            self.checkBox_4.isChecked(),
            self.checkBox.isChecked()
        )
        self.model.setStringList(current_list)

    def update_ml_version_list(self, state):
        if len(self.listView.selectionModel().selectedIndexes()) == 0:
            return 0
        version = self.listView.selectionModel().selectedIndexes()[0].data()
        modloader = self.comboBox.currentText().lower()

        if modloader == 'forge':
            current_dict = forge.get_forge_version(version)
            current_list = [item["version"] for item in current_dict]
        elif modloader == 'fabric':
            current_list = fabric.get_fabric_versions()
        elif modloader == 'neoforge':
            current_dict = neoforge.get_neoforge_version(version)
            current_list = [item["version"] for item in current_dict]
        else:
            current_list = []

        self.comboBox_2.clear()
        for ver in current_list:
            self.comboBox_2.addItem(ver)

    # ================= 日志 =================
    def log(self, level, msg):
        try:
            if hasattr(self, "textBrowser"):
                self.textBrowser.append(f"[{level}] {msg}")
            else:
                print(f"[{level}] {msg}")
        except Exception as e:
            print(f"[LOG ERROR] {e}")
if __name__ == "__main__":
    # 如果缺少 JavaWrapper.jar，就自动下载
    if not os.path.exists(app_path() + '/JavaWrapper.jar'):
        download_javawrapper()

    # Qt 高分屏支持

    # =============== Python 插件加载 ===============
    app = QApplication(sys.argv)
    load_stylesheet(app, "style.qss")   # 应用外部主题
    MainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()

    loader = PluginLoader("plugins")
    loader.load_plugins()
    load_dll_plugins()
    # 进入 Qt 主循环
    sys.exit(app.exec_())

