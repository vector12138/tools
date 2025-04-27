import socket
import os
import sys
import requests

script_directory = os.path.dirname(os.path.abspath(__file__))

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.common import logger

# 创建 Logger 实例
app_logger = logger.Logger(name='LOG', log_file="./logs/wxapi_update_ip.log")

def get_ip_from_domain(domain):
    try:
        ip = socket.gethostbyname(domain)
        app_logger.info(f"获取 ip 成功: {ip}")
        return ip
    except Exception as e:
        app_logger.info(f"无法解析域名 {domain}: {e}")
        return None
    
# 获取企业微信 access_token
def get_access_token(corp_id, corp_secret):
    url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corp_id}&corpsecret={corp_secret}"
    response = requests.get(url)
    data = response.json()
    if data.get("errcode") == 0:
        app_logger.info(f"获取 access_token 成功: {data}")
        return data["access_token"]
    else:
        app_logger.info(f"获取 access_token 失败: {data}")
        return None

def update_ip_whitelist(access_token, ip):
    url = f"https://qyapi.weixin.qq.com/cgi-bin/whatever-whitelist-api"
    data = {
        "ip": ip,
        # 根据 API 文档，可能需要传入其他参数
    }
    response = requests.post(url, params={"access_token": access_token}, json=data)
    try:
        app_logger.info(response)
        result = response.json()
        if result.get("errcode") == 0:
            app_logger.info(f"成功添加 IP 地址 {ip} 到白名单")
        else:
            app_logger.info(f"更新白名单失败: {result}")
    except Exception as e:
        app_logger.info(f"解析 API 响应失败: {e}")

if __name__ == "__main__":
    corp_id = "wwe0abb1a9ad011a1c"
    corp_secret = "ECQ0usPbucEHICmWI2okqwOpZnyQvsHlYVrCwy20Tx4"
    domain = "device.nginx.littlehai.top"
    # 获取企业微信 access_token
    access_token = get_access_token(corp_id, corp_secret)
    if access_token:
        # 获取 IP 地址
        ip = get_ip_from_domain(domain)
        if ip:
            # 更新 IP 白名单
            update_ip_whitelist(access_token, ip)