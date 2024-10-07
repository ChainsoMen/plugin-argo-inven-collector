import logging
import argocd_client
from xml.etree import ElementTree as ET

from spaceone.core.connector import BaseConnector

_LOGGER = logging.getLogger(__name__)

class ArgoConnector(BaseConnector):
    def __init__(self, url: str, username: str, password: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        
        #임시로 인증서 검증 비활성화 (개발 환경에서만 사용)
        self.config.verify_ssl = False
        #세션 생성
        self.sessionRequest = argocd_client.SessionSessionCreateRequest(username=username, password=password)
        temp_client = argocd_client.ApiClient(configuration=argocd_client.Configuration(host=url))
        api_instance = argocd_client.SessionServiceApi(temp_client)
        
        try:
            api_instance.create_mixin11(self.sessionRequest)
            self.token = temp_client.last_response.getheaders().get('Set-Cookie').split(';')[0]
        except Exception as e:
            _LOGGER.error(f"Error creating session: {e}")
            return []
        
        self.client = argocd_client.ApiClient(configuration=argocd_client.Configuration(host=url), cookie=self.token)
    
    def get_applications(self):
        try:
            api_instance = argocd_client.ApplicationServiceApi(self.client)
            api_response = api_instance.list_mixin9()
            return api_response
        except Exception as e:
            _LOGGER.error(f"Error fetching applications from Argo CD: {e}")
            return []