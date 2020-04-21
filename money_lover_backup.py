import requests
import csv
import os
import uuid
from datetime import datetime
from os import path
from requests.auth import AuthBase

# define api endpoints
wallets_endpoint = 'https://web.moneylover.me/api/wallet/list'
transactions_endpoint = 'https://web.moneylover.me/api/transaction/list'
transaction_csv_headers = ['']


# authenticator class used for passing authorization header to money-lovers api
class TokenAuth(AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers['authorization'] = f'{self.token}'
        return r


# fetches wallets and creates backups for them
def fetch_wallets(jwt_token):
    wallets = requests.post(wallets_endpoint, {}, auth=TokenAuth(jwt_token)).json()

    # backup wallets
    wallets = wallets['data']

    # get current script location
    dir_path = os.getcwd()

    # create all missing directories
    if not path.exists(dir_path + '/backups'):
        os.mkdir(dir_path + '/backups')

    if not path.exists(dir_path + '/backups/wallets'):
        os.mkdir(dir_path + '/backups/wallets')

    if not path.exists(dir_path + '/backups/transactions'):
        os.mkdir(dir_path + '/backups/transactions')

    uuid_int = uuid.uuid1().hex
    with open(dir_path + '/backups/wallets/wallets_' + uuid_int + '.csv', 'w', newline='') as wallet_backup_csv:
        for wallet in wallets:
            wallet_balance = wallet['balance'][0]

            for key, value in wallet_balance.items():
                balance = value
                currency = key

            writer = csv.writer(wallet_backup_csv, delimiter=',')
            writer.writerow(
                ['wallet_id', 'wallet_name', 'archived', 'created_at', 'updated_at', 'is_deleted', 'balance',
                 'currency'])
            writer.writerow([wallet['_id'], wallet['name'], wallet['archived'], wallet['createdAt'], wallet['updateAt'],
                             wallet['isDelete'], balance, currency])

    return wallets


# fetches all the transaction for the given period
def fetch_transactions(wallet_id, start_date, end_date, jwt_auth):
    transactions = requests.post(transactions_endpoint, data={
        'walletId': wallet_id,
        'startDate': start_date,
        'force': 'true',
        'endDate': end_date
    }, auth=TokenAuth(jwt_auth)).json()

    return transactions['data']['transactions']


if __name__ == '__main__':
    # ask for date and jwt
    date_from = input("Give me from which date to backup (2019-01-01 with format year-month-day): ")
    date_to = input("Give me to which date to backup (2020-01-01 with format year-month-day): ")
    jwt_token = input("Give me your jwt auth token: ")

    wallets = fetch_wallets(jwt_token)
    dir_path = os.getcwd()

    transaction_backup_dir = dir_path + '/backups/transactions/backup_' + datetime.today().strftime('%Y-%m-%d_%H-%M-%S')

    if not path.exists(transaction_backup_dir):
        os.mkdir(transaction_backup_dir)

    for wallet in wallets:

        # data required for transaction fetching
        wallet_id = wallet['_id']
        wallet_name = wallet['name']

        # get all transactions for given period
        transactions = fetch_transactions(wallet_id, date_from, date_to, jwt_token)

        # extract keys for header in csv
        header = dict()
        if len(transactions) != 0:
            header = transactions[0].keys()

        if len(header) != 0:
            with open(transaction_backup_dir + '/' + wallet_name + '.csv', 'w', newline='') as wallet_backup_csv:
                writter = csv.writer(wallet_backup_csv, delimiter=',')
                writter.writerow(header)
                for transaction in transactions:
                    writter.writerow(transaction.values())

    print('Wallets and transactions have been backed up')
