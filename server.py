import os
import json
import sys
import argparse
from parseConfig import parseConfig
from mqtt_connect import mqtt_connect
import adbcommend


def server_install():
    """
    生成 'open.sh' 脚本并打印 alias 命令。
    此脚本用于辅助在 Linux shell 中执行 FastOpen 命令。
    """
    config = parseConfig()
    config.parse_cmd_config()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    shell_name = os.path.join(current_dir, 'open.sh')
    run_name = os.path.abspath(__file__)
    alias = ''

    # 写入 open.sh 脚本
    with open(shell_name, 'w') as f:
        f.writelines('#!/bin/bash\n')
        f.writelines('FILE=$2\n')  # 直接传递路径；由 Python 脚本内部处理绝对/相对路径逻辑

        commands = config.get_cmd_name_all()
        for cmd in commands:
            execute = config.get_cmd_execute(cmd)
            if not execute:
                continue

            file_flag = ''
            param_flag = ''
            base_flag = '$2'

            execute_items = execute if isinstance(execute, list) else [execute]
            has_file = any('{file}' in item for item in execute_items)
            has_param = any('{param}' in item for item in execute_items)

            if has_file:
                file_flag = '-f "$FILE" '
                base_flag = ''
            if has_param:
                param_flag = f'-p {base_flag} "$3" "$4" "$5" "$6"'

            f.writelines(f'if [ "$1" = "{cmd}" ]; then\n')
            f.writelines(f'    python3 {run_name} -c {cmd} {file_flag} {param_flag}\n')
            f.writelines(f'fi\n')

            alias += f"alias {cmd}='{shell_name} {cmd} '\n"
    print(alias)


def usage():
    """
    解析命令行参数。
    """
    config = parseConfig()
    config.parse_cmd_config()
    commands = config.get_cmd_name_all()

    parser = argparse.ArgumentParser(description='linux server to win')
    parser.add_argument('-c', '--commend', dest='commend', type=str, required=True,
                        help=f'command must be one of: ServerInstall, {commands}')
    parser.add_argument('-f', '--file', dest='file_path', type=str, help='file path')
    parser.add_argument('-p', dest='param', type=str, nargs='+', help='param')

    return parser.parse_args()


def callback(client, topic, data):
    """
    MQTT 回调函数，用于接收来自本地 (Windows) 客户端的响应。
    """
    print(data)
    client.disconnect()


def send_commend(commend, data):
    """
    通过 MQTT 发送格式化后的命令到 Windows 客户端。
    """
    print(f"Sending command: {commend}")
    config = parseConfig()
    config.get_mqtt_config()

    send = mqtt_connect()
    status = send.publish(config.get_mqtt_server(),
                          config.get_mqtt_port(),
                          config.get_mqtt_keepalive_sec(),
                          config.get_mqtt_client_id(),
                          config.get_mqtt_topic(),
                          data)
    if status != 0:
        print("send error")
        return

    rcv = mqtt_connect()
    rcv.subscribe(config.get_mqtt_server(),
                  config.get_mqtt_port(),
                  config.get_mqtt_keepalive_sec(),
                  config.get_mqtt_client_id(),
                  config.get_mqtt_topic() + 'local',
                  callback)


def path_back_previous(path):
    """
    将路径分隔符规范化为正斜杠。
    """
    # 使用 normpath 解析路径中的 `..` 等相对符号，并确保统一使用正斜杠
    norm = os.path.normpath(path)
    return norm.replace('\\', '/')


def server_path_to_local(path):
    """
    将 Linux 服务器路径映射到对应的 Windows 本地路径 (UNC 或盘符)。
    """
    parse_config = parseConfig()
    parse_config.parse_server_config()

    # 标准化输入路径以确保符合标准的 Linux 格式，便于后续匹配。
    # 即使之前包含反斜杠，为了统一匹配逻辑，先全部转为正斜杠。
    path_norm = path.replace('\\', '/')

    for i in range(parse_config.get_server_count()):
        server_path = parse_config.get_server_path(i)
        local_path = parse_config.get_local_path(i)

        if not server_path or not local_path:
            continue

        # 标准化服务器路径以进行一致性匹配 (统一去除末尾斜杠)
        server_path_norm = server_path.replace('\\', '/').rstrip('/')
        local_path_clean = local_path.rstrip('\\').rstrip('/')

        # 确定本地路径是否需要 Windows 风格 (盘符或 UNC)
        is_win_target = ':' in local_path_clean or local_path_clean.startswith('//') or local_path_clean.startswith('\\\\')

        # 使用循环查找所有匹配项并进行替换
        # 注意：为了避免无限循环，我们在替换后继续搜索剩余部分
        # 但由于我们修改了字符串，最好使用 while 循环重新查找

        search_idx = 0
        while True:
            # 在当前路径字符串中查找服务器路径
            # 必须匹配完整路径段的前缀 (例如 /home/user 匹配 /home/user/file，但不匹配 /home/username)
            # 我们查找 server_path_norm，并检查它的下一个字符是否是 / 或 空格 或 结束

            idx = path_norm.find(server_path_norm, search_idx)
            if idx == -1:
                break

            # 验证匹配边界：
            # 1. 前面必须是字符串开头或空格 (或者是 quote? 暂时假设空格分隔)
            if idx > 0 and path_norm[idx-1] != ' ':
                 search_idx = idx + 1
                 continue

            # 2. 后面必须是 '/' (子目录) 或 ' ' (路径结束) 或 字符串结束
            end_of_match = idx + len(server_path_norm)
            if end_of_match < len(path_norm):
                char_after = path_norm[end_of_match]
                if char_after not in ('/', ' '):
                    search_idx = idx + 1
                    continue

            # 找到合法的路径前缀匹配！
            # 现在我们需要找到这个完整路径 Token 的结束位置 (下一个空格或结束)
            token_end = path_norm.find(' ', end_of_match)
            if token_end == -1:
                token_end = len(path_norm)

            # 提取相对路径部分
            # full_token: /home/quwj/work/file.txt
            # server_path_norm: /home/quwj
            # relative_part: /work/file.txt
            full_token = path_norm[idx:token_end]
            relative_part = full_token[len(server_path_norm):]

            # 构建新的本地路径 Token
            new_token = local_path_clean + relative_part

            # 如果是 Windows 目标，只转换这个 Token 内部的分隔符
            if is_win_target:
                new_token = new_token.replace('/', '\\')

            # 执行替换 (只替换当前找到的这个 Token)
            path_norm = path_norm[:idx] + new_token + path_norm[token_end:]

            # 更新搜索索引，继续查找下一个 (跳过刚刚替换的部分)
            search_idx = idx + len(new_token)

    return path_norm


def format_execute(args, indata):
    """
    通过替换占位符为实际值并执行路径映射来格式化执行字符串。
    """
    inparam = " ".join(args.param) if args.param else ""
    file_path = args.file_path if args.file_path else ""

    # 解析 Linux 路径 (处理 ~, ., 以及相对路径)
    if file_path:
        file_path = os.path.expanduser(file_path)
        file_path = os.path.abspath(file_path)

    # 替换 {file} 和 {param} 占位符
    indata = indata.format(file=file_path, param=inparam)

    # 如果存在 'OUT' 环境变量，则进行替换处理
    out_env = os.getenv('OUT')
    if out_env:
        indata = indata.replace("OUT", out_env)

    path = path_back_previous(indata)

    # 特殊处理 'adb push' 命令，自动推断 Android 目标路径
    if 'adb push' in path and not inparam:
        path = adbcommend.push(path)

    mapped_path = server_path_to_local(path)
    print(f"Executing Mapping: {path} -> {mapped_path}")
    return mapped_path


def commend_encode(commend_name, args):
    """
    将命令及其参数编码为 JSON 字符串以便通过 MQTT 传输。
    """
    parse_config = parseConfig()
    parse_config.parse_cmd_config()
    execute = parse_config.get_cmd_execute(commend_name)

    if execute is None:
        print(f'Error: command "{commend_name}" not found in config.json')
        sys.exit(2)

    json_array = []
    execute_list = execute if isinstance(execute, list) else [execute]
    for item in execute_list:
        json_array.append(format_execute(args, item))

    return json.dumps({"commend": commend_name, "execute": json_array}, indent=4)


def main():
    args = usage()
    if args.commend == 'ServerInstall':
        server_install()
    else:
        send_str = commend_encode(args.commend, args)
        send_commend(args.commend, send_str)


if __name__ == "__main__":
    main()
