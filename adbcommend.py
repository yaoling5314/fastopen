#!/usr/bin/env python3
#coding=utf-8

import os


def push(path):
    """
    根据标准 Android 目录结构 (system, vendor, product 等) 智能推断 'adb push' 命令的目标路径。
    如果已提供目标路径，则返回原始命令。
    """
    # path 预期为完整的命令行字符串，例如 'adb push /path/to/local/file'
    cmd_parts = path.strip().split()

    # 验证：确保这是一个 adb push 命令
    if len(cmd_parts) < 3:
        return path

    if cmd_parts[0] != 'adb' or cmd_parts[1] != 'push':
        return path

    local_path = cmd_parts[2]

    # 如果已经由于提供了目标路径，则直接返回原命令
    if len(cmd_parts) > 3:
        return path

    # 基于 Android 源码树结构自动计算目标路径
    src = local_path.replace('\\', '/')
    dest = ""

    dest = ""

    # 尝试在路径中查找标准的 Android 分区
    # 如果路径存在嵌套，优先顺序很重要
    partitions = ["/system/", "/system_ext/", "/vendor/", "/product/", "/data/", "/apex/", "/odm/", "/oem/"]

    for partition in partitions:
        idx = src.rfind(partition)
        if idx != -1:
            dest = src[idx:]
            break

    if dest:
        return f"{path.strip()} {dest}"

    return path
