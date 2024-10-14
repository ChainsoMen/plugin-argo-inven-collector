import logging
import os
from spaceone.core.manager import BaseManager
from spaceone.inventory.plugin.collector.lib import (
    make_cloud_service_type,
    make_cloud_service_with_metadata,
    make_error_response,
    make_response,
)
from plugin.connector.argo_connector import ArgoConnector

_LOGGER = logging.getLogger(__name__)
_CURRENT_DIR = os.path.dirname(__file__)
_METADATA_DIR = os.path.join(_CURRENT_DIR, "../metadata/")

class ArgoManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.provider = "argo"
        self.cloud_service_group = "CI/CD"
        self.cloud_service_type = "Application"
        self.metadata_path = os.path.join(_METADATA_DIR, "cicd/argo.yaml")

    def collect_resources(self, options, secret_data, schema):
        try:
            yield from self.collect_cloud_service_type()
            yield from self.collect_cloud_service(secret_data)
        except Exception as e:
            yield make_error_response(
                error=e,
                provider=self.provider,
                cloud_service_group=self.cloud_service_group,
                cloud_service_type=self.cloud_service_type,
            )

    def collect_cloud_service_type(self):
        cloud_service_type = make_cloud_service_type(
            name=self.cloud_service_type,
            group=self.cloud_service_group,
            provider=self.provider,
            metadata_path=self.metadata_path,
            is_primary=True,
            is_major=True,
        )
        yield make_response(
            cloud_service_type=cloud_service_type,
            match_keys=[["name", "reference.resource_id", "account", "provider"]],
            resource_type="inventory.CloudServiceType",
        )

    def collect_cloud_service(self, secret_data):
        argo_connector = ArgoConnector(
            url=secret_data['argo-server-url'],
            username=secret_data['argo-username'],
            password=secret_data['argo-password']
        )
        applications = argo_connector.get_applications()

        for app in applications:
            app_details = argo_connector.get_application_details(app['metadata']['name']) # 추가
            cloud_service = make_cloud_service_with_metadata(
                name=app['metadata']['name'],
                cloud_service_type=self.cloud_service_type,
                cloud_service_group=self.cloud_service_group,
                provider=self.provider,
                # data=app,
                data={"application": app, "details": app_details},
                data_format='dict',
                metadata_path=self.metadata_path,
            )
            yield make_response(
                cloud_service=cloud_service,
                match_keys=[['name', 'reference.resource_id', 'account', 'provider']],
            )
