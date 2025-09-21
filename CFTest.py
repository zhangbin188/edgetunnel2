MAX_CONCURRENT_THREADS = 500
REQUEST_TIMEOUT = 5

import sys
import requests
import ipaddress
from concurrent.futures import ThreadPoolExecutor, as_completed, wait, FIRST_COMPLETED
import re
import threading

def is_valid_ipv4_range(ip_range):
    """验证IPv4段格式是否正确"""
    # 匹配CIDR格式 (如192.168.1.0/24)
    cidr_pattern = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})/(\d{1,2})$'
    match = re.match(cidr_pattern, ip_range)
    
    if not match:
        return False
    
    # 验证每个IP段的值在0-255之间
    for i in range(4):
        if not (0 <= int(match.group(i+1)) <= 255):
            return False
    
    # 验证前缀长度在0-32之间
    prefix = int(match.group(5))
    if not (0 <= prefix <= 32):
        return False
        
    return True

def fetch_ip_ranges(url):
    """从指定URL获取IP段列表"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # 过滤并验证IP段
        ip_ranges = []
        for line in response.text.splitlines():
            line = line.strip()
            if line and is_valid_ipv4_range(line):
                ip_ranges.append(line)
            elif line:
                print(f"忽略无效的IP段: {line}")
                
        return ip_ranges
    except Exception as e:
        print(f"获取IP段失败: {e}")
        sys.exit(1)

def expand_ip_range(ip_range):
    """将IP段扩展为具体的所有IP地址列表"""
    try:
        # 使用strict=True确保网络地址合法
        network = ipaddress.ip_network(ip_range, strict=True)
        
        # 只处理IPv4地址
        if not isinstance(network, ipaddress.IPv4Network):
            print(f"忽略非IPv4段: {ip_range}")
            return []
            
        # 返回所有IP地址，包括网络地址和广播地址
        return [str(ip) for ip in network]
            
    except ValueError as e:
        print(f"解析IP段 {ip_range} 失败: {e}")
        return []

def check_ip_location(ip, target_colo, stop_event):
    """检查IP对应的机场码是否匹配目标，支持通过事件停止"""
    # 如果已触发停止事件，直接返回
    if stop_event.is_set():
        return None
        
    # 验证IP格式
    try:
        ipaddress.IPv4Address(ip)
    except ValueError:
        print(f"无效的IP地址: {ip}")
        return None
        
    url = f"http://{ip}/cdn-cgi/trace"
    try:
        # 如果已触发停止事件，直接返回
        if stop_event.is_set():
            return None
            
        # 使用常量作为超时时间
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        for line in response.text.splitlines():
            if line.startswith('colo='):
                colo = line.split('=')[1].strip()
                return ip if colo == target_colo else None
        return None
    except Exception as e:
        # 静默处理连接错误，避免输出过多信息
        return None

def main():
    if len(sys.argv) != 4:
        print("用法: python CFTest.py 机场三字码 最大数量 文件名(.txt)")
        print("示例: python CFTest.py HKG 100 output.txt")
        sys.exit(1)
    
    target_colo = sys.argv[1].upper()
    try:
        max_count = int(sys.argv[2])
        if max_count <= 0:
            raise ValueError("最大数量必须为正数")
    except ValueError as e:
        print(f"无效的最大数量: {e}")
        sys.exit(1)
    
    output_file = sys.argv[3]
    ip_ranges_url = "https://www.cloudflare-cn.com/ips-v4"
    
    print(f"正在从 {ip_ranges_url} 获取IP段...")
    ip_ranges = fetch_ip_ranges(ip_ranges_url)
    print(f"成功获取并验证 {len(ip_ranges)} 个IP段")
    
    print("正在扩展IP段...")
    all_ips = []
    for range_str in ip_ranges:
        ips = expand_ip_range(range_str)
        all_ips.extend(ips)
        # 显示每个网段扩展的IP数量
        print(f"  从 {range_str} 扩展出 {len(ips)} 个IP")
    
    # 去重IP列表
    all_ips = list(set(all_ips))
    print(f"共扩展出 {len(all_ips)} 个唯一IP地址，正在检查每个IP的位置...")
    print(f"找到 {max_count} 个匹配IP后将停止搜索")
    
    # 创建停止事件
    stop_event = threading.Event()
    
    # 使用常量作为最大并发线程数
    max_workers = min(MAX_CONCURRENT_THREADS, len(all_ips))
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        futures = []
        for ip in all_ips:
            # 将停止事件传递给每个任务
            future = executor.submit(check_ip_location, ip, target_colo, stop_event)
            futures.append(future)
        
        # 跟踪进度
        total = len(futures)
        completed = 0
        matched_ips = []
        
        # 循环处理完成的任务，直到达到最大数量或所有任务完成
        while completed < total and len(matched_ips) < max_count:
            # 等待第一个任务完成
            done, not_done = wait(futures, return_when=FIRST_COMPLETED)
            
            for future in done:
                if future in futures:
                    futures.remove(future)
                    completed += 1
                    
                    result = future.result()
                    if result:
                        matched_ips.append(result)
                        print(f"已找到 {len(matched_ips)}/{max_count} 个匹配IP")
                        
                        # 检查是否达到最大数量
                        if len(matched_ips) >= max_count:
                            print(f"\n已找到 {max_count} 个匹配IP，达到最大数量，停止搜索")
                            stop_event.set()  # 触发停止事件
                            # 取消所有未完成的任务
                            for f in futures:
                                f.cancel()
                            break
            
            # 检查是否需要停止
            if stop_event.is_set():
                break
            
            # 显示进度
            if completed % 50 == 0 or completed == total:
                print(f"进度: {completed}/{total} ({(completed/total)*100:.1f}%)，已找到 {len(matched_ips)} 个匹配IP")
    
    # 如果达到最大数量，截断结果
    if len(matched_ips) > max_count:
        matched_ips = matched_ips[:max_count]
    
    # 排序结果
    matched_ips = sorted(matched_ips, key=lambda x: ipaddress.IPv4Address(x))
    
    # 保存结果到文件
    with open(output_file, 'w') as f:
        for ip in matched_ips:
            f.write(f"{ip}\n")
    
    print(f"完成！共找到 {len(matched_ips)} 个属于 {target_colo} 的IP地址，已保存到 {output_file}")

main()