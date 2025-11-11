import os
from PyQt6.QtWebEngineCore import (
    QWebEngineUrlRequestInfo,
    QWebEngineUrlRequestInterceptor,
)
import adblock

from browser.utils import setup_logging

ResourceType = QWebEngineUrlRequestInfo.ResourceType


class AdBlockInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.adblock_engine = None
        self.load_filters()
        self.logger = setup_logging()

    def load_filters(self):
        """Load adblock filter lists"""
        filter_lists = next(os.walk("filter_lists"), (None, None, []))[2]

        all_rules = []
        for filter_file in filter_lists:
            try:
                with open(filter_file, "r", encoding="utf-8") as f:
                    all_rules.extend(f.readlines())
            except FileNotFoundError:
                print(f"Filter list not found: {filter_file}")

        # Build filter set
        filter_set = adblock.FilterSet()
        filter_set.add_filters(all_rules)

        self.adblock_engine = adblock.Engine(filter_set)

    def interceptRequest(self, info):
        """Intercept and block requests matching adblock rules"""
        url = info.requestUrl().toString()
        source_url = info.firstPartyUrl().toString()

        # Map Qt resource types to adblock resource types
        resource_type_map = {
            ResourceType.ResourceTypeUnknown: "other",
            ResourceType.ResourceTypeMainFrame: "main_frame",
            ResourceType.ResourceTypeSubFrame: "sub_frame",
            ResourceType.ResourceTypeStylesheet: "stylesheet",
            ResourceType.ResourceTypeScript: "script",
            ResourceType.ResourceTypeImage: "image",
            ResourceType.ResourceTypeFontResource: "font",
            ResourceType.ResourceTypeSubResource: "sub_resource",
            ResourceType.ResourceTypeObject: "object",
            ResourceType.ResourceTypeMedia: "media",
            ResourceType.ResourceTypeWorker: "worker",
            ResourceType.ResourceTypeSharedWorker: "shared_worker",
            ResourceType.ResourceTypePrefetch: "prefetch",
            ResourceType.ResourceTypeFavicon: "favicon",
            ResourceType.ResourceTypeXhr: "xhr",
            ResourceType.ResourceTypePing: "ping",
            ResourceType.ResourceTypeServiceWorker: "service_worker",
            ResourceType.ResourceTypeCspReport: "csp_report",
            ResourceType.ResourceTypePluginResource: "plugin_resource",
            ResourceType.ResourceTypeNavigationPreloadMainFrame: "navigation_preload_main_frame",
            ResourceType.ResourceTypeNavigationPreloadSubFrame: "navigation_preload_sub_frame",
            ResourceType.ResourceTypeWebSocket: "web_socket",
            ResourceType.ResourceTypeJson: "json",
        }

        resource_type = resource_type_map.get(info.resourceType(), "other")

        # Check if URL should be blocked
        if self.adblock_engine:
            blocked = self.adblock_engine.check_network_urls(
                url=url, source_url=source_url, request_type=resource_type
            )

            if blocked:
                info.block(True)
                self.logger.info(f"Blocked: {url}")
