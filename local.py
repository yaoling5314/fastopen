import os
import json
from parseConfig import parseConfig
from mqtt_connect import mqtt_connect


def send_result(data):
    """
    将执行结果 (成功/错误) 发布回 MQTT 主题。
    """
    config = parseConfig()
    config.get_mqtt_config()

    send = mqtt_connect()
    status = send.publish(config.get_mqtt_server(),
                          config.get_mqtt_port(),
                          config.get_mqtt_keepalive_sec(),
                          config.get_mqtt_client_id(),
                          config.get_mqtt_topic() + 'local',
                          data)
    if status != 0:
        print("send error")


def callback(client, topic, data):
    """
    处理传入的 MQTT 消息，执行命令并报告状态。
    """
    print(f"Received: {data}")
    try:
        json_data = json.loads(data)
        execute = json_data.get("execute", [])

        success = True
        for exe in execute:
            # 清理命令字符串（去除首尾空格）
            cmd = exe.strip()

            # 针对 Windows 系统优化路径分隔符（将其转换为反斜杠）
            # 特殊情况：如果是 adb 命令，则保留原样（adb 自带处理或需要特定格式）
            if not cmd.startswith('adb'):
                cmd = cmd.replace('/', '\\')

            print(f"Executing: {cmd}")
            result = os.system(cmd)
            if result != 0:
                send_result(f"error: {exe}")
                success = False
                break

        if success:
            send_result("success")
    except Exception as e:
        print(f"Error: {e}")
        send_result(f"exception: {str(e)}")


def main():
    """
    初始化 MQTT 订阅者并开始监听命令。
    """
    config = parseConfig()
    config.get_mqtt_config()
    print("FastOpen Local Listener Started*****")

    rcv = mqtt_connect()
    rcv.subscribe(config.get_mqtt_server(),
                  config.get_mqtt_port(),
                  config.get_mqtt_keepalive_sec(),
                  config.get_mqtt_client_id(),
                  config.get_mqtt_topic(),
                  callback)


if __name__ == "__main__":
    main()
