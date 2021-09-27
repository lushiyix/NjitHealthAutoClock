# coding=utf-8
# @Time : 2021/9/25 15:46
# @Author : 黄鸿林
# @File : NjitLogin.py
# @Software : PyCharm
import re,requests
from bs4 import BeautifulSoup
from todaySchool.utils.Utils import Utils


class NjitLogin:
    # 初始化
    def __init__(self, userInfo):
        self.userInfo = userInfo
        self.setUserInfo(self.userInfo)

    # 初始化用户信息
    def setUserInfo(self, userInfo):
        if None == userInfo['username'] or '' == userInfo['username'] or None == userInfo['password'] or '' == userInfo['password']:
            raise Exception('初始化失败，请输入正确参数（用户名，密码，学校）')
        self.username = userInfo['username']
        self.password = userInfo['password']
        self.session = requests.session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; U; Android 8.1.0; zh-cn; BLA-AL00 Build/HUAWEIBLA-AL00) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.132 MQQBrowser/8.9 Mobile Safari/537.36',
        }
        self.session.headers = headers
        self.host = 'https://ensdp.njit.edu.cn:10443/http/webvpn617574687365727665722e6e6a69742e6564752e636e/'
        self.login_url = f'{self.host}authserver/login?service=https://ensdp.njit.edu.cn/enlink/api/client/auth/cas'

    # 判断是否需要验证码
    def getNeedCaptchaUrl(self):
        host = re.findall('\w{4,5}\:\/\/.*?\/', self.login_url)[0]
        url = host + 'authserver/needCaptcha.html' + '?username=' + self.username
        flag = self.session.get(url, verify=False).text
        return 'false' != flag and 'False' != flag

    def login(self):
        html = self.session.get(self.login_url, verify = False).text
        soup = BeautifulSoup(html, 'lxml')
        form = soup.select('#casLoginForm')
        if(len(form)==0):
            raise Exception('网页加载出错！')
        # 填充数据
        params={}
        form=soup.select('input')
        for item in form:
            if None != item.get('name') and len(item.get('name'))>0:
                if item.get('name')!='rememberMe':
                    if None == item.get('value'):
                        params[item.get('name')]=''
                    else:
                        params[item.get('name')]=item.get('value')
        salt = soup.select('#pwdDefaultEncryptSalt')
        if(len(salt)!=0):
            salt = salt.get_text()
        else:
            pattern = '\"(\w{16})\"'
            salt = re.findall(pattern, html)
            if(len(salt)==1):
                salt = salt[0]
            else:
                salt = False
        params['username']=self.username
        if not salt:
            params['password']=self.password
        else:
            params['password']= Utils.encryptAES(self.password, salt)
            if self.getNeedCaptchaUrl():
                imgUrl = self.host + 'authserver/captcha.html'
                code = Utils.getCodeFromImg(self.session, imgUrl)
                params['captchaResponse'] = code
        data=self.session.post(self.login_url,params=params,allow_redirects=False)
        # 如果等于302强制跳转，代表登陆成功
        if data.status_code == 302:
            jump_url=data.headers['Location']
            self.session.post(jump_url,verify=False)
            return '登录成功'
        elif data.status_code==200:
            data=data.text
            soup=BeautifulSoup(data,'lxml')
            msg=soup.select('#errorMsg')[0].get_text()
            raise Exception(msg)
        else:
            raise Exception('教务系统出现问题！返回状态码'+str(data.status_code))