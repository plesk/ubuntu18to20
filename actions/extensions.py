# Copyright 1999 - 2023. Plesk International GmbH. All rights reserved.
from common import action, systemd


class DisableGrafana(action.ActiveAction):
    def __init__(self):
        self.name = "disabling grafana"

    def _is_required(self) -> bool:
        return systemd.is_service_exists("grafana-server.service")

    def _prepare_action(self):
        systemd.stop_services(["grafana-server.service"])
        systemd.disable_services(["grafana-server.service"])

    def _post_action(self):
        systemd.enable_services(["grafana-server.service"])
        systemd.start_services(["grafana-server.service"])

    def _revert_action(self):
        systemd.enable_services(["grafana-server.service"])
        systemd.start_services(["grafana-server.service"])

    def estimate_prepare_time(self):
        return 20

    def estimate_post_time(self):
        return 20

    def estimate_revert_time(self):
        return 20
