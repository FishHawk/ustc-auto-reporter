# 中国科学技术大学健康打卡平台自动打卡脚本

这个脚本支持以下功能：
- 每日报备。使用最近一次打卡的信息，如果需要修改打卡的信息（比如放假回家），只需要手动打一次，之后脚本都会根据这一次信息打卡。
- 健康信息上传。会上传项目目录下的文件，`xcm.jpg`是行程码，`hs.jpg`是核算结果，需要自行push。
- 申请报备(高新校区)。只支持到高新校区的报备。

## 使用方法

### 使用Github workflow自动运行

1. 将本代码仓库fork到自己的github。

2. （可选）根据需要更新项目。
    - 默认只执行每日报备。如果需要其他功能，自行修改`.github/workflows/report.yml`
    - 如果想启用健康信息上传，需要在项目目录下添加`xcm.jpg`和`hs.jpg`，分别为行程码和核算截图。
    - 默认的打卡时间是每天的早上4:30和8:30。如果需要选择其它时间，可以修改`.github/workflows/report.yml`中的`cron`，详细说明参见[触发工作流程的事件](https://docs.github.com/cn/actions/reference/events-that-trigger-workflows#scheduled-events)，请注意这里使用的是**国际标准时间UTC**，北京时间的数值比它大8个小时。建议修改默认时间，避开打卡高峰期以提高成功率。

3. 点击Settings选项卡，创建两个repository secret.
    - 创建名为`STUID`的secret，值为学号。
    - 创建名为`PASSWORD`的secret，值为统一身份认证密码。

4. 点击Actions选项卡，启用workflow。在Actions选项卡可以确认打卡情况。如果打卡失败（可能是临时网络问题等原因），脚本会自动重试，三次尝试后如果依然失败，将失败。

5. （可选）在Github个人设置页面的Notifications下可以设置Github Actions的通知，建议打开Email通知，并勾选"Send notifications for failed workflows only"。

### 本地运行

要在本地运行测试，需要安装python3。假设您已经安装了python3和pip3，并已将其路径添加到环境变量，则可以使用下面的命令安装需要的库。

```shell
pip install -r requirements.txt
```

脚本的使用方式如下。

```shell
usage: report.py [-h] --stuid STUID --password PASSWORD [--mrbb] [--jkxxsc] [--sqbb]

USTC auto report script.

options:
  -h, --help           show this help message and exit
  --stuid STUID        你的学号
  --password PASSWORD  你的统一身份认证的密码
  --mrbb               执行每日报备.
  --jkxxsc             执行健康信息上传.
  --sqbb               执行申请报备(高新校区).
```

其中，健康信息上传会把目录下的`xcm.jpg`和`hs.jpg`文件视作行程码和核算截图。