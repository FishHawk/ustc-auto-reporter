# 中国科学技术大学健康打卡平台自动打卡脚本

这个脚本会使用最近一次打卡的信息自动打卡。如果需要修改打卡的信息（比如放假回家），只需要手动打一次，之后的自动打卡都会根据这一次信息打卡。

## 使用方法

### 使用Github workflow自动运行

1. 将本代码仓库fork到自己的github。

2. 点击Actions选项卡，启用workflow。

3. 点击Settings选项卡，创建两个repository secret.
   - 创建名为`STUID`的secret，值为学号。
   - 创建名为`PASSWORD`的secret，值为统一身份认证密码。
   - 如果要为多人打卡，可以使用空格作为分隔符。注意学号要与密码数目一致。
4. 默认的打卡时间是每天的早上7:30、中午12:30和晚上19:30，可能会有数分钟的浮动。如需选择其它时间，可以修改`.github/workflows/report.yml`中的`cron`，详细说明参见[触发工作流程的事件](https://docs.github.com/cn/actions/reference/events-that-trigger-workflows#scheduled-events)，请注意这里使用的是**国际标准时间UTC**，北京时间的数值比它大8个小时。建议修改默认时间，避开打卡高峰期以提高成功率。
5. 在Actions选项卡可以确认打卡情况。如果打卡失败（可能是临时网络问题等原因），脚本会自动重试，三次尝试后如果依然失败，将返回非零值提示构建失败。
6. 在Github个人设置页面的Notifications下可以设置Github Actions的通知，建议打开Email通知，并勾选"Send notifications for failed workflows only"。

### 本地运行

要在本地运行测试，需要安装python 3。假设您已经安装了python3和pip3，并已将其路径添加到环境变量，则可以使用下面的命令安装需要的库。

```shell
pip install -r requirements.txt
```

脚本的使用方式如下。

```shell
usage: report.py [-h] --stuid STUID [STUID ...] --password PASSWORD [PASSWORD ...]

USTC auto report script.

options:
  -h, --help							show this help message and exit
  --stuid STUID [STUID ...]				your student number
  --password PASSWORD [PASSWORD ...]	your CAS password
```
其中，`STUID`是学号，`PASSWORD`是统一身份认证的密码。支持多个学号密码，可以使用空格作为分隔符。
