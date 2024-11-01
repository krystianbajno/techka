from techka.auth.auth_service import AuthService

class ServiceProvider:
    def __init__(self):
        self.auth_service = AuthService()

    def get_auth_service(self):
        return self.auth_service
