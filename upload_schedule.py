from apscheduler.schedulers.background import BackgroundScheduler
from auto_upload import AutoUpload
import toml

def daily_upload():
    config = toml.load("config.toml")
    wallet_address = config['WalletInfo']['wallet_address']
    private_key = config['WalletInfo']['private_key']
    web3_api = config['WalletInfo']['web3_api']
    file_path = config['FileInfo']['file_path']
    up = AutoUpload(wallet_address, private_key, web3_api, file_path)
    up.auto_upload()

scheduler = BackgroundScheduler

scheduler.add_job(
    daily_upload,
    trigger='interval',
    days=1
)

scheduler.start()