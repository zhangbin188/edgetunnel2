# Edge Tunnel

Edge Tunnel 是一个基于 Cloudflare Pages 的免费代理解决方案, 配置精简, 适合新手快速上手

## 项目特点

- **免费**：利用 Cloudflare Pages 免费托管
- **易用**：通过环境变量灵活配置
- **兼容性强**：支持 v2ray 和 clash 客户端

> **欢迎各位大佬指正代码中存在的问题！**

[![Stargazers over time](https://starchart.cc/ImLTHQ/edgetunnel.svg?variant=adaptive)](https://starchart.cc/ImLTHQ/edgetunnel)

如果本项目对您有帮助, 请点 Star 支持 !

## 使用方法

1. **Fork 本项目**
2. **创建 Cloudflare Pages**
- **导入您 Fork 的仓库**
- **添加环境变量**
- **保存并部署**
3. **导入订阅(域名/订阅路径/clash或v2ray)并开始使用**

## 环境变量说明

| 变量名 | 示例值 | 说明 |
|-|-|-|
| SUB_PATH | `订阅路径` | 域名/`订阅路径` |
| TXT_URL | `https://raw.domain.com/CFST.txt` | 优选 IP 列表, 格式：`地址:端口#节点名称`, 端口默认 `443` |
| NAT64 | `2a02:898:146:64::/96` | NAT64 前缀 |
| DOH | `1.1.1.1` | DOH地址 |
| PROXY_IP | `proxyip.cmliussss.net` | 反代地址和端口, 端口不填默认 `443` |
| FAKE_WEB | `baidu.com` | 伪装网页 |

<details>
<summary><strong>反代说明</strong></summary>

- 并非指的是 `PROXY_IP`, 而是用于没有代理工具场景的简易代理
- 使用方法: https://域名/订阅路径/https://目标域名和路径
- 无法访问CF CDN

请勿用于非法用途

</details>

<details>
<summary><strong>CFTest说明</strong></summary>

# 简介

CFTest 是用于检测 Cloudflare IP 地址的工具，可帮助用户快速筛选出可连通的 Cloudflare IP 地址，并支持按指定地区（机场三字码）进行筛选。该工具适用于需要寻找优质 Cloudflare IP 节点的场景

- 所需 Python 库：requests
- 可通过以下命令安装依赖：`pip install requests`

| 可选参数 | 说明 |
|-|-|
| `-d` | 指定一个或多个机场三字码（如 LAX SJC），仅返回属于这些地区的 IP |
| `-i` | 指定需要获取的 IP 数量，默认值为 10 |
| `-o` | 指定输出文件名称，默认值为 `output.txt` |

</details>

## 提醒

- CloudFlare 明文禁止优选IP和使用CF Pages部署代理, 封号风险自己承担
- 建议定期同步上游仓库以获取最新功能和修复