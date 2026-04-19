## 远程办公场景下，通过 WireGuard 代替 IPSEC 实现网络互访

### 🛠️ 实验室基础环境

#### 节点 A（Client）: Ubuntu 24.04 (Noble Numbat) / Windows 11，位于用户家中。

#### 节点 B（Sever）: Red Hat Enterprise Linux 9.3, 位于企业内网环境。


### 🌈 网络拓扑架构

WireGuard Server --> Core SW --> 深信服AC --> 飞塔防火墙 --> 出口

防火墙/网关: FortiGate / WireGuard Gateway

分析工具: Wireshark, tcpdump, tshark, iperf3

自动化: Python (Netmiko, Paramiko, Requests)
