import os
import time

import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.utils import formataddr

from mcs.api import McsAPI
from mcs.contract import ContractAPI

mail_user = 'zhchen@nbai.io'
mail_pass = '17681768asA'
mail_host = "smtp.office365.com"
sender = ''

class AutoUpload():
    
    def __init__(self, wallet_address, private_key, rpc_url, file_path, email_address=None):
        self.wallet_address = wallet_address
        self.private_key = private_key
        self.web3_api = rpc_url
        
        self.file_path = file_path
        self.file_name = os.path.basename(self.file_path)

        self.email_address = email_address

    def auto_upload(self):
        file_status = self.upload_pay()
        self.check_detail_status()
        return

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
        return

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
        message['From'] = formataddr(('Swan', sender))
        message['To'] = receiver
        message['Subject'] = Header(sub, 'utf-8')
        with smtplib.SMTP(mail_host, 587) as server:
            server.starttls()
            server.ehlo()
            server.login(mail_user, mail_pass)
            server.sendmail(sender, receiver, message.as_string())