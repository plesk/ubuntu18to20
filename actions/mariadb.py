# Copyright 1999 - 2023. Plesk International GmbH. All rights reserved.
import subprocess

from common import action, dist, dpkg, files, log, packages, systemd


MARIADB_VERSION_ON_ALMA = "10.3.35"


def _get_mariadb_utilname() -> str:
    for utility in ("mariadb", "mysql"):
        if subprocess.run(["which", utility], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
            return utility

    return None


def _is_mariadb_installed() -> bool:
    utility = _get_mariadb_utilname()
    if utility is None:
        return False
    elif utility == "mariadb":
        return True

    return "MariaDB" in subprocess.check_output([utility, "--version"], universal_newlines=True)


def _is_mysql_installed() -> bool:
    utility = _get_mariadb_utilname()
    if utility is None or utility == "mariadb":
        return False

    return "MariaDB" not in subprocess.check_output([utility, "--version"], universal_newlines=True)


class AddMysqlConnector(action.ActiveAction):
    def __init__(self):
        self.name = "install mysql connector"

    def _is_required(self) -> bool:
        return _is_mysql_installed()

    def _prepare_action(self) -> None:
        pass

    def _post_action(self) -> None:
        subprocess.check_call(["/usr/bin/dnf", "install", "-y", "mariadb-connector-c"])

    def _revert_action(self) -> None:
        pass


def get_db_server_config_file():
    if dist._is_rhel_based(dist.get_distro()):
        return "/etc/my.cnf.d/server.cnf"

    if _is_mysql_installed():
        return "/etc/mysql/my.cnf"
    return "/etc/mysql/mariadb.conf.d/50-server.cnf"


class DisableMariadbInnodbFastShutdown(action.ActiveAction):
    def __init__(self):
        self.name = "disabling mariadb innodb fast shutdown"

    def _is_required(self) -> bool:
        return _is_mariadb_installed() or _is_mysql_installed()

    def _prepare_action(self):
        target_file = get_db_server_config_file()
        files.cnf_set_section_variable(target_file, "mysqld", "innodb_fast_shutdown", "0")
        systemd.restart_services(["mariadb", "mysql"])

    def _post_action(self):
        target_file = get_db_server_config_file()
        files.cnf_unset_section_variable(target_file, "mysqld", "innodb_fast_shutdown")
        systemd.restart_services(["mariadb", "mysql"])

    def _revert_action(self):
        target_file = get_db_server_config_file()
        files.cnf_unset_section_variable(target_file, "mysqld", "innodb_fast_shutdown")
        systemd.restart_services(["mariadb", "mysql"])

    def estimate_prepare_time(self):
        return 15

    def estimate_post_time(self):
        return 15

    def estimate_revert_time(self):
        return 15


class InstallUbuntu20DatabaseVersion(action.ActiveAction):
    def __init__(self):
        self.name = "installing mariadb/mysql from ubuntu 20 official repository"

    def _is_required(self) -> bool:
        return _is_mariadb_installed() or _is_mysql_installed()

    def _prepare_action(self):
        dpkg.depconfig_parameter_set("libraries/restart-without-asking", "true")

        if _is_mariadb_installed():
            packages.install_packages(["mariadb-server-10.3"], force_package_config=True)
        elif _is_mysql_installed():
            packages.install_packages(["mysql-server-5.7"], force_package_config=True)

    def _post_action(self):
        dpkg.depconfig_parameter_set("libraries/restart-without-asking", "false")

    def _revert_action(self):
        dpkg.depconfig_parameter_set("libraries/restart-without-asking", "false")

    def estimate_prepare_time(self):
        return 60
