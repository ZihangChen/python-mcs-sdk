import os
import time
from configparser import ConfigParser

import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.utils import formataddr

from mcs.api import McsAPI
from mcs.contract import ContractAPI

class AutoUpload():
    
    def __init__(self, wallet_address, private_key, web3_api, file_path, email_address=None):
        self.wallet_address = wallet_address
        self.private_key = private_key
        self.web3_api = web3_api
        
        self.file_path = file_path
        self.file_name = os.path.basename(self.file_path)

        self.email_address = email_address

        with ConfigParser() as conf:
            conf.read('config.ini')
            self.mail_user = conf['MailInfo']['user']
            self.mail_pass = conf['MailInfo']['password']
            self.mail_host = conf['MailInfo']['host']
            self.sender = conf['MailInfo']['sender']


    def auto_upload(self):
        self.upload_pay()
        status = self.check_detail_status()
        return status

    def upload_pay(self):
        w3_api = ContractAPI(self.web3_api)
        api = McsAPI()

        # upload file
        upload_file = api.upload_file(self.wallet_address, self.file_path)
        
        file_data = upload_file["data"]
        payload_cid, source_file_upload_id, nft_uri, file_size, w_cid = file_data['payload_cid'], file_data[
        'source_file_upload_id'], file_data['ipfs_url'], file_data['file_size'], file_data['w_cid']
        params = api.get_params()["data"]
        rate = api.get_price_rate()["data"]

        # payment
        w3_api.upload_file_pay(self.wallet_address, self.private_key, file_size, w_cid, rate, params)

    def check_detail_status(self):
        api = McsAPI()
        task_detail = api.get_user_tasks_deals(self.wallet_address, self.file_name)
        deal = task_detail['data']['source_file_upload'][0]
        source_file_upload_id = deal['source_file_upload_id']
        deal_id = deal['offline_deal']['deal_id']

        start_time = time.time()
        current_time = time.time()
        while current_time-start_time > 43200:
            deal_status = api.get_deal_detail(self.wallet_address, source_file_upload_id, deal_id)
            if deal_status['data']['source_file_upload_dea']['verified_deal']:
                self.notification_email(sub='MCS', message='Upload sucessfully')
                return True
            time.sleep(1800)
        self.notification_email(message='MCS', message='Upload unsucessful')
        return False
            
    def notification_email(self, sub, msg):
        receiver = self.email_address

        message = MIMEText(msg, 'html', 'utf-8')
        message['From'] = formataddr(('Swan', self.sender))
        message['To'] = receiver
        message['Subject'] = Header(sub, 'utf-8')
        with smtplib.SMTP(self.mail_host, 587) as server:
            server.starttls()
            server.ehlo()
            server.login(self.mail_user, self.mail_pass)
            server.sendmail(self.sender, receiver, message.as_string())