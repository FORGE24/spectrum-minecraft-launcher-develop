
---

# 总览：运行时架构

* 启动器是一个 **PyQt5 应用**（`MainWindow`），包含插件加载器：

  * **Python 插件**：在 `plugins/<插件名>/main.py` 中定义 `MyPlugin` 类（`on_enable/on_disable` 钩子）。由 `PluginLoader` 动态 import 并调用。
  * **DLL 插件（C/C++）**：由 `dll_loader.load_dll_plugins()` 通过 **ctypes** 加载指定的 DLL。首先用 `loader_bind_all.bind_all(lib)` 把 **Python 侧实现的 API** 以 **函数指针**的方式导出给 DLL；随后从 DLL 中查找 `create_plugin` 符号并取得插件对象，调用其 `start/stop/reload`。你日志里显示“已绑定 api_***”“成功加载 libSpectrumPlugin.dll”就是这一步在工作。

> 关键点：C/C++ 侧**不直接链接**任何实现库（MinGW 链接阶段不会报未解析符号），而是在**运行时**通过函数指针调用 Python 中的实现（见下文 ABI 约定）。

---

# API/ABI 约定（DLL 插件）

## 插件生命周期结构体与入口

**头文件 `spectrum_sdk.h` 的强约束（请以你的仓库中版本为准）**：

```c
// PluginBase 与 create_plugin 原型
typedef struct {
    void (*start)(void* launcher);   // 插件启动
    void (*stop)();                  // 插件关闭
    void (*reload)();                // 插件重载
} PluginBase;

EXPORT PluginBase* create_plugin();
```

（以上来自你上传的头文件定义）

* **必须导出** `create_plugin`（Windows 下推荐 `__declspec(dllexport)` + `extern "C"`）。
* `create_plugin()` **返回静态/全局** 的 `PluginBase` 实例地址，插件停止后仍应有效，**不要返回栈对象**。
* `start(void* launcher)` 的 `launcher` 是宿主窗体指针（仅占位），目前无需在 C 层解引用它；**涉及 UI 的操作请用 API 函数**（见“10. UI”）。

## 函数指针型 API（由 Python 侧注入）

在 `spectrum_sdk.h` 中，大部分 API 被声明为**函数指针**变量（而不是普通函数），例如日志、存储、调度、系统信息、版本管理、网络、文件系统、事件、玩家、UI、工具等模块：

```c
// 示例：日志
extern void (*api_sysc_out_info)(const char* msg);
extern void (*api_sysc_out_warn)(const char* msg);
// ... 略

// 示例：调度
typedef void (*task_func)();
extern void (*api_scheduler_schedule)(const char* name, task_func func);
extern void (*api_scheduler_schedule_repeat)(const char* name, int interval_ms, task_func func);
// ... 略

// 示例：UI
extern void (*api_ui_add_button)(const char* label, task_func func);
extern int  (*api_ui_confirm)(const char* msg);
// ... 略
```

这些指针在 DLL 被加载时，由 Python 的 `loader_bind_all.bind_all(lib)` 按 **ctypes 原型**逐个赋值完成（你日志中的“[bind_all] 已绑定 ...”即完成注入）。

> 因此：**在调用任何 `api_***` 之前，不需要你做额外初始化**；只要 DLL 被 `dll_loader` 成功加载，指针就已经有效。

## 字符串/数组/回调的内存与编码规范

* **编码**：所有 `const char*` **使用 UTF-8**（Python 侧统一 `.decode()`/`.encode('utf-8')`）。
* **返回的字符串与字符串数组**：

  * 例如 `api_fs_read(path) -> const char*`、`api_versions_all(int* count) -> const char**`。
  * **内存属于 Python**（由 ctypes/py 分配），**C 侧请“立刻拷贝”再使用**。不要在 C 里长期持有这些指针（避免悬垂/GC 移动）。
* **字符串数组的计数**：形如 `foo(..., int* count)`，Python 侧会把 `count[0]` 设为长度，并返回 `const char**`；你需要遍历 `i in [0..count-1]`。这是 `api_storage_keys`、`api_system_process_list`、`api_fs_list_dir` 等 API 的返回约定（Python 侧构建了 `ctypes.c_char_p * count` 的数组）。
* **回调**：

  * `task_func` = `void (*)()`，比如 `api_ui_add_button("Hi", on_click)`；你传入的 `on_click` **必须是全局/静态函数**或生存期覆盖插件全程的函数指针。
  * 事件/观察者回调同理：`void (*)(const char* data)` 形态的回调也由 Python 线程触发（见 scheduler/observer/event）。

## 线程模型与 UI 说明

* Python 侧的**调度器**使用 `threading.Timer` 或子线程，所以**你的回调可能在非 GUI 线程**上被调用。
* PyQt GUI 理论上要在主线程操作，但 Python 实现里直接调用了 `QMessageBox`、`QPushButton` 添加等（`api_ui_***`），在你的现有工程中**它们已在实践中可用**。谨慎起见：

  * **尽量把 UI 操作都通过 `api_ui_*` 完成**，而不要在 C 插件里调用 Qt。
  * 长耗时工作放到 `api_scheduler_schedule_repeat`/`api_util_thread` 等后台执行，UI 用 `api_ui_notify`/`api_sysc_out_*` 汇报。

---

# Python 插件开发

## 目录与入口

* 位置：`plugins/<你的插件名>/main.py`
* 入口类：定义 `MyPlugin`，包含 `on_enable(self)` 与可选的 `on_disable(self)`。

### Python 插件最小示例

```python
# plugins/hello_py/main.py
import loader_api as api

class MyPlugin:
    def on_enable(self):
        api.api_sysc_out_info(b"[HelloPy] on_enable")
        # 加一个按钮
        def on_click():
            api.api_ui_show_message(b"Hello from Python plugin!")
        api.api_ui_add_button(b"HelloPy Button", api.task_func(on_click))

    def on_disable(self):
        api.api_sysc_out_info(b"[HelloPy] on_disable")
```

> 说明：`loader_api.py` 中每个导出函数都收/返 **bytes**（UTF-8），而不是 `str`；如果你传 `str`，请 `.encode()`。日志/存储/网络/文件/事件/玩家/UI/工具函数都在 `loader_api.py` 内实现。

---

# C 插件开发

## 头文件

请包含仓库中的 `spectrum_sdk.h`（当前版本含函数指针声明）。核心定义见上文（结构体与函数指针声明）。

## 最小示例（Hello 按钮）

```c
// main.c
#include "spectrum_sdk.h"
#include <stdio.h>

// 点击按钮
static void on_button_click() {
    api_ui_show_message("Hello from Spectrum C Plugin!");
}

// 启动
static void plugin_start(void* launcher) {
    api_sysc_out_info("[CPlugin] start");
    api_ui_add_button("CPlugin Button", on_button_click);
}

// 停止/重载
static void plugin_stop()   { api_sysc_out_info("[CPlugin] stop");   }
static void plugin_reload() { api_sysc_out_info("[CPlugin] reload"); }

// 插件对象（静态/全局）
static PluginBase plugin = {
    .start  = plugin_start,
    .stop   = plugin_stop,
    .reload = plugin_reload,
};

// 必须导出
#ifdef __cplusplus
extern "C"
#endif
EXPORT PluginBase* create_plugin() {
    return &plugin;
}
```

> 这份最小例子与你仓库中的示例实现一致（按钮/日志）——见你上传的 `main.c`。

### 使用存储/调度/事件的示例（进阶）

```c
#include "spectrum_sdk.h"
#include <string.h>

static void tick() {
    api_sysc_out_debug("[CPlugin] tick");
    // 读一个键
    const char* v = api_storage_get("demo", "counter");
    int n = v && *v ? atoi(v) : 0;
    char buf[32]; sprintf(buf, "%d", n+1);
    api_storage_set("demo","counter", buf);
}

static void on_button_click() {
    // 广播事件（字符串数据）
    api_events_fire("hello_event", "from_c_plugin");
}

static void plugin_start(void* _) {
    api_storage_set("demo", "counter", "0");
    api_ui_add_button("EmitEvent", on_button_click);
    api_scheduler_schedule_repeat("tick", 2000, tick); // 2s一次
}
static void plugin_stop(){ api_scheduler_cancel("tick"); }
static void plugin_reload(){ api_sysc_out_info("[CPlugin] reload"); }

static PluginBase plugin = { plugin_start, plugin_stop, plugin_reload };
EXPORT PluginBase* create_plugin(){ return &plugin; }
```

---

# C++ 插件开发

**要点**：用 `extern "C"` 防止 C++ 名字改编；其余与 C 一致。

```cpp
// main.cpp
#include "spectrum_sdk.h"

static void on_button_click() {
    api_ui_show_message("Hello from C++ Plugin!");
}

static void start(void*) { api_ui_add_button("CXX Button", on_button_click); }
static void stop() {}
static void reload() {}

static PluginBase plugin { start, stop, reload };

extern "C" EXPORT PluginBase* create_plugin() { return &plugin; }
```

---

# CMake 构建（Windows/MinGW）

最小 CMake（生成 `libSpectrumPlugin.dll`）：

```cmake
cmake_minimum_required(VERSION 3.16)
project(SpectrumPlugin C)

set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON) # 保险起见
set(CMAKE_C_STANDARD 11)
add_library(SpectrumPlugin SHARED
    main.c
    spectrum_sdk.c   # <<< 若你使用了函数指针变量的定义文件
)
target_include_directories(SpectrumPlugin PRIVATE ${CMAKE_SOURCE_DIR})

# 可选：减少不必要依赖
if(MINGW)
  target_link_libraries(SpectrumPlugin PRIVATE
    kernel32 user32 gdi32 winspool shell32 ole32 oleaut32 uuid comdlg32 advapi32)
endif()
```

> 你的仓库里已经有 `spectrum_sdk.c` **定义了所有函数指针变量**（把 `extern` 的变量真正放到一个 TU 里），需要把它加入到目标里一起编译，否则会出现多重定义/未定义问题。

* 产物名一般为 `libSpectrumPlugin.dll`（MinGW 带 `lib` 前缀属正常）。
* 将 DLL 放到 **启动器可执行的工作目录**（你日志中正是从当前目录加载）。常见做法是丢在项目根与 `main.py` 同级。

---

# 常用 API 清单与示例

> **以下签名均来自你的头文件/实现，按模块罗列。**实际以你当前提交为准。

## 1) 日志（部分）

```c
void (*api_sysc_out_info)(const char* msg);
void (*api_sysc_out_warn)(const char* msg);
void (*api_sysc_out_printf)(const char* fmt, ...);
```

* 用法：`api_sysc_out_info("hello");`
* 说明：在 UI 的日志面板输出（Python 侧实现）。

## 2) 存储（KV）

```c
void         (*api_storage_set)(const char* ns,const char* key,const char* value);
const char*  (*api_storage_get)(const char* ns,const char* key);
const char** (*api_storage_keys)(const char* ns, int* count);
```

* 注意：**返回值内存属于 Python**，C 侧要自行拷贝。`keys` 遍历要用 `count`。

## 3) 调度（定时/重复任务）

```c
typedef void (*task_func)();
void (*api_scheduler_schedule)(const char* name, task_func func);
void (*api_scheduler_schedule_repeat)(const char* name, int interval_ms, task_func func);
void (*api_scheduler_cancel)(const char* name);
```

* 示例：`api_scheduler_schedule_repeat("tick", 1000, on_tick);`
* 注意：**task_func 无参数**；若需状态，请用静态全局或自行管理。

## 4) 系统信息（部分）

```c
const char* (*api_system_os_name)();
int         (*api_system_cpu_count)();
const char* (*api_system_gpu_info)();
```

* 由 Python (psutil/GPUtil) 提供。

## 5) 版本管理（部分）

```c
const char** (*api_versions_all)(int* count);
const char*  (*api_versions_latest)();
int          (*api_versions_download)(const char* version);
```

* 示例：列出全部版本 -> 过滤 -> 下载。

## 6) 网络（部分）

```c
const char* (*api_net_http_get)(const char* url);
int         (*api_net_download)(const char* url, const char* path);
int         (*api_net_ping)(const char* host);
```

* 说明：底层用 `requests`、`subprocess ping`，请传 UTF-8 URL/主机名。

## 7) 文件系统（部分）

```c
const char*  (*api_fs_read)(const char* path);
int          (*api_fs_write)(const char* path, const char* content);
const char** (*api_fs_list_dir)(const char* path, int* count);
```

* `read` 返回文件内容（UTF-8），`list_dir` 返回文件名数组。

## 8) 事件（部分）

```c
typedef void (*consumer_func)(const char* v);
void (*api_events_register)(const char* event, consumer_func handler);
void (*api_events_fire)(const char* event, const char* data);
```

* 例：`api_events_register("hello_event", on_evt); api_events_fire("hello_event","data");`

## 9) 玩家（部分）

```c
int  (*api_player_login)(const char* username, const char* password);
void (*api_player_broadcast)(const char* msg);
```

* Python 侧是一个内存模拟（演示/测试），可用于 UI 演示。

## 10) UI（部分）

```c
void (*api_ui_show_message)(const char* msg);
void (*api_ui_add_button)(const char* label, task_func func);
int  (*api_ui_confirm)(const char* msg);
```

* 直接弹框、添加按钮到主界面（PyQt）。

## 11) 工具（部分）

```c
int         (*api_util_random_int)(int a, int b);
const char* (*api_util_now_iso)();
int         (*api_util_benchmark)(task_func func);
```

* `benchmark` 会在 Python 侧测量 `func` 耗时（ms）。

---

# 放置与运行

1. 构建得到 `libSpectrumPlugin.dll`（或 `SpectrumPlugin.dll`）。
2. 放到启动器根目录（与 `main.py` 同级），或 `dll_loader` 扫描的目录（你的当前日志显示从**工作目录**加载）。
3. 运行 `main.py`，日志应出现：

```
[bind_all] 已绑定 ...
[DLL Loader] 成功加载 DLL 插件: libSpectrumPlugin.dll
```

随后你在 UI 会看到通过 `api_ui_add_button` 新增的按钮，或者在日志里看到 `api_sysc_out_info` 打印。

---

# 常见坑位与排查

* **“function 'create_plugin' not found”**

  * 是否导出符号（MSVC 需 `extern "C"`/导出；MinGW 一般 OK）。
  * DLL 是否放在可扫描目录，名称是否正确。
* **TypeError: invalid result type for callback function**（Python 侧绑定）

  * 回调签名与 `ctypes.CFUNCTYPE` 不匹配，或 Python 返回类型不对。比如 `api_storage_keys` **必须返回** “`POINTER(c_char_p)` 指向的数组”，并正确设置 `count[0]`（这个问题你之前已经修好）。
* **构建阶段“未定义/多重定义”**

  * 你若采用了将 `api_*` 声明为指针变量（`extern void (*api_xxx)();`），**务必把它们的“定义”文件 `spectrum_sdk.c` 一并编进 DLL**。
* **UI 没变化**

  * 请确保在 `start()` 中调用了 `api_ui_add_button`/`api_ui_notify` 等可视 API，并确认 DLL 被成功加载（看日志）。

---

# 一键可用的示例打包

### `main.c`（按钮 + 定时器 + 存储 + 事件）

```c
#include "spectrum_sdk.h"
#include <stdio.h>

static void on_timer() {
    const char* v = api_storage_get("demo","ticks");
    int n = (v && *v) ? atoi(v) : 0;
    char buf[32]; sprintf(buf, "%d", ++n);
    api_storage_set("demo","ticks", buf);
    api_sysc_out_debug("[CPlugin] tick");
}

static void on_button() {
    api_ui_show_message("Hello from DLL!");
    api_events_fire("dll.clicked", "btn");
}

static void start(void* _) {
    api_sysc_out_info("[CPlugin] start");
    api_storage_set("demo","ticks","0");
    api_ui_add_button("DLL Button", on_button);
    api_scheduler_schedule_repeat("dll.timer", 3000, on_timer);
}

static void stop() {
    api_scheduler_cancel("dll.timer");
    api_sysc_out_info("[CPlugin] stop");
}
static void reload() { api_sysc_out_info("[CPlugin] reload"); }

static PluginBase plugin = { start, stop, reload };
#ifdef __cplusplus
extern "C"
#endif
EXPORT PluginBase* create_plugin(){ return &plugin; }
```

> 这个版本在你的现有框架中即可直接表现“有按钮、有定时日志、有存储”的可见效果。

### `CMakeLists.txt`

```cmake
cmake_minimum_required(VERSION 3.16)
project(SpectrumPlugin C)
set(CMAKE_C_STANDARD 11)

add_library(SpectrumPlugin SHARED
  main.c
  spectrum_sdk.c  # 定义函数指针变量
)
target_include_directories(SpectrumPlugin PRIVATE ${CMAKE_SOURCE_DIR})
if(MINGW)
  target_link_libraries(SpectrumPlugin PRIVATE
    kernel32 user32 gdi32 winspool shell32 ole32 oleaut32 uuid comdlg32 advapi32)
endif()
```

---

# Python 端“看得见的效果”建议

若你希望更明显的可见效果，可以在 DLL 插件 `start()` 里调用：

```c
api_ui_notify("DLL Loaded", "已成功注入按钮与定时任务");
```

或：

```c
// 实时输出到日志面板
api_sysc_out_info("[CPlugin] 已注入 UI 与任务");
```

二者都会立刻在 UI 上给出反馈（消息框/日志）。


