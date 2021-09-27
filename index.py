# coding=utf-8
# @Time : 2021/9/25 15:48
# @Author : 黄鸿林
# @File : index.py
# @Software : PyCharm
import yaml

from todaySchool.utils.Utils import Utils
from todaySchool.login.NjitLogin import NjitLogin
from todaySchool.actions.AutoClock import AutoClock

def getConfig(yaml_file='config/userConfig.yml'):
    file=open(yaml_file,'r',encoding='utf8')
    file_data=file.read()
    file.close()
    config=yaml.load(file_data,Loader=yaml.FullLoader)
    return dict(config)

def main():
    config=getConfig()
    for user in config['users']:
        if config['debug']:
            msg=working(user)
            print(msg)
        else:
            try:
                msg=working(user)
            except Exception as e:
                msg=str(e)
            print(msg)
        if user['user']['isNoticeOpen']:
            if '打卡成功' in msg:
                if user['user']['isNotice']:
                    Utils.sendEmail(user['user']['email'], msg)
            elif '打卡失败' in msg:
                Utils.sendEmail(user['user']['email'], msg)
            else:
                Utils.sendEmail(user['user']['email'], msg)


def working(user):
    count = 0
    msg = '无效的验证码'
    while '无效的验证码' in msg or '连接尝试失败' in msg and count < 3:
        try:
            njitLogin = NjitLogin(user['user'])
            msg = njitLogin.login()
        except Exception as e:
            msg = str(e)
        count += 1
    print(msg)
    if '无效的验证码' in msg or '连接尝试失败' in msg:
        return '验证码识别未通过，打卡失败，请手动打卡'
    if user['user']['type']==0:
        # 以下代码是信息收集的代码
        pass
    elif user['user']['type']==1:
        # 签到
        pass
    elif user['user']['type'] == 3:
        # 打卡
        clock = AutoClock(njitLogin, user['user'])
        msg = clock.start()
        return msg

def main_handler(event,context):
    main()
    return '执行成功！'

if __name__=='__main__':
    main()