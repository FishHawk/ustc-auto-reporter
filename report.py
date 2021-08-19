# encoding=utf8
import requests
import json
import datetime
import pytz
import re
import argparse
from bs4 import BeautifulSoup


def retry(n, function):
    if (function()):
        return True
    for _ in range(n - 1):
        print("Retrying...")
        if (function()):
            return True
    return False


class Report(object):
    def __init__(self, stuid, password, data_path):
        self.stuid = stuid
        self.password = password
        self.data_path = data_path

    def run(self):
        print("Login...")
        if retry(5, self.login):
            print("Login Successful!")
        else:
            print("Login Failed!")
            exit(-1)

        print("Report...")
        if retry(5, self.report):
            print("Report Successful!")
        else:
            print("Report Failed!")
            exit(-1)


    def login(self):
        self.session = requests.Session()

        url = "https://passport.ustc.edu.cn/login?service=https%3A%2F%2Fweixine.ustc.edu.cn%2F2020%2Fcaslogin"

        res = self.session.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        cas_lt = soup.find("input", {"name": "CAS_LT"})['value']

        self.session.post(url, data={
            'model': 'uplogin.jsp',
            'service': 'https://weixine.ustc.edu.cn/2020/caslogin',
            'CAS_LT': cas_lt,
            'username': self.stuid,
            'password': str(self.password),
            'warn': '',
            'showCode': '',
            'button': '',
        })

        res = self.session.get("https://weixine.ustc.edu.cn/2020")
        success = (res.url == "https://weixine.ustc.edu.cn/2020/home")
        return success

    def report(self):
        url = "https://weixine.ustc.edu.cn/2020/daliy_report"

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
            'cookie': "PHPSESSID=" + cookies.get("PHPSESSID") + ";XSRF-TOKEN=" + cookies.get("XSRF-TOKEN") + ";laravel_session="+cookies.get("laravel_session"),
        }

        res = self.session.get("https://weixine.ustc.edu.cn/2020")
        soup = BeautifulSoup(res.text, 'html.parser')
        token = soup.find("input", {"name": "_token"})['value']
        with open(self.data_path, "r+") as f:
            data = f.read()
            data = json.loads(data)
            data["_token"] = token

        self.session.post(url, data=data, headers=headers)

        return self.is_report_success()

    def is_report_success(self):
        res = self.session.get("https://weixine.ustc.edu.cn/2020")
        soup = BeautifulSoup(res.text, 'html.parser')
        token = soup.find("span", {"style": "position: relative; top: 5px; color: #666;"})

        pattern = re.compile("202[0-9]-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}")
        if pattern.search(token.text) is not None:
            date = pattern.search(token.text).group()
            print("Latest report: " + date)
            date = date + " +0800"
            reporttime = datetime.datetime.strptime(
                date, "%Y-%m-%d %H:%M:%S %z")
            timenow = datetime.datetime.now(pytz.timezone('Asia/Shanghai'))
            delta = timenow - reporttime
            print("{} second(s) before.".format(delta.seconds))
            if delta.seconds < 120:
                return True
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='URC nCov auto report script.')
    parser.add_argument('data_path', help='path to your own data used for post method', type=str)
    parser.add_argument('stuid', help='your student number', type=str)
    parser.add_argument('password', help='your CAS password', type=str)
    args = parser.parse_args()
    Report(stuid=args.stuid, password=args.password, data_path=args.data_path).run()