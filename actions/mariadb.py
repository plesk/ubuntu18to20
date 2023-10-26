# Copyright 1999 - 2023. Plesk International GmbH. All rights reserved.
import subprocess

from common import action, dpkg, files, mariadb, packages, systemd


MARIADB_VERSION_ON_UBUNTU_20 = mariadb.MariaDBVersion("10.3.38")


class AddMysqlConnector(action.ActiveAction):
    def __init__(self):
        self.name = "install mysql connector"

    def _is_required(self) -> bool:
        return mariadb.is_mysql_installed()

    def _prepare_action(self) -> None:
        pass

    def _post_action(self) -> None:
        subprocess.check_call(["/usr/bin/dnf", "install", "-y", "mariadb-connector-c"])

    def _revert_action(self) -> None:
        pass


def get_db_server_config_file():
    return mariadb.get_mysql_config_file_path() if mariadb.is_mysql_installed() else mariadb.get_mariadb_config_file_path()


class DisableMariadbInnodbFastShutdown(action.ActiveAction):
    def __init__(self):
        self.name = "disabling mariadb innodb fast shutdown"

    def _is_required(self) -> bool:
        return mariadb.is_mariadb_installed() or mariadb.is_mysql_installed()

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


class InstallUbuntu20Mariadb(action.ActiveAction):
    def __init__(self):
        self.name = "installing mariadb from ubuntu 20 official repository"

    def _is_required(self) -> bool:
        return mariadb.is_mariadb_installed() and MARIADB_VERSION_ON_UBUNTU_20 > mariadb.get_installed_mariadb_version()

    def _prepare_action(self):
        dpkg.depconfig_parameter_set("libraries/restart-without-asking", "true")
        packages.install_packages(["mariadb-server-10.3"], force_package_config=True)

    def _post_action(self):
        dpkg.depconfig_parameter_set("libraries/restart-without-asking", "false")

    def _revert_action(self):
        dpkg.depconfig_parameter_set("libraries/restart-without-asking", "false")

    def estimate_prepare_time(self):
        return 60


class InstallUbuntu20Mysql(action.ActiveAction):
    def __init__(self):
        self.name = "installing mysql from ubuntu 20 official repository"

    def _is_required(self) -> bool:
        return mariadb.is_mysql_installed()

    def _prepare_action(self):
        dpkg.depconfig_parameter_set("libraries/restart-without-asking", "true")
        packages.install_packages(["mysql-server-5.7"], force_package_config=True)

    def _post_action(self):
        dpkg.depconfig_parameter_set("libraries/restart-without-asking", "false")

    def _revert_action(self):
        dpkg.depconfig_parameter_set("libraries/restart-without-asking", "false")

    def estimate_prepare_time(self):
        return 60
