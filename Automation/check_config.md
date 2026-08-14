# check_config.py

用于批量备份网络设备配置并检查配置变化的 Python 脚本。

## 主要功能

- 从 `ip_list.txt` 读取设备地址
- 通过 SSH 登录网络设备
- 获取并保存当前配置
- 与最近一次历史配置进行比较
- 生成单设备报告和每日汇总报告
- 单台设备失败后继续处理其他设备

## 工作流程

读取设备列表 → SSH 登录设备 → 关闭终端分页 → 获取当前配置 → 保存配置 → 比较历史配置 → 生成审计报告

## 环境要求

- Python 3.9+
- Paramiko
- 设备已启用 SSH
- 登录账户具有查看配置的权限

安装依赖：`pip install paramiko`

## 使用方法

1. 在脚本所在目录创建 `ip_list.txt`，每行填写一个设备地址，例如：

    192.0.2.10  
    192.0.2.11

2. 设置 SSH 密码。

   Windows PowerShell：

    $env:SWITCH_PASSWORD = "your-password"

   Linux/macOS：

    export SWITCH_PASSWORD='your-password'

3. 运行脚本：

    python check_config.py

## 输出文件

- `configs/`：设备配置备份
- `reports/`：单设备审计报告和每日汇总报告

报告结果包括：

- 初始基线
- 配置无变化
- 配置有变化
- 执行失败

## 适用范围

脚本默认执行 `display current-configuration` 获取配置，主要适用于支持该命令的 Huawei、H3C 等设备。

不同厂商或型号可能需要修改配置查询命令和分页关闭命令。

## 注意事项

- 不要将真实密码写入代码
- 不要上传真实的 `ip_list.txt`
- 不要上传 `configs/` 和 `reports/` 中的敏感内容
- 建议使用只读或最小权限账户
- 请先在测试设备上验证后再用于生产环境

## Disclaimer

This script is intended for authorized network configuration backup and auditing only. Use it at your own risk.
