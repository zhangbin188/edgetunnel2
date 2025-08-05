import os

# 配置：根据需求设置最大行数限制（示例：限制最多 5000 行）
MAX_LINES = 25
TEST_FILE = "AutoTest.txt"


def count_lines(file_path):
    """统计文件行数"""
    if not os.path.exists(file_path):
        return 0
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return sum(1 for line in f)


def main():
    current_lines = count_lines(TEST_FILE)
    print(f"当前测速结果行数：{current_lines}/{MAX_LINES}")
    
    if current_lines > MAX_LINES:
        print(f"❌ 超过行数限制，需要重新测速")
        return 1  # 返回非零状态码，告知 Actions 步骤失败
    else:
        print(f"✅ 行数符合限制")
        return 0  # 返回 0 表示成功


if __name__ == "__main__":
    exit(main())