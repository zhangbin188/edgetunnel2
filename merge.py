import os

def merge():
    regions = {
        'HKG': 'HKG',
        'KHH': 'KHH',
        'SIN': 'SIN',
        'NRT': 'NRT',
        'SEA': 'SEA'
    }
    
    merged_entries = []
    current_id = 1
    
    # 读取并合并所有文件
    for filename, region in regions.items():
        with open(filename, 'r') as f:
            for line in f:
                ip = line.strip()
                if ip:  # 跳过空行
                    merged_entries.append(f"{ip}#{region} {current_id}")
                    current_id += 1
    
    # 保存合并结果
    with open('ips.txt', 'w') as f:
        for entry in merged_entries:
            f.write(f"{entry}\n")
    
    print(f"合并完成，共 {len(merged_entries)} 条记录，已保存到 ips.txt")
    
    # 删除原始文件
    for filename in regions.keys():
        if os.path.exists(filename):
            os.remove(filename)
            print(f"已删除 {filename}")

merge()