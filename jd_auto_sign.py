import requests
import time
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 京东签到接口和请求头
SIGN_URL = 'https://api.m.jd.com/client.action?functionId=signBeanAct'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Referer': 'https://h5.m.jd.com/',
    'Cookie': 'your_jd_cookie'
}

def jd_sign():
    try:
        params = {'appid': 'your_appid'}
        response = requests.get(SIGN_URL, headers=HEADERS, params=params)
        result = response.json()
        if result.get('code') == 0:
            logging.info('京东签到成功，结果：%s', result)
        else:
            logging.warning('京东签到失败，结果：%s', result)
    except Exception as e:
        logging.error('签到过程中出现异常：%s', str(e))

if __name__ == '__main__':
    jd_sign()
    time.sleep(3)