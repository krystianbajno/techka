import sqlite3
import json

class AuthService:
    def __init__(self, db_name='auth_service.db'):
        self.db_name = db_name
        self._initialize_database()

    def _initialize_database(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS identity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT NOT NULL,
                identity_name TEXT NOT NULL,
                phone_number TEXT,
                email TEXT,
                username TEXT,
                password TEXT,
                session_file TEXT,
                cookies TEXT,
                UNIQUE(service_name, identity_name)
            )
        ''')

        conn.commit()
        conn.close()

    def add_identity(self, service_name, identity_name, phone_number=None, email=None, username=None, password=None, session_file=None, cookies=None):
        """
        Add a new identity for a specific service.
        :param service_name: The name of the service (e.g., 'Telegram')
        :param identity_name: A unique name for the identity (e.g., 'MarketingBot1')
        :param phone_number: The phone number associated with the identity (optional)
        :param email: The email associated with the identity (optional)
        :param username: The username for the identity (optional)
        :param password: The password for the identity (optional)
        :param session_file: Path to the session file (optional)
        :param cookies: Cookies associated with the identity (optional)
        """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO identity (service_name, identity_name, phone_number, email, username, password, session_file, cookies)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (service_name, identity_name, phone_number, email, username, password, session_file, json.dumps(cookies)))
            conn.commit()
            print(f'Identity "{identity_name}" for service "{service_name}" added successfully.')
        except sqlite3.IntegrityError:
            print(f'Identity "{identity_name}" for service "{service_name}" already exists.')
        finally:
            conn.close()

    def update_identity(self, service_name, identity_name, **kwargs):
        """
        Update an existing identity's details.
        :param service_name: The name of the service
        :param identity_name: The unique name of the identity
        :param kwargs: Key-value pairs of attributes to update (e.g., email="new_email@example.com")
        """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        update_fields = []
        update_values = []
        for key, value in kwargs.items():
            update_fields.append(f"{key} = ?")
            update_values.append(value)

        update_query = f"UPDATE identity SET {', '.join(update_fields)} WHERE service_name = ? AND identity_name = ?"
        update_values.extend([service_name, identity_name])

        cursor.execute(update_query, update_values)
        conn.commit()
        conn.close()
        print(f'Identity "{identity_name}" for service "{service_name}" updated successfully.')

    def get_identity(self, service_name, identity_name):
        """
        Retrieve an identity's details.
        :param service_name: The name of the service
        :param identity_name: The unique name of the identity
        :return: Dictionary containing the identity details or None if not found
        """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM identity WHERE service_name = ? AND identity_name = ?
        ''', (service_name, identity_name))
        identity = cursor.fetchone()
        conn.close()

        if identity:
            return {
                'service_name': identity[1],
                'identity_name': identity[2],
                'phone_number': identity[3],
                'email': identity[4],
                'username': identity[5],
                'password': identity[6],
                'session_file': identity[7],
                'cookies': json.loads(identity[8]) if identity[8] else None
            }
        else:
            print(f'Identity "{identity_name}" for service "{service_name}" not found.')
            return None
