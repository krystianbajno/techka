import json
from telethon.sync import TelegramClient

class TelegramClientManager:
    def __init__(self, auth_service):
        self.auth_service = auth_service
        self.client = None
        
        self.identity = self._get_identity()

        self.api_id, self.api_hash = self._get_api_credentials(self.identity)
        
        self.phone_number = self.identity.get('phone_number')
        if not self.phone_number:
            raise ValueError("Phone number not found in identity. Cannot proceed.")
        
        self._initialize_client()

    def _get_identity(self):
        """Retrieve or create a new identity if one doesn't exist."""
        identity = self.auth_service.get_any_identity_for('Telegram')
        if not identity:
            print("No existing identity found; creating a new one.")
            identity = self.login_and_store_identity(api_id=None, api_hash=None)
        return identity

    def _get_api_credentials(self, identity):
        """Fetch or prompt for API credentials and update identity if necessary."""
        cookies = identity.get('cookies', {})
        api_id = cookies.get('api_id')
        api_hash = cookies.get('api_hash')

        if not api_id or not api_hash:
            print("API credentials not found. Please enter them.")
            api_id = input("Enter your Telegram API ID: ")
            api_hash = input("Enter your Telegram API Hash: ")

            self.auth_service.update_identity(
                'Telegram',
                identity.get('identity_name'),
                cookies=json.dumps({'api_id': api_id, 'api_hash': api_hash})
            )
            print("API credentials stored successfully.")
        
        return api_id, api_hash

    def _initialize_client(self):
        """Set up the Telegram client using the session file or create a new session if not available."""
        session_file = self.identity.get('session_file', f"telegram_session_{self.phone_number}")
        self.client = TelegramClient(session_file, self.api_id, self.api_hash)
        
        self.client.connect()
        if not self.client.is_user_authorized():
            self.login_and_store_identity(api_id=self.api_id, api_hash=self.api_hash)

    def login_and_store_identity(self, api_id=None, api_hash=None):
        if not api_id or not api_hash:
            temp_identity = self.auth_service.get_any_identity_for('Telegram') or {}
            api_id, api_hash = self._get_api_credentials(temp_identity)

        phone_number = input("Enter your phone number for Telegram: ")
        
        session_file = f'telegram_session_{phone_number}'
        if not self.client:
            self.client = TelegramClient(session_file, api_id, api_hash)
            self.client.connect()

        if not self.client.is_user_authorized():
            self.client.send_code_request(phone_number)
            code = input('Enter the code you received: ')
            self.client.sign_in(phone_number, code)
                
        self.auth_service.add_identity(
            service_name='Telegram',
            identity_name='NewIdentity',
            phone_number=phone_number,
            session_file=session_file,
            cookies={'api_id': api_id, 'api_hash': api_hash}
        )
        print(f"Logged in and session saved as '{session_file}'.")

        return self.auth_service.get_any_identity_for('Telegram')

    def get_client(self):
        """Return the initialized and authenticated Telegram client."""
        return self.client


