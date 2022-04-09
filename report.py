# encoding=utf8
import argparse
import requests
from bs4 import BeautifulSoup


def retry(n, function):
    if (function()):
        return True
    for _ in range(n - 1):
        print('Retrying...')
        if (function()):
            return True
    return False


class Report(object):
    def __init__(self, stuid, password):
        self.stuid = stuid
        self.password = password
        self.session = requests.Session()

    def run(self):
        print('Login...')
        if retry(3, self.login):
            print('Login Successful!')
        else:
            print('Login Failed!')
            exit(-1)

        print('Report...')
        if retry(3, self.report):
            print('Report Successful!')
        else:
            print('Report Failed!')
            exit(-1)

    def login(self):
        url = 'https://passport.ustc.edu.cn/login'
        service = 'https://weixine.ustc.edu.cn/2020/caslogin'

        res = self.session.get(url+'?service='+service)
        soup = BeautifulSoup(res.text, 'html.parser')
        res = self.session.post(url, data={
            'model': 'uplogin.jsp',
            'service': service,
            'username': self.stuid,
            'password': str(self.password),
            'warn': '',
            'showCode': '',
            'button': '',
            'CAS_LT': soup.find('input', {'name': 'CAS_LT'})['value'],
            'LT': '',
        })
        return (res.url != url)

    def report(self):
        url = 'https://weixine.ustc.edu.cn/2020/daliy_report'

        cookies = self.session.cookies
        headers = {
            'authority': 'weixine.ustc.edu.cn',
            'origin': 'https://weixine.ustc.edu.cn',
            'upgrade-insecure-requests': '1',
            'content-type': 'application/x-www-form-urlencoded',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.100 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'referer': 'https://weixine.ustc.edu.cn/2020/home',
            'accept-language': 'zh-CN,zh;q=0.9',
            'Connection': 'close',
            'cookie': 'PHPSESSID=' + cookies.get('PHPSESSID') + ';XSRF-TOKEN=' + cookies.get('XSRF-TOKEN') + ';laravel_session='+cookies.get('laravel_session'),
        }

        res = self.session.get('https://weixine.ustc.edu.cn/2020')
        soup = BeautifulSoup(res.text, 'html.parser')
        form = soup.find('div', {'id': 'daliy-report'})

        data = {}

        for row in form.find_all('input', {'type': 'hidden'}):
            data[row['name']] = row['value']

        for row in form.find_all('input', {'type': 'text'}):
            data[row['name']] = row['value']

        for row in form.find_all('input', {'type': 'radio', 'checked': True}):
            data[row['name']] = row['value']

        for row in form.find_all('select'):
            data[row['name']] = row.find('option', {'selected': True})['value']

        for row in form.find_all('textarea'):
            data[row['name']] = row.contents[0] if len(
                row.contents) > 0 else ''

        res = self.session.post(url, data=data, headers=headers)
        return ('上报成功' in res.text)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='USTC auto report script.')
    parser.add_argument('--stuid', nargs='+',
                        help='your student number', required=True)
    parser.add_argument('--password', nargs='+',
                        help='your CAS password', required=True)
    args = parser.parse_args()
    for stuid, password in zip(args.stuid, args.password):
        print(f'Report for {stuid}.')
        Report(stuid=stuid, password=password).run()
