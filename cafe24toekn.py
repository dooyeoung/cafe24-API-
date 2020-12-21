import requests
import base64
import re
import json
import datetime 
import urllib
from time import time, sleep
from tqdm import tqdm_notebook
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import subprocess


mall_id = ''
client_id = ''
encode_csrf_token = ''
encode_redirect_uri=''
scope='mall.read_application,mall.read_order,mall.read_category,mall.read_product'
driver_path = '/Users/dooyeoung/Documents/projects/webdriver/chromedriver'
save_path = '/Users/dooyeoung/Desktop'

# Encode string data
def stringToBase64(s):
    return base64.b64encode(s.encode('utf-8'))
 
def base64ToString(b):
    return base64.b64decode(b).decode('utf-8')

# 셀레니움 시작
options = webdriver.ChromeOptions()  
options.add_argument('headless')
options.add_argument('window-size=1920x1080')
options.add_argument("disable-gpu")

capa = DesiredCapabilities.CHROME
capa["pageLoadStrategy"] = "none"
driver = webdriver.Chrome(driver_path, chrome_options=options, desired_capabilities=capa)
wait = WebDriverWait(driver, 20)

#  카페24 로그인
url = 'https://eclogin.cafe24.com/Shop/'
driver.get(url)
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mall_id')))
driver.find_element_by_css_selector('#mall_id').send_keys('')
driver.find_element_by_css_selector('#userpasswd').send_keys('')
driver.find_element_by_css_selector('#tabAdmin > div > fieldset > p.gButton > a').click()
 
# 비밀번호 변경하기 있는경우
pwchange = driver.find_elements_by_css_selector('#iptBtnEm')
if len(pwchange) > 0:
    pwchange[0].click()
     

# cafe24 상위 메뉴가 로딩될때까지 기다린후 
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#gnb'))) 
url = '''https://{mall_id}.cafe24api.com/api/v2/oauth/authorize?response_type=code&client_id={client_id}&state={encode_csrf_token}&redirect_uri={encode_redirect_uri}&scope={scope}
'''.format(mall_id=mall_id, 
           client_id=client_id, 
           encode_csrf_token=encode_csrf_token, 
           encode_redirect_uri=encode_redirect_uri,
          scope=scope)

driver.get(url)
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'body'))) 

# 인증코드 발급
qry = urllib.parse.urlparse(driver.current_url).query
for param in qry.split('&'):
    if 'code' in param:
        code = param.split('=')[1]
        break

s = '{client_id}:{client_Secret}'.format( client_id=client_id,  client_Secret=encode_csrf_token)
b = stringToBase64(s)


# 토큰 발급
headers = {
    'Authorization': 'Basic {}'.format(b.decode()) ,
    'Content-Type': 'application/x-www-form-urlencoded',
}

data = {
  'grant_type': 'authorization_code',
  'code': code,
  'redirect_uri': encode_redirect_uri
}

response = requests.post('https://'+mall_id+'.cafe24api.com/api/v2/oauth/token', headers=headers, data=data)
token = eval(response.text)
print(token)

# 토큰 저장 및 업로드 
path_local  = '/Users/dooyeoung/Documents/projects/backend/server_v1/cafe24_token.json'
path_server = ''
with open(path_local, 'wt') as f:
  json.dump(token, f, indent=2)
 
path_pemfile = ''
# 토큰파일을 flaks api에도 업로드 
subprocess.call(f'scp -i {path_pemfile} {path_local} {path_server}', shell=True)  