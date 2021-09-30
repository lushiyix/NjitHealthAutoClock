# coding=utf-8
# @Time : 2021/9/25 15:47
# @Author : 黄鸿林
# @File : AutoClock.py
# @Software : PyCharm

class AutoClock:
    # 初始化
    def __init__(self, njitLogin, userInfo):
        self.session = njitLogin.session
        self.host = njitLogin.host
        self.userInfo = userInfo
        self.taskInfo = None
        self.task = None
        self.previousTask = None
        self.form = {}
        self.taskWid = None
        self.fileName = None
        self.healthInfo_Host = 'https://ensdp.njit.edu.cn:10443/http/webvpn6568616c6c6170702e6e6a69742e6564752e636e/'

    # 进入任务页
    def enterTaskPage(self):
        url = f'{self.healthInfo_Host}publicapp/sys/lwNjitHealthInfoDailyClock/index.do'
        self.session.get(url)

    # 通过请求对应链接获取用户信息
    def getUserInfo(self):
        url = f'{self.healthInfo_Host}publicapp/sys/lwNjitHealthInfoDailyClock/modules/healthClock/V_LWPUB_JKDK_QUERY.do'
        user = self.session.post(url).json()['datas']['V_LWPUB_JKDK_QUERY']['rows'][0]
        self.userID = user['USER_ID']           # 学号
        self.userName = user['USER_NAME']
        self.deptCode = user['DEPT_CODE']
        self.deptName = user['DEPT_NAME']
        print(f'userID: {self.userID} userName: {self.userName}\n'
              f'deptCode: {self.deptCode} deptName: {self.deptName}')


    # 通过配置文件获取用户基本信息
    def fillInfo(self):
        self.userID = self.userInfo['username']         # 学号
        self.userName = self.userInfo['name']
        self.deptCode = self.userInfo['deptCode']
        self.deptName = self.userInfo['deptName']
        self.StuAccommodationInfo = self.userInfo['StuAccommodationInfo']

    # 获取时间
    def getFillTime(self):
        url = f'{self.healthInfo_Host}publicapp/sys/lwpub/api/getServerTime.do?enlink-vpn'
        self.date = self.session.post(url).json()['date']
        self.date = str(self.date).replace('/', '-')
        self.hour = int(self.date.split(' ')[1].split(':')[0])

    # 填充表单
    def fillForm(self):
        self.form['USER_ID'] = self.userID
        self.form['USER_NAME'] = self.userName
        self.form['DEPT_CODE'] = self.deptCode
        self.form['DEPT_NAME'] = self.deptName
        self.form['BY2'] = self.StuAccommodationInfo
        self.form['BY3'] = '002' if self.hour >= 12 else '001'
        self.form['PHONE_NUMBER'] = self.userInfo['phtoneNumber']
        self.form['CLOCK_SITUATION'] = self.userInfo['address']

        key = [
            'TODAY_SITUATION', 'TODAY_VACCINE_CONDITION', 'TODAY_BODY_CONDITION', 'TODAY_TEMPERATURE',
            'TODAY_HEALTH_CODE', 'TODAY_TARRY_CONDITION', 'TODAY_ISOLATE_CONDITION'
        ]
        userForms = self.userInfo['forms']
        for i in range(len(userForms)):
            self.form[key[i]] = userForms[i]['form']['value']

        self.form['FILL_TIME'] = self.date

    def submitForm(self):
        url = f'{self.healthInfo_Host}publicapp/sys/lwNjitHealthInfoDailyClock/modules/healthClock/T_HEALTH_DAILY_INFO_SAVE.do'
        res=self.session.post(url, data = self.form, verify=False)
        res = res.json()
        return self.userName + ' 打卡成功' if res['datas']['T_HEALTH_DAILY_INFO_SAVE'] == 1 else ' 打卡失败'

    def start(self):
        self.enterTaskPage()        # 进入任务页
        self.getFillTime()          # 获取时间

        self.fillInfo()             # 填充基本信息，多人打卡推荐

        # getUserInfo() 通过请求链接获取一些用户的基本信息，但不稳定，多人打卡不推荐
        # 若是不知道该方法内的四个基本信息如何填，可以先调用 getUserInfo() 获取信息
        # getUserInfo() 与 fillInfo() 所填数据一样
        # self.getUserInfo()

        self.fillForm()             # 填充表单
        msg = self.submitForm()     # 提交表单
        return msg