import json
from telethon.sync import TelegramClient

class TelegramClientManager:
    def __init__(self, auth_service, identity_name):
        self.auth_service = auth_service
        self.identity_name = identity_name
        self.client = None

        self.identity = self.auth_service.get_identity('Telegram', self.identity_name)
        if not self.identity:
            raise ValueError(f"Identity '{identity_name}' for Telegram not found in AuthService.")

        self.api_id, self.api_hash = self._get_api_credentials()
        self.phone_number = self.identity['phone_number']
        self._initialize_client()

    def _get_api_credentials(self):
        cookies = self.identity.get('cookies', {})
        api_id = cookies.get('api_id')
        api_hash = cookies.get('api_hash')

        if not api_id or not api_hash:
            api_id = input("Enter your Telegram API ID: ")
            api_hash = input("Enter your Telegram API Hash: ")

            self.auth_service.update_identity(
                'Telegram',
                self.identity_name,
                cookies=json.dumps({'api_id': api_id, 'api_hash': api_hash})
            )

        return api_id, api_hash

    def _initialize_client(self):
        session_file = self.identity.get('session_file')
        if session_file:
            self.client = TelegramClient(session_file, self.api_id, self.api_hash)
            self.client.connect()
            print('Loaded existing session.')
        else:
            self.client = TelegramClient('telegram_session', self.api_id, self.api_hash)
            self.client.connect()
            self.login_and_store_identity()

    def login_and_store_identity(self):
        if not self.client.is_user_authorized():
            self.client.send_code_request(self.phone_number)
            code = input('Enter the code you received: ')
            self.client.sign_in(self.phone_number, code)
        
        session_file = f'telegram_session_{self.phone_number}'
        self.client.session.save(session_file)
        print('Logged in successfully and session saved.')

        self.auth_service.update_identity(
            'Telegram',
            self.identity_name,
            session_file=session_file
        )

    def get_client(self):
        return self.client
