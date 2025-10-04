#include "spectrum_sdk.h"
#include <stdlib.h>

// 按钮点击事件
void on_button_click(void* userdata) {
    api_sysc_out_info("DLL 插件按钮被点击！");
    api_ui_show_message("来自 DLL 插件的提示：按钮被点了！");
}

// 插件启动时调用
void plugin_start(void* launcher) {
    api_sysc_out_info("[SpectrumPlugin] 插件启动！");
    api_ui_add_button("点我测试DLL插件", on_button_click);
}

// 插件停止时调用
void plugin_stop() {
    api_sysc_out_info("[SpectrumPlugin] 插件停止！");
}

// 插件重载时调用
void plugin_reload() {
    api_sysc_out_info("[SpectrumPlugin] 插件重载！");
}

// 导出 create_plugin
EXPORT PluginBase* create_plugin() {
    static PluginBase plugin = {
            .start  = plugin_start,
            .stop   = plugin_stop,
            .reload = plugin_reload
    };
    return &plugin;
}
