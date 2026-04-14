import requests

# 测试文件上传
def test_upload():
    url = 'http://localhost:9000/api/encry/file/upload'
    
    # 使用之前获取的 token
    token = 'eyJhbGciOiJIUzUxMiJ9.eyJsb2dpbl91c2VyX2tleSI6IjYyNzMwYjQ5ZjNjZDRlMzZiZWYzMDMwM2E5MDQxZmZlIn0.221zIeeCS2DqwZyGHx1qgrp1GX6Ne6-AzV-9aAdVNzO7Z_bGsnmqGiSxK8p14iCPh1w738vU7SAWQASrE9hGwA'
    
    # 准备文件和其他参数
    files = {
        'file': open('test.txt', 'rb')
    }
    
    data = {
        'publicKey': 'test',
        'encryptAlgo': 'AES'
    }
    
    # 添加认证头
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    try:
        response = requests.post(url, files=files, data=data, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    test_upload()
