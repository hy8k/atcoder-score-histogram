import environ
import requests
from bs4 import BeautifulSoup

env = environ.Env()
env.read_env('.env')

LOGIN_URL = 'https://atcoder.jp/login'


def login():
    # ログイン処理
    session = requests.session()
    login_form = session.get(LOGIN_URL)
    bs = BeautifulSoup(login_form.text, 'html.parser')
    csrf_token = bs.find(attrs={'name': 'csrf_token'}).get('value')
    login_data = {
        'username': env('ATCODER_USERNAME'),
        'password': env('ATCODER_PASSWORD'),
        'csrf_token': csrf_token
    }
    session.post(LOGIN_URL, data=login_data)
    return session
