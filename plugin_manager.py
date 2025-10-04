# plugin_manager.py
# -*- coding: utf-8 -*-
import sys, os, json, traceback, types
from pathlib import Path
import importlib.util

# 这里用到 loader_api 作为全局 API 提供者
import loader_api as api

PLUGINS_ROOT = Path(__file__).resolve().parent / "plugins"

class PluginInstance:
    def __init__(self, name, path, manifest):
        self.name = name
        self.path = path
        self.manifest = manifest
        self.module = None
        self.instance = None
        self.enabled = False

class PluginManager:
    def __init__(self, plugins_dir: Path = PLUGINS_ROOT):
        self.plugins_dir = plugins_dir
        self.plugins = {}
        self._discover()

    def _discover(self):
        """扫描 plugins/ 下的 manifest.json"""
        if not self.plugins_dir.exists():
            self.plugins_dir.mkdir(parents=True)
        for p in self.plugins_dir.iterdir():
            if not p.is_dir(): continue
            mf = p / "manifest.json"
            if mf.exists():
                try:
                    data = json.loads(mf.read_text(encoding="utf-8"))
                    name = data.get("name", p.name)
                    self.plugins[name] = PluginInstance(name, p, data)
                except Exception as e:
                    print(f"[PluginManager] manifest 解析失败 {mf}: {e}")

    def load_plugin(self, name: str):
        if name not in self.plugins:
            raise KeyError(f"未知插件 {name}")
        p = self.plugins[name]
        if p.enabled:
            return True
        entry = p.manifest.get("entry", "main.py")
        entry_path = p.path / entry
        if not entry_path.exists():
            print(f"[PluginManager] 插件 {name} 缺少入口文件 {entry}")
            return False
        try:
            spec = importlib.util.spec_from_file_location(f"plugin_{name}", str(entry_path))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)  # type: ignore
            p.module = module
            if hasattr(module, "MyPlugin"):
                p.instance = module.MyPlugin()
                if hasattr(p.instance, "on_enable"):
                    p.instance.on_enable()
            elif hasattr(module, "on_enable"):
                module.on_enable()
            p.enabled = True
            api.api_sysc_out_info(f"插件 {name} 已加载".encode("utf-8"))
            return True
        except Exception:
            traceback.print_exc()
            return False

    def unload_plugin(self, name: str):
        if name not in self.plugins: return False
        p = self.plugins[name]
        if not p.enabled: return True
        try:
            if p.instance and hasattr(p.instance, "on_disable"):
                p.instance.on_disable()
            elif p.module and hasattr(p.module, "on_disable"):
                p.module.on_disable()
        except Exception:
            traceback.print_exc()
        p.enabled = False
        api.api_sysc_out_warn(f"插件 {name} 已卸载".encode("utf-8"))
        return True

    def reload_plugin(self, name: str):
        self.unload_plugin(name)
        return self.load_plugin(name)

    def list_plugins(self):
        return {n: {"enabled": p.enabled, "path": str(p.path), "manifest": p.manifest}
                for n, p in self.plugins.items()}

    def load_all(self):
        for n in list(self.plugins.keys()):
            try: self.load_plugin(n)
            except Exception: traceback.print_exc()

    def unload_all(self):
        for n in list(self.plugins.keys()):
            try: self.unload_plugin(n)
            except Exception: traceback.print_exc()
