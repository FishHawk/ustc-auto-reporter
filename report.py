# encoding=utf8
import argparse
import requests
from bs4 import BeautifulSoup
import re
import pyjson5
import datetime
import pytz


def retry(n, function):
    if (function()):
        print('Successful!')
        return True
    for _ in range(n - 1):
        print('Retrying...')
        if (function()):
            print('Successful!')
            return True
    print('Fail!')
    return False


class Report(object):
    def __init__(self, stuid, password):
        self.stuid = stuid
        self.password = password
        self.session = requests.Session()

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

    def 每日报备(self):
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

        url = 'https://weixine.ustc.edu.cn/2020/daliy_report'
        res = self.session.post(url, data=data)
        return ('上报成功' in res.text)

    def 申请报备高新校区(self):
        res = self.session.get(
            'https://weixine.ustc.edu.cn/2020/apply/daliy/i?t=3')
        soup = BeautifulSoup(res.text, 'html.parser')
        form = soup.find('div', {'id': 'daliy-report'})

        now = datetime.datetime.now(pytz.timezone('Asia/Shanghai'))
        data = {
            'start_date': now.strftime('%Y-%m-%d %H:%m:%S'),
            'end_date': now.strftime('%Y-%m-%d 23:59:59'),
            'return_college[]': '高新校区',
            'reason': '实验室',
            't': 3,
        }
        for row in form.find_all('input', {'type': 'hidden'}):
            data[row['name']] = row['value']

        url = 'https://weixine.ustc.edu.cn/2020/apply/daliy/ipost'
        res = self.session.post(url, data=data)
        return ('报备成功' in res.text)

    def 健康信息上传(self):
        xcm_filename = 'xcm.jpg'
        hs_filename = 'hs.jpg'

        res = self.session.get('https://weixine.ustc.edu.cn/2020/upload/xcm')
        pattern = re.compile(r"formData[^}]*}", re.MULTILINE | re.DOTALL)
        formData = {}
        for (name, json) in zip(['行程码', '安康码', '核酸'], re.findall(pattern, str(res.text))):
            formData[name] = pyjson5.loads(json[len('formData:'):])

        url = 'https://weixine.ustc.edu.cn/2020img/api/upload_for_student'

        xcm_result = True
        if xcm_filename is not None:
            data = formData['行程码']
            files = {'file': open(xcm_filename, 'rb')}
            res = self.session.post(url, files=files, data=data)
            xcm_result = res.text.startswith('{"status":true,')

        hs_result = True
        if hs_filename is not None:
            data = formData['核酸']
            files = {'file': open(hs_filename, 'rb')}
            res = self.session.post(url, files=files, data=data)
            hs_result = res.text.startswith('{"status":true,')

        return xcm_result and hs_result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='USTC auto report script.')
    parser.add_argument(
        '--stuid',  required=True,
        help='你的学号'
    )
    parser.add_argument(
        '--password', required=True,
        help='你的统一身份认证的密码'
    )
    parser.add_argument(
        '--mrbb', default=False, action='store_true',
        help='执行每日报备.'
    )
    parser.add_argument(
        '--jkxxsc', default=False, action='store_true',
        help='执行健康信息上传.'
    )
    parser.add_argument(
        '--sqbb', default=False, action='store_true',
        help='执行申请报备(高新校区).'
    )
    args = parser.parse_args()

    report = Report(stuid=args.stuid, password=args.password)

    print('Login...')
    if not retry(3, report.login):
        exit(-1)

    if args.mrbb:
        print('每日报备...')
        retry(3, report.每日报备)

    if args.jkxxsc:
        print('健康信息上传...')
        retry(3, report.健康信息上传)

    if args.sqbb:
        print('申请报备高新校区...')
        retry(3, report.申请报备高新校区)
