import datetime
import difflib
import os
import re
import time
from pathlib import Path

import paramiko


# ==================== 基础配置 ====================

USERNAME = "xxxxxx"
PASSWORD = os.getenv("SWITCH_PASSWORD")
IP_LIST_FILE = "ip_list.txt"

SSH_PORT = 22
CONNECT_TIMEOUT = 10
COMMAND_TIMEOUT = 90

# 不区分厂商，依次尝试关闭分页
PAGING_COMMANDS = [
    "screen-length 0 temporary",
    "screen-length disable"
]

CONFIG_COMMAND = "display current-configuration"

TODAY = datetime.date.today()
CONFIG_DIR = Path("configs")
REPORT_DIR = Path("reports")

CONFIG_DIR.mkdir(exist_ok=True)
REPORT_DIR.mkdir(exist_ok=True)


# ==================== 通用函数 ====================

def safe_filename(value):
    """将IP或主机名转换为安全文件名。"""
    return re.sub(r'[\\/:*?"<>|]', "_", value)


def decode_output(data):
    """兼容常见设备输出编码。"""
    for encoding in ("utf-8", "gb18030", "gbk"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def clear_buffer(shell):
    """清空交互终端缓冲区。"""
    while shell.recv_ready():
        shell.recv(65535)
        time.sleep(0.05)


def run_command(shell, command, timeout=90, idle_timeout=2):
    """
    执行命令并持续接收输出。
    连续idle_timeout秒没有新数据时，认为命令执行完毕。
    """
    clear_buffer(shell)
    shell.send(command.rstrip() + "\n")

    chunks = []
    start_time = time.monotonic()
    last_data_time = start_time
    received = False

    while time.monotonic() - start_time < timeout:
        if shell.recv_ready():
            data = shell.recv(65535)
            if not data:
                break

            chunks.append(data)
            received = True
            last_data_time = time.monotonic()
        else:
            if received and time.monotonic() - last_data_time >= idle_timeout:
                break
            time.sleep(0.1)

    if not received:
        raise TimeoutError(f"命令没有返回数据：{command}")

    return decode_output(b"".join(chunks))


def clean_config(output):
    """清理回车、ANSI字符、命令回显和末尾设备提示符。"""
    output = output.replace("\r", "")

    ansi_pattern = re.compile(
        r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])"
    )
    output = ansi_pattern.sub("", output)

    lines = output.splitlines()

    # 删除配置命令回显
    for index, line in enumerate(lines):
        if line.strip().endswith(CONFIG_COMMAND):
            lines = lines[index + 1:]
            break

    # 删除最后一行类似 <Switch> 或 [Switch] 的提示符
    while lines and not lines[-1].strip():
        lines.pop()

    if lines and re.fullmatch(r"[<\[].+[>\]]", lines[-1].strip()):
        lines.pop()

    return "\n".join(lines).strip() + "\n"


# ==================== 文件处理 ====================

def load_devices():
    """从文件读取设备地址，每行第一列为IP或主机名。"""
    path = Path(IP_LIST_FILE)

    if not path.exists():
        raise FileNotFoundError(f"找不到设备列表：{IP_LIST_FILE}")

    devices = []

    with path.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            device = line.split()[0]

            if device not in devices:
                devices.append(device)

    return devices


def get_today_config_path(ip):
    """返回当天配置文件路径。"""
    return CONFIG_DIR / (
        f"{safe_filename(ip)}_{TODAY.isoformat()}.cfg"
    )


def find_latest_history(ip):
    """查找该设备今天以前最近的一份配置。"""
    safe_ip = safe_filename(ip)
    history = []

    for path in CONFIG_DIR.glob(f"{safe_ip}_*.cfg"):
        date_text = path.stem[len(safe_ip) + 1:]

        try:
            file_date = datetime.date.fromisoformat(date_text)
        except ValueError:
            continue

        if file_date < TODAY:
            history.append((file_date, path))

    if not history:
        return None

    history.sort(key=lambda item: item[0], reverse=True)
    return history[0][1]


def save_config(ip, config):
    """保存当天设备配置。"""
    path = get_today_config_path(ip)

    with path.open("w", encoding="utf-8", newline="\n") as file:
        file.write(config)

    return path


def compare_configs(old_path, new_path, ip):
    """使用difflib比较两份配置文件。"""
    with old_path.open(
        "r", encoding="utf-8", errors="replace"
    ) as file:
        old_lines = file.readlines()

    with new_path.open(
        "r", encoding="utf-8", errors="replace"
    ) as file:
        new_lines = file.readlines()

    return list(
        difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=f"{ip} 旧配置：{old_path.name}",
            tofile=f"{ip} 新配置：{new_path.name}",
            lineterm="\n"
        )
    )


def create_report(ip, old_path, new_path):
    """生成单台设备差异报告。"""
    report_path = REPORT_DIR / (
        f"{safe_filename(ip)}_{TODAY.isoformat()}_report.txt"
    )

    if old_path is None:
        status = "初始基线"
        content = (
            f"设备：{ip}\n"
            f"检查日期：{TODAY.isoformat()}\n"
            f"当前配置：{new_path}\n\n"
            "未找到历史配置，本次配置已保存为初始基线。\n"
        )
    else:
        diff = compare_configs(old_path, new_path, ip)

        if diff:
            status = "配置有变化"
            content = (
                f"设备：{ip}\n"
                f"检查日期：{TODAY.isoformat()}\n"
                f"历史配置：{old_path}\n"
                f"当前配置：{new_path}\n\n"
                "发现配置变化：\n"
                f"{'=' * 70}\n"
                f"{''.join(diff)}"
                f"{'=' * 70}\n"
            )
        else:
            status = "配置无变化"
            content = (
                f"设备：{ip}\n"
                f"检查日期：{TODAY.isoformat()}\n"
                f"历史配置：{old_path}\n"
                f"当前配置：{new_path}\n\n"
                "没有发现配置变化。\n"
            )

    with report_path.open("w", encoding="utf-8") as file:
        file.write(content)

    return status, content

# ==================== 设备审计 ====================

def audit_device(ip):
    """登录设备、获取配置、保存并比较。"""
    ssh = None

    try:
        print(f"\n正在连接设备：{ip}")

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        ssh.connect(
            hostname=ip,
            port=SSH_PORT,
            username=USERNAME,
            password=PASSWORD,
            timeout=CONNECT_TIMEOUT,
            auth_timeout=CONNECT_TIMEOUT,
            banner_timeout=CONNECT_TIMEOUT,
            look_for_keys=False,
            allow_agent=False
        )

        print(f"登录成功：{ip}")

        shell = ssh.invoke_shell(width=200, height=1000)
        time.sleep(1)
        clear_buffer(shell)

        # 依次尝试分页关闭命令，不需要判断设备厂商
        for command in PAGING_COMMANDS:
            try:
                run_command(
                    shell,
                    command,
                    timeout=8,
                    idle_timeout=0.8
                )
            except Exception:
                pass

        print(f"正在获取配置：{ip}")

        output = run_command(
            shell,
            CONFIG_COMMAND,
            timeout=COMMAND_TIMEOUT,
            idle_timeout=5
        )

        config = clean_config(output)

        if len(config.strip()) < 20:
            raise RuntimeError("设备返回的配置内容为空或过短")

        # 必须在保存当天配置前查找历史配置
        old_path = find_latest_history(ip)
        new_path = save_config(ip, config)

        status, report_content = create_report(
            ip,
            old_path,
            new_path
        )

        print(f"配置已保存：{new_path}")
        print(f"审计结果：{status}")

        return True, report_content

    except paramiko.AuthenticationException:
        message = f"设备 {ip} SSH认证失败，请检查用户名或密码。"
    except paramiko.SSHException as error:
        message = f"设备 {ip} SSH连接失败：{error}"
    except Exception as error:
        message = f"设备 {ip} 审计失败：{error}"
    finally:
        if ssh is not None:
            ssh.close()

    print(message)
    return False, message + "\n"


# ==================== 主程序 ====================

def main():
    print("=" * 60)
    print("网络设备配置备份与差异审计工具")
    print("=" * 60)

    if not PASSWORD:
        print("错误：未设置 SWITCH_PASSWORD 环境变量。")
        return

    try:
        devices = load_devices()
    except Exception as error:
        print(f"读取设备列表失败：{error}")
        return

    if not devices:
        print("IP列表中没有有效设备。")
        return

    print(f"成功加载 {len(devices)} 台设备：")
    for device in devices:
        print(f"  - {device}")

    results = []

    for device in devices:
        success, content = audit_device(device)
        results.append((device, success, content))

    master_path = REPORT_DIR / (
        f"master_report_{TODAY.isoformat()}.txt"
    )

    with master_path.open("w", encoding="utf-8") as file:
        file.write(f"网络设备配置审计日报：{TODAY.isoformat()}\n")
        file.write("=" * 70 + "\n")

        for device, success, content in results:
            state = "成功" if success else "失败"
            file.write(f"\n设备：{device}，状态：{state}\n")
            file.write("-" * 70 + "\n")
            file.write(content)

    print(f"\n汇总报告已生成：{master_path}")


if __name__ == "__main__":
    main()
