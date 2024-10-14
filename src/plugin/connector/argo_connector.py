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

    def get_application_details(self, app_name: str):
        try:
            app_details_url = f"{self.url}/api/v1/applications/{app_name}"
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(app_details_url, headers=headers, verify=False)
            response.raise_for_status()
            details = response.json()
            return {
                "metadata": details['metadata'],
                "spec": details['spec'],
                "status": details['status'],
                "operationState": details.get('status', {}).get('operationState', {}),
                "conditions": details.get('status', {}).get('conditions', []),
                "history": details.get('status', {}).get('history', [])
            }
        except Exception as e:
            _LOGGER.error(f"Error fetching application details for {app_name} from ArgoCD: {e}")
            return {}