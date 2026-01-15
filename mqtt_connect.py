import time
from paho.mqtt import client as mqtt_client


class mqtt_connect:
    """
    Paho MQTT 客户端的封装类，用于处理发布和订阅。
    """
    def __init__(self):
        self.__server = None
        self.__port = None
        self.__keepalive = None
        self.__id = None
        self.__topic = None
        self.__callback = None
        self.__connect_status = 0
        self.__is_disconnected = False

    def connect(self, server, port, keepalive, client_id):
        """
        建立 MQTT 客户端配置 (连接在循环中进行)。
        """
        client = mqtt_client.Client(client_id)
        client.connect(server, port, keepalive)
        return client

    def publish(self, server, port, keepalive, client_id, topic, param):
        """
        向指定主题发布消息。
        - 连接到代理
        - 发布消息
        - 断开连接
        """
        if not param:
            return -1

        self.__connect_status = 0

        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                self.__connect_status = 1
            else:
                print(f"Failed to connect for publish, return code {rc}")

        client = self.connect(server, port, keepalive, client_id)
        client.on_connect = on_connect
        client.loop(1)  # 短暂处理网络事件以捕获 on_connect 回调

        if self.__connect_status == 0:
            # 如果初始循环未捕获，则再尝试一次
            time.sleep(0.1)
            client.loop(0.1)

        result = client.publish(topic, param, qos=0, retain=False)
        if result[0] != 0:
            print(f"Failed to send message to topic {topic}")

        client.disconnect()
        return result[0]

    def subscribe(self, server, port, keepalive, client_id, topic, callback):
        """
        订阅主题并无限期监听消息。
        - 处理自动重连
        - 收到消息时调用回调
        """
        def on_message(client, userdata, msg):
            callback(client, topic, msg.payload.decode())

        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print(f"Connected to MQTT OK! Subscribed to {topic}")
                self.__connect_status = 1
                if self.__is_disconnected:
                    self.__is_disconnected = False
                    client.subscribe(topic)
            else:
                print(f"Failed to connect for subscribe, return code {rc}")

        def on_disconnect(client, userdata, rc):
            print("Disconnected, trying to reconnect...")
            self.__is_disconnected = True
            while True:
                try:
                    client.reconnect()
                    break
                except Exception as e:
                    print(f"Reconnection failed: {e}")
                    time.sleep(5)

        self.__server = server
        self.__port = port
        self.__keepalive = keepalive
        self.__id = client_id
        self.__topic = topic
        self.__callback = callback

        client = self.connect(server, port, keepalive, client_id)
        client.on_message = on_message
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect

        client.subscribe(topic)
        client.loop_forever()
        client.disconnect()




