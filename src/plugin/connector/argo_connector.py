import logging
import requests
from spaceone.core.connector import BaseConnector

_LOGGER = logging.getLogger(__name__)

class ArgoConnector(BaseConnector):
    def __init__(self, url: str, username: str, password: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = url
        self.token = None
        
        self._login(username, password)

    def _login(self, username: str, password: str):
        try:
            login_url = f"{self.url}/api/v1/session"
            response = requests.post(login_url, json={"username": username, "password": password}, verify=False)
            response.raise_for_status()
            self.token = response.json()['token']
            _LOGGER.info(f"Logged in to ArgoCD at {self.url}")
        except Exception as e:
            _LOGGER.error(f"Error logging in to ArgoCD: {e}")
            raise

    def get_applications(self):
        try:
            apps_url = f"{self.url}/api/v1/applications"
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(apps_url, headers=headers, verify=False)
            response.raise_for_status()
            return response.json()['items']
        except Exception as e:
            _LOGGER.error(f"Error fetching applications from ArgoCD: {e}")
            return []
