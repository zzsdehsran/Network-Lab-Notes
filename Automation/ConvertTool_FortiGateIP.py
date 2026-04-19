import requests
import ipaddress

def download_and_save_ips(url, filepath):

    ips = []
    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding':'gzip, deflate, br, zstd',
        'Accept-Language':'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Connection': 'keep-alive',
        'path':'/china-operator-ip/chinanet.txt',
    }
    try:
        # 1.尝试连接并获取数据
        print(f"正在连接{url}...")
        response = requests.get(url, headers=headers,timeout=10)
        response.raise_for_status()  # 检查http状态码
        response.encoding = 'utf-8'  #指定编码类型去解码
        # response.encoding = response.apparent_encoding
        

        # 处理数据
        data = response.text.strip()
        count = len(data.split())
        print(f"获取成功，共{count}条数据。")


        # 2. 直接在内存中按行拆分数据
        raw_data_lines = response.text.strip().splitlines()
        print(f"获取成功，共 {len(raw_data_lines)}跳数据。正在转换格式并写入文件...：")

        # 3. 打开文件准备写入 （边转换、边存列表、边写文件）
        with open(filepath, 'w', encoding='utf-8') as f:
            for raw_ip in raw_data_lines:
                # 忽略可能存在的空行
                if not raw_ip.strip():
                    continue

                # 针对飞塔防火墙进行IP地址格式转换
                forti_format = ipaddress.ip_network(raw_ip.strip()).with_netmask.replace('/', ' ')
                f.write(forti_format + '\n')
                ips.append(forti_format)  # 把转换后的结果存进列表里，这样 return 才有东西

        print(f"🎉 处理完成！共 {len(ips)} 条数据已成功保存至：{filepath}")
        
    except Exception as e:
        print(f"错误原因：{e}")
    
    return ips

if __name__ == '__main__':
    target  = 'https://gaoyifan.github.io/china-operator-ip/chinanet.txt'
    file = 'chinanet_safe.txt'

    download_and_save_ips(target, file)
    
    