#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "spectrum_sdk.h"

// ========== UI ==========
static PyObject* sp_ui_add_button(PyObject* self, PyObject* args) {
    const char* text;
    if (!PyArg_ParseTuple(args, "s", &text)) return NULL;
    printf("[UI] 添加按钮: %s\n", text);
    Py_RETURN_NONE;
}

static PyObject* sp_ui_show_message(PyObject* self, PyObject* args) {
    const char* msg;
    if (!PyArg_ParseTuple(args, "s", &msg)) return NULL;
    printf("[UI] 消息: %s\n", msg);
    Py_RETURN_NONE;
}

// ========== Events ==========
static PyObject* sp_events_emit(PyObject* self, PyObject* args) {
    const char* name;
    if (!PyArg_ParseTuple(args, "s", &name)) return NULL;
    printf("[Event] 触发事件: %s\n", name);
    Py_RETURN_NONE;
}

// ========== FS ==========
static PyObject* sp_fs_exists(PyObject* self, PyObject* args) {
    const char* path;
    if (!PyArg_ParseTuple(args, "s", &path)) return NULL;
    int exists = access(path, 0) == 0;
    return PyBool_FromLong(exists);
}

// ========== Versions ==========
static PyObject* sp_versions_latest(PyObject* self, PyObject* args) {
    return PyUnicode_FromString("1.21.1"); // 假设返回最新版本
}

// ========== System ==========
static PyObject* sp_system_cpu_count(PyObject* self, PyObject* args) {
    return PyLong_FromLong(8); // 假设 8 核
}

// ========== Scheduler ==========
static PyObject* sp_scheduler_schedule(PyObject* self, PyObject* args) {
    const char* name;
    int delay;
    if (!PyArg_ParseTuple(args, "si", &name, &delay)) return NULL;
    printf("[Scheduler] 任务 %s 延迟 %d ms\n", name, delay);
    Py_RETURN_NONE;
}

// ========== Storage ==========
static PyObject* sp_storage_set(PyObject* self, PyObject* args) {
    const char* key; const char* val;
    if (!PyArg_ParseTuple(args, "ss", &key, &val)) return NULL;
    printf("[Storage] SET %s = %s\n", key, val);
    Py_RETURN_NONE;
}

// ========== SysC Out ==========
static PyObject* sp_sysc_out_log(PyObject* self, PyObject* args) {
    const char* msg;
    if (!PyArg_ParseTuple(args, "s", &msg)) return NULL;
    printf("[LOG] %s\n", msg);
    Py_RETURN_NONE;
}

// ========== 插件生命周期 ==========
static PyObject* sp_plugin_start(PyObject* self, PyObject* args) {
    printf("[Plugin] 启动\n");
    Py_RETURN_NONE;
}
static PyObject* sp_plugin_stop(PyObject* self, PyObject* args) {
    printf("[Plugin] 停止\n");
    Py_RETURN_NONE;
}

// ========== 方法表 ==========
static PyMethodDef SpectrumMethods[] = {
    {"ui_add_button", sp_ui_add_button, METH_VARARGS, "添加按钮"},
    {"ui_show_message", sp_ui_show_message, METH_VARARGS, "显示消息"},
    {"events_emit", sp_events_emit, METH_VARARGS, "触发事件"},
    {"fs_exists", sp_fs_exists, METH_VARARGS, "文件是否存在"},
    {"versions_latest", sp_versions_latest, METH_NOARGS, "获取最新版本"},
    {"system_cpu_count", sp_system_cpu_count, METH_NOARGS, "CPU 核心数"},
    {"scheduler_schedule", sp_scheduler_schedule, METH_VARARGS, "调度任务"},
    {"storage_set", sp_storage_set, METH_VARARGS, "存储 KV"},
    {"sysc_out_log", sp_sysc_out_log, METH_VARARGS, "日志输出"},
    {"plugin_start", sp_plugin_start, METH_NOARGS, "插件启动"},
    {"plugin_stop", sp_plugin_stop, METH_NOARGS, "插件停止"},
    {NULL, NULL, 0, NULL}
};

// ========== 模块定义 ==========
static struct PyModuleDef spectrummodule = {
    PyModuleDef_HEAD_INIT,
    "spectrum_plugin",
    "Spectrum C 扩展插件",
    -1,
    SpectrumMethods
};

// ========== 初始化 ==========
PyMODINIT_FUNC PyInit_spectrum_plugin(void) {
    return PyModule_Create(&spectrummodule);
}
