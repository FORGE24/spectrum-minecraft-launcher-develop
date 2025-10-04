cmake_minimum_required(VERSION 3.10)
project(SpectrumPlugin C)

set(CMAKE_C_STANDARD 11)

# 插件源码
set(SOURCES
        main.c
        spectrum_sdk.c
)

# 生成 DLL (Windows) 或 .so (Linux)
add_library(SpectrumPlugin SHARED ${SOURCES})

# 头文件路径
target_include_directories(SpectrumPlugin PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

# Windows 下 DLL 名称不要自动加 "lib" 前缀
if (WIN32)
    set_target_properties(SpectrumPlugin PROPERTIES PREFIX "")
endif()
