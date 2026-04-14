import requests
import json

# 测试登录获取 token
def test_login():
    url = 'http://localhost:9000/api/login'
    
    data = {
        'username': 'admin',
        'password': 'admin123',
        'code': '',
        'uuid': ''
    }
    
    try:
        response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        # 解析响应
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 200:
                token = result.get('data', {}).get('token')
                if token:
                    print(f"Token: {token}")
                    return token
    except Exception as e:
        print(f"Error: {e}")
    
    return None

if __name__ == '__main__':
    test_login()
