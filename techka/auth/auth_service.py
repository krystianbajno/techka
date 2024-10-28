import sqlite3
import json
import time

class AuthService:
    def __init__(self, db_name='auth_service.db'):
        self.db_name = db_name
        self._initialize_database()

    def _initialize_database(self):
        self._execute_with_retry(self._create_identity_table)

    def _create_identity_table(self, cursor):
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

    def add_identity(self, service_name, identity_name, phone_number=None, email=None, username=None, password=None, session_file=None, cookies=None):
        """Add a new identity for a specific service."""
        def execute_add(cursor):
            cursor.execute('''
                INSERT INTO identity (service_name, identity_name, phone_number, email, username, password, session_file, cookies)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (service_name, identity_name, phone_number, email, username, password, session_file, json.dumps(cookies)))
            print(f'Identity "{identity_name}" for service "{service_name}" added successfully.')

        self._execute_with_retry(execute_add)

    def update_identity(self, service_name, identity_name, **kwargs):
        """Update an existing identity's details."""
        def execute_update(cursor):
            update_fields = []
            update_values = []
            for key, value in kwargs.items():
                update_fields.append(f"{key} = ?")
                update_values.append(value)
            
            update_query = f"UPDATE identity SET {', '.join(update_fields)} WHERE service_name = ? AND identity_name = ?"
            update_values.extend([service_name, identity_name])

            cursor.execute(update_query, update_values)
            print(f'Identity "{identity_name}" for service "{service_name}" updated successfully.')

        self._execute_with_retry(execute_update)

    def get_any_identity_for(self, service_name):
        """Retrieve an identity's details."""
        def execute_select(cursor):
            cursor.execute('SELECT * FROM identity WHERE service_name = ?', (service_name,))
            identity = cursor.fetchone()
            return identity if identity else None

        result = self._execute_with_retry(execute_select)
        if result:
            return {
                'service_name': result[1],
                'identity_name': result[2],
                'phone_number': result[3],
                'email': result[4],
                'username': result[5],
                'password': result[6],
                'session_file': result[7],
                'cookies': json.loads(result[8]) if result[8] else None
            }
        else:
            print(f'Identity for service "{service_name}" not found.')
            return None

    def _execute_with_retry(self, operation, max_retries=5, delay=0.1):
        """Retry logic for database operations to handle database locking."""
        attempt = 0
        while attempt < max_retries:
            try:
                with sqlite3.connect(self.db_name) as conn:
                    cursor = conn.cursor()
                    result = operation(cursor)
                    conn.commit()
                    return result
            except sqlite3.OperationalError as e:
                if 'database is locked' in str(e):
                    print("Database is locked, retrying...")
                    attempt += 1
                    time.sleep(delay)
                else:
                    raise
        raise sqlite3.OperationalError("Failed to execute operation due to database lock.")

