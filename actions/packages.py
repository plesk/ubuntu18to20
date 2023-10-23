# Copyright 1999 - 2023. Plesk International GmbH. All rights reserved.
from common import action, packages, log, util

import os


class ReinstallSystemd(action.ActiveAction):
    def __init__(self):
        self.name = "installing systemd from modern repository"

    def _prepare_action(self):
        packages.install_packages(["systemd"])

    def _post_action(self):
        pass

    def _revert_action(self):
        pass

    def estimate_prepare_time(self):
        return 30


class RemoveMailComponents(action.ActiveAction):
    def __init__(self):
        self.name = "removing mail components"
        self.removed_components_list_file = "/tmp/ubuntu18to20_removed_mail_components.txt"

    def _prepare_action(self):
        mail_components_2_packages = {
            "postfix": "postfix",
            "dovecot": "plesk-dovecot",
            "qmail": "psa-qmail",
            "courier": "psa-courier-imap",
            "spamassassin": "psa-spamassassin",
            "mailman": "psa-mailman",
        }

        components_to_remove = []
        for component, package in mail_components_2_packages.items():
            if packages.is_package_installed(package):
                components_to_remove.append(component)

        with open(self.removed_components_list_file, "w") as f:
            f.write("\n".join(components_to_remove))

        util.logged_check_call(["/usr/sbin/plesk", "installer", "remove", "--components", " ".join(components_to_remove)])

    def _post_action(self):
        if not os.path.exists(self.removed_components_list_file):
            log.warn("File with removed email components list does not exist. The reinstallation is skipped.")
            return

        with open(self.removed_components_list_file, "r") as f:
            components_to_install = f.read().splitlines()
            util.logged_check_call(["/usr/sbin/plesk", "installer", "add", "--components", " ".join(components_to_install)])

        os.unlink(self.removed_components_list_file)

    def _revert_action(self):
        if not os.path.exists(self.removed_components_list_file):
            log.warn("File with removed email components list does not exist. The reinstallation is skipped.")
            return

        with open(self.removed_components_list_file, "r") as f:
            components_to_install = f.read().splitlines()
            util.logged_check_call(["/usr/sbin/plesk", "installer", "add", "--components", " ".join(components_to_install)])

        os.unlink(self.removed_components_list_file)

    def estimate_prepare_time(self):
        return 2 * 60

    def estimate_post_time(self):
        return 3 * 60

    def estimate_revert_time(self):
        return 3 * 60
