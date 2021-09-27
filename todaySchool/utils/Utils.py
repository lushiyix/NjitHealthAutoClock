# coding=utf-8
# @Time : 2021/9/25 15:48
# @Author : 黄鸿林
# @File : Utils.py
# @Software : PyCharm
import base64
import json
import random
from io import BytesIO

import yaml
from Crypto.Cipher import AES
from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.ocr.v20181119 import ocr_client, models

import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from email.header import Header

class Utils:
    def __init__(self):
        pass

    # 获取指定长度的随机字符
    @staticmethod
    def randString(length):
        baseString = "ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678"
        data = ''
        for i in range(length):
            data += baseString[random.randint(0, len(baseString) - 1)]
        return data
    @staticmethod
    def getYmlConfig(yaml_file='config/system.yml'):
        file = open(yaml_file, 'r', encoding="utf-8")
        file_data = file.read()
        file.close()
        config = yaml.load(file_data, Loader=yaml.FullLoader)
        return dict(config)

    # aes加密的实现
    @staticmethod
    def encryptAES(password, key):
        randStrLen = 64
        randIvLen = 16
        ranStr = Utils.randString(randStrLen)
        ivStr = Utils.randString(randIvLen)
        aes = AES.new(bytes(key, encoding='utf-8'), AES.MODE_CBC, bytes(ivStr, encoding="utf8"))
        data = ranStr + password

        text_length = len(data)
        amount_to_pad = AES.block_size - (text_length % AES.block_size)
        if amount_to_pad == 0:
            amount_to_pad = AES.block_size
        pad = chr(amount_to_pad)
        data = data + pad * amount_to_pad

        text = aes.encrypt(bytes(data, encoding='utf-8'))
        text = base64.encodebytes(text)
        text = text.decode('utf-8').strip()
        return text

    @staticmethod
    def getCodeFromImg(res, imgUrl):
        response = res.get(imgUrl, verify=False)  # 将这个图片保存在内存
        # 得到这个图片的base64编码
        imgCode = str(base64.b64encode(BytesIO(response.content).read()), encoding='utf-8')
        # print(imgCode)
        try:
            cred = credential.Credential(Utils.getYmlConfig()['SecretId'], Utils.getYmlConfig()['SecretKey'])
            httpProfile = HttpProfile()
            httpProfile.endpoint = "ocr.tencentcloudapi.com"

            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            client = ocr_client.OcrClient(cred, "ap-beijing", clientProfile)

            req = models.GeneralBasicOCRRequest()
            params = {
                "ImageBase64": imgCode
            }
            req.from_json_string(json.dumps(params))
            resp = client.GeneralBasicOCR(req)
            codeArray = json.loads(resp.to_json_string())['TextDetections']
            code = ''
            for item in codeArray:
                code += item['DetectedText'].replace(' ', '')
            if len(code) == 4:
                return code
            else:
                return Utils.getCodeFromImg(res, imgUrl)
        except TencentCloudSDKException as err:
            raise Exception('验证码识别出现问题了' + str(err.message))

    @staticmethod
    def sendEmail(to_addr,msg):
        # 发送方账号
        from_addr = ''
        # 授权码
        password = ''
        # 发件服务器
        smtp_server = 'smtp.qq.com'
        msg = MIMEText(msg, 'plain', 'utf8')
        # 邮件头信息
        msg['From'] = formataddr(['发件人：', from_addr])
        msg['To'] = Header(to_addr)
        msg['Subject'] = Header('今日校园签到')
        # 开启发信服务，使用SSL加密传输
        server = smtplib.SMTP_SSL(host=smtp_server)
        server.connect(smtp_server, 465)
        # 登录邮箱
        server.login(from_addr, password)
        # 发送邮件
        server.sendmail(from_addr, to_addr, msg.as_string())
        # 关闭服务器
        server.quit()