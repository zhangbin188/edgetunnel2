import requests
import time

# 配置信息
API_TOKEN = "替换为你的 API 令牌()"
ACCOUNT_ID = "替换为你的账户 ID"
PROJECT_NAME = "替换为你的 Pages 项目名称"
BATCH_SIZE = 100  # 每批删除的部署数量
PER_PAGE = 15    # 每页获取的部署数量

# API 端点
LIST_DEPLOYMENTS_URL = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/pages/projects/{PROJECT_NAME}/deployments"
DELETE_DEPLOYMENT_URL = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/pages/projects/{PROJECT_NAME}/deployments/{{deployment_id}}"

# 请求头
headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

def get_all_deployments():
    """获取所有部署的 ID 列表"""
    deployments = []
    page = 1
    
    while True:
        params = {
            "page": page,
            "per_page": PER_PAGE,
            "order": "created_on",
            "direction": "desc"  # 最新的部署先返回
        }
        
        response = requests.get(LIST_DEPLOYMENTS_URL, headers=headers, params=params)
        response_data = response.json()
        
        if not response_data.get("success", False):
            print(f"获取部署列表失败: {response_data.get('errors')}")
            print(f"当前请求参数: page={page}, per_page={PER_PAGE}")
            return []
        
        result = response_data.get("result", [])
        if not result:
            break  # 没有更多部署了
        
        # 提取部署 ID
        deployment_ids = [item["id"] for item in result]
        deployments.extend(deployment_ids)
        
        page += 1

    return deployments

def batch_delete_deployments(deployment_ids):
    """批量删除部署"""
    total_deleted = 0
    total_failed = 0
    failed_ids = []
    
    # 分批处理
    for i in range(0, len(deployment_ids), BATCH_SIZE):
        batch = deployment_ids[i:i+BATCH_SIZE]
        print(f"处理第 {i//BATCH_SIZE + 1} 批，共 {len(batch)} 个部署...")
        
        for deployment_id in batch:
            url = DELETE_DEPLOYMENT_URL.format(deployment_id=deployment_id)
            
            try:
                response = requests.delete(url, headers=headers)
                response_data = response.json()
                
                if response_data.get("success", False):
                    total_deleted += 1
                    print(f"已删除部署: {deployment_id}")
                else:
                    total_failed += 1
                    failed_ids.append(deployment_id)
                    print(f"删除部署 {deployment_id} 失败: {response_data.get('errors')}")
                
                # 控制请求频率，避免触发速率限制
                time.sleep(0.5)
                
            except Exception as e:
                total_failed += 1
                failed_ids.append(deployment_id)
                print(f"删除部署 {deployment_id} 时发生错误: {str(e)}")
        
        # 每批处理后稍作休息
        time.sleep(2)
    
    print("\n处理完成:")
    print(f"成功删除: {total_deleted} 个部署")
    print(f"删除失败: {total_failed} 个部署")
    
    if failed_ids:
        print("删除失败的部署 ID:")
        print(", ".join(failed_ids))

if __name__ == "__main__":
    print(f"开始获取 {PROJECT_NAME} 项目的所有部署...")
    deployments = get_all_deployments()
    
    if not deployments:
        print("没有找到部署或获取部署失败")
    else:
        print(f"共找到 {len(deployments)} 个部署")
        confirm = input(f"确定要删除这 {len(deployments)} 个部署吗？(y/N): ")
        
        if confirm.lower() == "y":
            batch_delete_deployments(deployments)
        else:
            print("操作已取消")