# 远程办公场景下，通过 WireGuard 代替 IPSEC 实现网络互访

### 🛠️ 实验室基础环境

#### 节点 A（Client）: Ubuntu 24.04 (Noble Numbat) / Windows 11，位于用户家中。

#### 节点 B（Sever）: Red Hat Enterprise Linux 9.3, 位于企业内网环境。

### 🌈 网络拓扑架构

WireGuard Server --> Core SW --> 深信服AC --> FortiGate 100F --> 出口


### WireGuard Server 配置
#### 1、安装EPEL仓库
```bash
# 1. 启用 EPEL 仓库
sudo dnf install epel-release -y

# 注意：如果是正宗的 RHEL 9 官方镜像，可能需要先注册或手动下载 EPEL 的 rpm 包：
# sudo dnf install https://dl.fedoraproject.org/pub/epel/epel-release-latest-9.noarch.rpm -y
分析工具: Wireshark, tcpdump, tshark, iperf3
```

#### 2、安装WireGuard工具
```bash
# 2. 安装 wireguard-tools
sudo dnf install wireguard-tools -y
```

#### 3、验证安装
```bash
# 查看 wg 命令是否可用
wg --version

# 验证内核是否成功加载了 wireguard 模块
lsmod | grep wireguard
# 如果没有输出，可以手动加载一下：sudo modprobe wireguard
```

#### 4、放行UDP 51820端口

```bash
# 永久放行 UDP 51820 端口
sudo firewall-cmd --add-port=51820/udp --permanent

# 重新加载防火墙规则使其生效
sudo firewall-cmd --reload

# 查看是否放行成功
sudo firewall-cmd --list-ports
```

自动化: Python (Netmiko, Paramiko, Requests)
