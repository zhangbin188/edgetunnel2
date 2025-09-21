import pandas as pd

csv_files = [
    "HKG.csv",
    "KHH.csv",
    "SIN.csv",
    "NRT.csv",
    "SEA.csv",
]

area_names = [
    "香港",
    "台湾",
    "新加坡",
    "东京",
    "西雅图",
]

def csv_to_txt(csv_files, area_names, output_filename):
    with open(output_filename, 'w', encoding='utf-8') as f:
        for csv_file, area in zip(csv_files, area_names):

            df = pd.read_csv(csv_file, encoding='utf-8')

            for i, ip in enumerate(df.iloc[:, 0], start=1):
                # 确保内容不为空才写入
                if pd.notna(ip) and str(ip).strip() != "":
                    line = f"{ip}#{area} {i}"
                    f.write(f"{line}\n")
    
    # 移除空行
    with open(output_filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 过滤掉空行
    non_empty_lines = [line for line in lines if line.strip() != ""]
    
    # 重新写入无空行的内容
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.writelines(non_empty_lines)

csv_to_txt(csv_files, area_names, "AutoTest.txt")