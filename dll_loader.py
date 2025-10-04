import os
import ctypes
import loader_bind_all

PLUGINS_DIR = os.path.join(os.path.dirname(__file__), "plugins")

loaded_plugins = []

def load_dll_plugins():
    if not os.path.exists(PLUGINS_DIR):
        print("[DLL Loader] plugins 目录不存在，跳过 DLL 插件加载")
        return

    for file in os.listdir(PLUGINS_DIR):
        if file.lower().endswith(".dll"):
            dll_path = os.path.join(PLUGINS_DIR, file)
            try:
                lib = ctypes.CDLL(dll_path)

                # 绑定 API
                loader_bind_all.bind_all(lib)

                # 获取插件入口
                create_plugin = lib.create_plugin
                create_plugin.restype = ctypes.c_void_p  # PluginBase*
                plugin_ptr = create_plugin()

                loaded_plugins.append((file, plugin_ptr))
                print(f"[DLL Loader] 成功加载 DLL 插件: {file}")

            except Exception as e:
                print(f"[DLL Loader] 加载 {file} 失败: {e}")

if __name__ == "__main__":
    load_dll_plugins()
