import os
import time
import toml

import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.utils import formataddr

from mcs.api import McsAPI
from mcs.contract import ContractAPI

class AutoUpload():
    
    def __init__(self, wallet_address, private_key, web3_api, file_path):
        self.wallet_address = wallet_address
        self.private_key = private_key
        self.web3_api = web3_api
        
        self.file_path = file_path
        self.file_name = os.path.basename(self.file_path)

        config = toml.load("config.toml")
        self.mail_user = config['MailInfo']['user']
        self.mail_pass = config['MailInfo']['password']
        self.mail_host = config['MailInfo']['host']

    def auto_upload(self):
        try:
            self.upload_pay()
        except Exception as e:
            self.notification_email(sub='MCS', msg='Upload erro \n' + e)
        
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
        w3_api.approve_usdc(self.wallet_address, self.private_key, "1")
        w3_api.upload_file_pay(self.wallet_address, self.private_key, file_size, w_cid, rate, params)

    def check_detail_status(self):
        api = McsAPI()

        start_time = time.time()
        current_time = time.time()
        while current_time-start_time < 43200:
            task_detail = api.get_user_tasks_deals(self.wallet_address, self.file_name)
            deal = task_detail['data']['source_file_upload'][0]
            source_file_upload_id = deal['source_file_upload_id']
            if deal['offline_deal']:
                deal_id = deal['offline_deal'][0]['deal_id']
                deal_status = api.get_deal_detail(self.wallet_address, source_file_upload_id, str(deal_id))
                if deal_status['data']['source_file_upload_deal']['unlocked']:
                    self.notification_email(sub='MCS', msg='Unlock successful')
                    return True
            time.sleep(1800)
            current_time = time.time()
        self.notification_email(sub='MCS', msg='Unlock unsucessful')
        return False
            
    def notification_email(self, sub, msg):
        message = MIMEText(msg, 'html', 'utf-8')
        message['From'] = formataddr(('Swan', self.mail_user))
        message['To'] = self.mail_user
        message['Subject'] = Header(sub, 'utf-8')
        with smtplib.SMTP(self.mail_host, 587) as server:
            server.starttls()
            server.ehlo()
            server.login(self.mail_user, self.mail_pass)
            server.sendmail(self.mail_user, self.mail_user, message.as_string())