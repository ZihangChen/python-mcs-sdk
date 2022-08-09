from apscheduler.schedulers.background import BackgroundScheduler
from auto_upload import AutoUpload
from configparser import ConfigParser

def daily_upload():
    with ConfigParser() as conf:
            conf.read('config.ini')
            wallet_address = conf['WalletInfo']['wallet_address']
            private_key = conf['WalletInfo']['private_key']
            web3_api = conf['WalletInfo']['web3_api']
            file_path = conf['FileInfo']['file_path']
            email_address = conf['MailInfo']['receiver']
    up = AutoUpload(wallet_address, private_key, web3_api, file_path, email_address)
    up.auto_upload()

scheduler = BackgroundScheduler

scheduler.add_job(
    daily_upload,
    trigger='interval',
    days=1
)

scheduler.start()