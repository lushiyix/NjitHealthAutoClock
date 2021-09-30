# Njit Health AutoClock
## 声明
本项目是在若离的今日校园签到项目上进行的二次开发，因此部分项目文件中保留有若离作者的信息

本项目实现了南京工程学院金智体温自动打卡的功能，可下载搭配`腾讯云函数`食用

本项目仅供交流学习使用，严禁用于代挂等收费相关业务，如作他用所产生的一系列法律责任均与作者无关

[若离项目地址](https://github.com/thriving123/fuckTodayStudy)

## 项目说明
- `system.yml`腾讯云ocr配置文件

- `test.yml`测试程序功能的配置文件

- `userConfig.yml`用户信息配置文件

- `requirements.txt`py依赖库及版本说明文件

- `AutoClock.py`实现打卡功能的py脚本

- `NjitLogin.py`实现登录功能的py脚本

- `Utils`实现加密及验证码识别功能的py脚本

- `index.py`程序执行入口

## 使用教程
1.在`userConfig.yml`中配置用户信息

2.邮箱通知，由于本人开发时使用了`smtplib`模块发送QQ邮箱通知，因此需要在`Utils.sendEmail()`中填入发送方账号与授权码，此功能需要开启QQ邮箱的SMTP服务，[开启SMTP服务](https://jingyan.baidu.com/article/425e69e61e9178be15fc168a.html)，若不使用则将`isNoticeOpen`设为`false`即可

3.验证码识别，由于学校登录需要验证码识别，因此需要配置`system.yml`，[开启腾讯云ocr服务](https://cloud.tencent.com/document/product/866/17622)

4.安装依赖，在Python IDE终端下执行`pip3 install -r requirements.txt -t ./ -i https://mirrors.aliyun.com/pypi/simple` 即可运行程序

5.部署，只有部署之后设置定时任务才能实现自动打卡，部署可选择`腾讯云函数`、`阿里云函数计算`或`自己电脑`，具体操作可阅读[若离项目文档](https://github.com/thriving123/fuckTodayStudy)，此处不再做介绍

## 更新
- 新增住宿信息
