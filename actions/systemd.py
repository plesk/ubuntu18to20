# Copyright 1999 - 2023. Plesk International GmbH. All rights reserved.
import os

from common import action, systemd


class AddUpgradeSystemdService(action.ActiveAction):

    def __init__(self, script_path, options):
        self.name = "adding ubuntu18to20 resume service"

        self.script_path = script_path
        # ToDo. It's pretty simple to forget to add argument here, so maybe we should find another way
        self.options = [
            (" --verbose", options.verbose),
            (" --no-reboot", options.no_reboot),
        ]

        self.service_name = 'plesk-ubuntu18to20.service'
        self.service_file_path = os.path.join('/etc/systemd/system', self.service_name)
        self.service_content = '''
[Unit]
Description=First boot service for upgrade process from Ubuntu 18 to Ubuntu 20.
After=network.target network-online.target

[Service]
Type=simple
# want to run it once per boot time
RemainAfterExit=yes
# Using python 3.8 since it's the default version in Ubuntu 20
# our pex should be fine with it
ExecStart=/usr/bin/python3.8 {script_path} -s finish {arguments}

[Install]
WantedBy=multi-user.target
'''

    def _prepare_action(self):
        arguments = ""
        for argument, enabled in self.options:
            if enabled:
                arguments += argument

        systemd.add_systemd_service(self.service_name,
                                    self.service_content.format(script_path=self.script_path, arguments=arguments))

    def _post_action(self):
        systemd.remove_systemd_service(self.service_name)

    def _revert_action(self):
        systemd.remove_systemd_service(self.service_name)
