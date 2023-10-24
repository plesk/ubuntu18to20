# Copyright 1999 - 2023. Plesk International GmbH. All rights reserved.
import os
import subprocess

from common import action, dist, dpkg, files, log, packages, util


class InstallUbuntuUpdateManager(action.ActiveAction):
    def __init__(self):
        self.name = "installing ubuntu update manager"

    def _prepare_action(self):
        packages.install_packages(["update-manager-core"])

    def _post_action(self):
        pass

    def _revert_action(self):
        pass

    def estimate_prepare_time(self):
        return 10


class SetupUbuntu20Repositories(action.ActiveAction):
    def __init__(self):
        self.name = "setting up ubuntu 20 repositories"
        self.plesk_sourcelist_path = "/etc/apt/sources.list.d/plesk.list"

    def _prepare_action(self):
        files.replace_string("/etc/apt/sources.list", "bionic", "focal")

        for root, _, file in os.walk("/etc/apt/sources.list.d/"):
            for file in file:
                if file.endswith(".list"):
                    files.replace_string(os.path.join(root, file), "bionic", "focal")

        files.backup_file(self.plesk_sourcelist_path)
        files.replace_string(self.plesk_sourcelist_path, "extras", "all")

        packages.update_package_list()

    def _post_action(self):
        files.restore_file_from_backup(self.plesk_sourcelist_path)

    def _revert_action(self):
        files.restore_file_from_backup(self.plesk_sourcelist_path)
        files.replace_string("/etc/apt/sources.list", "focal", "bionic")

        for root, _, file in os.walk("/etc/apt/sources.list.d/"):
            for file in file:
                if file.endswith(".list"):
                    files.replace_string(os.path.join(root, file), "focal", "bionic")

        packages.update_package_list()

    def estimate_prepare_time(self):
        return 20

    def estimate_revert_time(self):
        return 20


class InstallNextKernelVersion(action.ActiveAction):
    def __init__(self):
        self.name = "installing kernel from next distro version"

    def _prepare_action(self):
        packages.install_packages(["linux-generic"])

    def _post_action(self):
        pass

    def _revert_action(self):
        pass

    def estimate_prepare_time(self):
        return 2 * 60 + 30


class InstallUdev(action.ActiveAction):
    def __init__(self):
        self.name = "installing udev"

    def _prepare_action(self):
        try:
            packages.install_packages(["udev"])
        except Exception:
            udevd_service_path = "/lib/systemd/system/systemd-udevd.service"
            if os.path.exists(udevd_service_path):
                files.replace_string(udevd_service_path,
                                     "ExecReload=udevadm control --reload --timeout 0",
                                     "ExecReload=/bin/udevadm control --reload --timeout 0")

            dpkg.restore_installation()

    def _post_action(self):
        pass

    def _revert_action(self):
        pass

    def estimate_prepare_time(self):
        return 2 * 60 + 30


class RemoveLXD(action.ActiveAction):
    def __init__(self):
        self.name = "remove lxd"

    def _is_required(self) -> bool:
        return packages.is_package_installed("lxd")

    def _prepare_action(self):
        packages.remove_packages(["lxd", "lxd-client"])

    def _post_action(self):
        packages.install_packages(["lxd", "lxd-client"])

    def _revert_action(self):
        packages.install_packages(["lxd", "lxd-client"])

    def estimate_prepare_time(self):
        return 30

    def estimate_post_time(self):
        return 30

    def estimate_revert_time(self):
        return 30


class UpgradeGrub(action.ActiveAction):
    def __init__(self):
        self.name = "upgrade grub from new repositories"

    def _prepare_action(self):
        try:
            packages.upgrade_packages(["grub-pc"])
        except Exception:
            log.warn("grub-pc require configuration, trying to do it automatically")
            reconfigure_process = subprocess.Popen("/usr/bin/dpkg --configure grub-pc",
                                                   stdin=subprocess.PIPE,
                                                   stdout=subprocess.PIPE,
                                                   stderr=subprocess.PIPE,
                                                   shell=True, universal_newlines=True,
                                                   env={"PATH": os.environ["PATH"], "DEBIAN_FRONTEND": "readline"})

            reconfigure_process.stdin.write("1\n")
            stdout, stderr = reconfigure_process.communicate()

            if reconfigure_process.returncode != 0:
                log.err("Unable to reconfigure grub-pc package automatically.\nstdout: {}\nstderr: {}".format(stdout, stderr))
                raise Exception("""Unable to reconfigure grub-pc package, plesk perform reconfiguration manually by calling:
1. dpkg --configure grub-pc
2. apt-get install -f""")

            dpkg.restore_installation()

    def _post_action(self):
        pass

    def _revert_action(self):
        pass

    def estimate_prepare_time(self):
        return 5 * 60


class UpgradePackagesFromNewRepositories(action.ActiveAction):
    def __init__(self):
        self.name = "upgrade packages from new repositories"

    def _prepare_action(self):
        packages.upgrade_packages()
        packages.autoremove_outdated_packages()

    def _post_action(self):
        pass

    def _revert_action(self):
        pass

    def estimate_prepare_time(self):
        return 5 * 60


class DoDistupgrade(action.ActiveAction):
    def __init__(self):
        self.name = "make dist-upgrade"

    def _prepare_action(self):
        dpkg.do_distupgrade()

    def _post_action(self):
        packages.autoremove_outdated_packages()

    def _revert_action(self):
        # I believe there is no way to revert dist-upgrade
        pass

    def estimate_prepare_time(self):
        return 5 * 60

    def estimate_post_time(self):
        return 30


class RepairPleskInstallation(action.ActiveAction):
    def __init__(self):
        self.name = "repair plesk installation"

    def _prepare_action(self):
        pass

    def _post_action(self):
        util.logged_check_call(["/usr/sbin/plesk", "repair", "installation", "-y"])

    def _revert_action(self):
        pass

    def estimate_post_time(self):
        return 3 * 60
