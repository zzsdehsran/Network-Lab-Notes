# Network Automation Scripts

本目录用于存放网络运维与自动化相关的 Python 脚本。

## 工具列表

| 文件 | 功能 |
|---|---|
| [`check_config.py`](check_config.py) | 通过 SSH 批量备份网络设备配置，并与历史配置进行差异审计 |
| [`ConvertTool_FortiGateIP.py`](ConvertTool_FortiGateIP.py) | FortiGate IP 数据转换工具 |
| `Network_config/huawei/` | Huawei 网络设备相关配置与资料 |

## check_config.py

`check_config.py` 是一个基于 Python 和 Paramiko 的网络设备配置备份与差异审计脚本。

主要功能：

- 从 `ip_list.txt` 批量读取设备地址
- 通过 SSH 登录网络设备
- 执行 `display current-configuration`
- 尝试关闭设备终端分页
- 将当前配置保存到 `configs/`
- 与最近一次历史配置进行比较
- 在 `reports/` 中生成单设备报告和每日汇总报告
- 单台设备执行失败时继续检查其他设备

详细使用方法请参阅：

- [check_config.py 使用说明](check_config.md)

## Warning and Disclaimer

Every effort has been made to make these Python scripts as complete and
accurate as possible, but no warranty or fitness for a particular network
environment is implied. Use them at your own risk.

我已尽一切努力使这些 Python 脚本尽可能完整和准确，但不暗示对特定网络环境的任何保证或适用性。使用风险由使用者自行承担。
