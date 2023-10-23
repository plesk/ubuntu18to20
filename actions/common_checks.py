# Copyright 1999 - 2023. Plesk International GmbH. All rights reserved.
import os
import subprocess

from common import action, dist, log, plesk, packages, version


class PleskInstallerNotInProgress(action.CheckAction):
    def __init__(self):
        self.name = "checking if Plesk installer is in progress"
        self.description = """The conversion process cannot continue because Plesk Installer is working.
\tPlease wait until it finishes or call 'plesk installer stop' to abort it.
"""

    def _do_check(self) -> bool:
        installer_status = subprocess.check_output(["/usr/sbin/plesk", "installer", "--query-status", "--enable-xml-output"],
                                                   universal_newlines=True)
        if "query_ok" in installer_status:
            return True
        return False


class DistroIsUbuntu18(action.CheckAction):
    def __init__(self):
        self.name = "checking if distro is Ubuntu18"
        self.description = "You are running a distributive other than Ubuntu 18. The tool supports only Ubuntu 18"

    def _do_check(self) -> bool:
        return dist.get_distro() == dist.Distro.ubuntu18


class PleskVersionIsActual(action.CheckAction):
    def __init__(self):
        self.name = "checking if Plesk version is actual"
        self.description = "Only Plesk Obsidian 18.0.43 or later is supported. Update Plesk to version 18.0.43 or later and try again."

    def _do_check(self) -> bool:
        try:
            major, _, iter, _ = plesk.get_plesk_version()
            return int(major) >= 18 and int(iter) >= 43
        except Exception as ex:
            log.warn("Checking plesk version is failed with error: {}".format(ex))

        return False


class CheckOutdatedPHP(action.CheckAction):
    def __init__(self, first_allowed: str):
        self.name = "checking outdated PHP"
        self.first_allowed = version.PHPVersion(first_allowed)
        self.description = "Outdated PHP versions were detected: '{}'. To proceed with the conversion:"
        self.fix_domains_step = """Switch the following domains to {} or later:
\t- {}

\tYou can do so by running the following command:
\t> plesk bin domain -u [domain] -php_handler_id plesk-php80-fastcgi
"""
        self.remove_php_step = """Remove outdated PHP packages via Plesk Installer. You can do it by calling the following command:
\tplesk installer remove --components {}
"""

    def _do_check(self) -> bool:
        known_php_versions = [
            version.PHPVersion("PHP 5.2"),
            version.PHPVersion("PHP 5.3"),
            version.PHPVersion("PHP 5.4"),
            version.PHPVersion("PHP 5.5"),
            version.PHPVersion("PHP 5.6"),
            version.PHPVersion("PHP 7.0"),
            version.PHPVersion("PHP 7.1"),
        ]
        outdated_php_versions = [php for php in known_php_versions if php < self.first_allowed]
        outdated_php_packages = {f"plesk-php{php.major}{php.minor}": str(php) for php in outdated_php_versions}

        installed_pkgs = packages.filter_installed_packages(outdated_php_packages.keys())
        if len(installed_pkgs) == 0:
            return True

        php_hanlers = {"'{}-fastcgi'", "'{}-fpm'", "'{}-fpm-dedicated'"}
        outdated_php_handlers = []
        for installed in installed_pkgs:
            outdated_php_handlers += [handler.format(installed) for handler in php_hanlers]

        try:
            looking_for_domains_sql_request = """
                SELECT d.name FROM domains d JOIN hosting h ON d.id = h.dom_id WHERE h.php_handler_id in ({});
            """.format(", ".join(outdated_php_handlers))
            outdated_php_domains = subprocess.check_output(["/usr/sbin/plesk", "db", looking_for_domains_sql_request],
                                                           universal_newlines=True)
            outdated_php_domains = [domain[2:-2] for domain in outdated_php_domains.splitlines()
                                    if domain.startswith("|") and not domain.startswith("| name ")]
            outdated_php_domains = "\n\t- ".join(outdated_php_domains)
        except Exception:
            outdated_php_domains = "Unable to get domains list. Please check it manually."

        self.description = self.description.format(", ".join([outdated_php_packages[installed] for installed in installed_pkgs]))
        if outdated_php_domains:
            self.description += "\n\t1. " + self.fix_domains_step.format(self.first_allowed, outdated_php_domains) + "\n\t2. "
        else:
            self.description += "\n\t"

        self.description += self.remove_php_step.format(" ".join(outdated_php_packages[installed].replace(" ", "") for installed in installed_pkgs).lower())

        return False


class CheckIsInContainer(action.CheckAction):
    def __init__(self):
        self.name = "checking if the system not in a container"
        self.description = "The system is running in a container-like environment ({}). The conversion is not supported for such systems."

    def _is_docker(self) -> bool:
        return os.path.exists("/.dockerenv")

    def _is_podman(self) -> bool:
        return os.path.exists("/run/.containerenv")

    def _is_vz_like(self) -> bool:
        return os.path.exists("/proc/vz")

    def _do_check(self) -> bool:
        if self._is_docker():
            self.description = self.description.format("Docker container")
            return False
        elif self._is_podman():
            self.description = self.description.format("Podman container")
            return False
        elif self._is_vz_like():
            self.description = self.description.format("Virtuozzo container")
            return False

        return True


class PleskWatchdogIsntInstalled(action.CheckAction):
    def __init__(self):
        self.name = "checking if Plesk watchdog extension is not installed"
        self.description = """The Plesk Watchdog extension is installed. Unfortunately the extension is unsupported on Ubuntu 20 and later.
\tPlease remove the extension be calling: plesk installer remove --components watchdog
"""

    def _do_check(self) -> bool:
        return not packages.is_package_installed("psa-watchdog")


class DPKGIsLocked(action.CheckAction):
    def __init__(self):
        self.name = "checking if dpkg is locked"
        self.description = """It looks like some other process is using dpkg. Please wait until it finishes and try again."""

    def _do_check(self) -> bool:
        return subprocess.run(["/bin/fuser", "/var/lib/apt/lists/lock"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode != 0
