# FastOpen

## 项目简介
FastOpen 是一个提升跨平台开发效率的工具。当你通过终端（SSH）连接到 Linux 服务器进行开发时，如果在服务器终端中想要查看代码或打开文件夹，通常需要手动在 Windows 上找到对应的映射盘符路径并打开。

FastOpen 允许你直接在 Linux 终端输入命令（如 `vs main.py`），通过 MQTT 通信自动触发 Windows 端执行对应的操作（如用 VS Code 打开该文件），省去了手动查找路径的繁琐过程。

## 工作原理
1.  **Server 端 (Linux)**: 用户输入快捷指令 -> 解析路径 -> 发送 MQTT 消息。
2.  **Client 端 (Windows)**: 监听 MQTT 消息 -> 接收指令 -> 将 Linux 路径映射为 Windows 本地路径 (如 Samba/SMB 映射) -> 调用 Windows 程序打开。

## 目录结构
- `server.py`: Linux 端主程序，负责安装别名和发送指令。
- `local.py`: Windows 端监听程序，负责执行指令。
- `config.json`: 配置文件，定义 MQTT 代理、路径映射和命令行为。
- `alias.bashrc`: 预设别名文件，可直接 source 使用。

---

## 详细使用步骤

### 1. 环境准备
- **Linux 服务器**: Python 3
- **Windows 本地**: Python 3
- **文件共享**: 确保 Linux 目录已通过 Samba/SMB 映射到 Windows 本地驱动器 (例如 Linux 的 `/home/user/work` 映射为 Windows 的 `Z:\work`)。

### 2. 配置文件 (config.json)
无需分开配置，两端通常保持一致（或通过 Git 同步）。打开 `config.json` 进行修改：

```json
{
    "MQTT config": {
        "Server": "10.17.100.241",    // MQTT Broker IP
        "Port": "1883",               // MQTT Broker 端口
        "KeepAliveSeconed": "10",
        "Topic": "fastopen"           // 通信 Topic，确保唯一避免冲突
    },
    // 路径映射配置：将服务器路径转换为本地路径
    "server config": [
        {
            "IP": "",
            "server": "/home/quwj/",  // Linux 服务器上的绝对路径前缀
            "local": "Z:/"            // Windows 上对应的挂载盘符或路径
        }
    ],
    // 命令定义
    "command": [
        {
            "name": "vs",             // 在 Linux 终端输入的命令别名
            "execute": "code {file}"  // Windows 上执行的命令 ({file} 会被自动替换为本地路径)
        },
        {
            "name": "d",
            "execute": "start {file}" // 打开文件夹
        }
    ]
}
```

### 3. 服务器端操作 (Linux)
在 Linux 服务器上执行以下步骤以注册快捷指令。有两种方法：

**方法一：使用 alias.bashrc (推荐)**
1.  **编辑 alias.bashrc**:
    打开 `alias.bashrc`，确保里面的路径指向正确的 `open.sh` 位置。例如：
    ```bash
    alias vs='/path/to/fastopen/open.sh vs '
    alias d='/path/to/fastopen/open.sh d '
    ```
2.  **生效配置**:
    在你的 `~/.bashrc` 或 `~/.zshrc` 中添加以下内容，以便每次登录自动生效：
    ```bash
    source /path/to/fastopen/alias.bashrc
    ```
    或者直接在当前终端执行：
    ```bash
    source alias.bashrc
    ```
    `alias.bashrc` 中还可以包含其他常用的便捷别名。

**方法二：自动生成 open.sh**
1.  **生成执行脚本**:
    执行安装模式，这会根据 `config.json` 中的 `command` 自动覆写 `open.sh` 脚本并输出建议的 alias 命令。
    ```bash
    python3 server.py -c ServerInstall
    ```
2.  **生效配置**:
    将输出的 alias 命令复制到你的 shell 配置文件中，或者直接 source 生成的脚本。

### 4. Windows 终端操作 (Windows)
在 Windows 电脑上启动监听服务：

1.  **进入项目目录**:
    打开 CMD 或 PowerShell，进入 fastopen 目录。
2.  **启动监听**:
    ```cmd
    python local.py
    ```
    *注意*: 该窗口需要保持开启，建议将其加入开机自启或使用后台运行工具。

### 5. 开始使用
一切就绪后，尝试以下流程：

1.  在 **Linux 终端** 中，进入任意目录，输入：
    ```bash
    vs server.py
    ```
2.  观察 **Windows**:
    如果配置正确，VS Code 将会自动弹起并打开该文件。

3.  常用预设命令 (需在 config.json 中定义并配置 alias):
    - `d .`: 在 Windows 资源管理器中打开当前目录。
    - `vs file`: 用 VS Code 打开文件。

## 常见问题
- **路径打不开？**
  检查 `config.json` 中的 `server` 和 `local` 映射是否完全匹配。
- **没反应？**
  检查 `MQTT config` 中的 Server IP 是否两端都能访问。

## TODO
- [ ] 逻辑重构优化
