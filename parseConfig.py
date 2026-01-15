#!/usr/bin/env python3
#coding=utf-8

import os
import json
import random
import sys
import socket
import getpass

class parseConfig:
    """
    解析 'config.json' 配置并处理路径映射逻辑。
    """
    def __init__(self):
        self.__mqtt_config = {}
        self.__config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
        self.__server_path = {}
        self.__local_path = {}
        self.__server_ip = ''
        self.__server_username = ''
        self.__commend = {}

    def get_mqtt_config(self):
        """
        从 config.json 加载 MQTT 连接设置。
        """
        with open(self.__config_path, 'r') as f:
            param = json.load(f)
            mc = param["MQTT config"]
            self.__mqtt_config["Server"] = mc["Server"]
            self.__mqtt_config["Port"] = int(mc["Port"])
            self.__mqtt_config["KeepAliveSeconed"] = int(mc["KeepAliveSeconed"])
            self.__mqtt_config["Topic"] = mc["Topic"]

    def get_mqtt_server(self):
        return self.__mqtt_config.get("Server")

    def get_mqtt_port(self):
        return self.__mqtt_config.get("Port")

    def get_mqtt_keepalive_sec(self):
        return self.__mqtt_config.get("KeepAliveSeconed")

    def get_mqtt_topic(self):
        return self.__mqtt_config.get("Topic")

    def get_mqtt_client_id(self):
        return f"mqtt-{random.randint(0, 1000)}"

    def get_host_ip(self):
        """
        确定本机 IP 地址和当前用户名。用于路径映射的自动配置。
        """
        user_name = getpass.getuser()
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        except Exception:
            ip = "127.0.0.1"
        finally:
            s.close()
        return ip, user_name

    def parse_server_config(self):
        r"""
        解析服务器到本地的路径映射。如果映射为空，则应用默认逻辑：
        Server: /home/username/
        Local: \\IP\username\
        """
        self.__server_ip, self.__server_username = self.get_host_ip()
        self.__server_path.clear()
        self.__local_path.clear()
        count = 0
        with open(self.__config_path, 'r') as f:
            param = json.load(f)
            for p in param["server config"]:
                # 移除严格的 IP 检查，以允许配置优先并处理 IP 检测可能出现的错误。
                # 只要 config.json 中有配置，就应该尝试加载。
                # if p["IP"] == self.__server_ip or not p["IP"]:

                server_path = p["server"] if p["server"] else f"/home/{self.__server_username}/"

                # 如果 local 路径为空，则默认使用 UNC 路径格式：\\ConfigIP\User\ 或 \\DetectedIP\User\
                # 优先使用配置中的 IP，如果没有配置则回退到检测到的本机 IP。
                use_ip = p["IP"] if p["IP"] else self.__server_ip
                local_path = p["local"] if p["local"] else f"\\\\{use_ip}\\{self.__server_username}\\"

                self.__server_path[count] = server_path
                self.__local_path[count] = local_path
                count += 1

    def get_server_count(self):
        return len(self.__server_path)

    def get_server_path(self, index):
        return self.__server_path.get(index)

    def get_local_path(self, index):
        return self.__local_path.get(index)

    def parse_cmd_config(self):
        """
        从 config.json 加载命令定义。
        """
        with open(self.__config_path, 'r') as f:
            param = json.load(f)
            self.__commend.clear()
            for p in param["command"]:
                self.__commend[p["name"]] = p["execute"]

    def get_cmd_name_all(self):
        return list(self.__commend.keys())

    def get_cmd_execute(self, name):
        return self.__commend.get(name)
