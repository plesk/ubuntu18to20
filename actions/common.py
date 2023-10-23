# Copyright 1999 - 2023. Plesk International GmbH. All rights reserved.
import os
import shutil
import sys

from common import action, files, motd, plesk


class MoveOldBindConfigToNamed(action.ActiveAction):
    def __init__(self):
        self.name = "move old bind configuration to named"
        self.old_bind_config_path = "/etc/default/bind9"
        self.dst_config_path = "/etc/default/named"

    def _is_required(self) -> bool:
        return os.path.exists(self.old_bind_config_path)

    def _prepare_action(self):
        pass

    def _post_action(self):
        shutil.move(self.old_bind_config_path, self.dst_config_path)

    def _revert_action(self):
        pass


class AddFinishSshLoginMessage(action.ActiveAction):
    def __init__(self):
        self.name = "add finish ssh login message"
        self.finish_message = """
The server has been upgraded to Ubuntu 20.
"""

    def _prepare_action(self) -> None:
        pass

    def _post_action(self) -> None:
        motd.add_finish_ssh_login_message(self.finish_message)
        motd.publish_finish_ssh_login_message()

    def _revert_action(self) -> None:
        pass


class AddInProgressSshLoginMessage(action.ActiveAction):
    def __init__(self):
        self.name = "add in progress ssh login message"
        path_to_script = os.path.abspath(sys.argv[0])
        self.in_progress_message = f"""
===============================================================================
Message from the Plesk ubuntu18to20 tool:
The server is being converted to Ubuntu 20. Please wait.
To see the current conversion status, run the '{path_to_script} --status' command.
To monitor the conversion progress in real time, run the '{path_to_script} --monitor' command.
===============================================================================
"""

    def _prepare_action(self) -> None:
        motd.add_inprogress_ssh_login_message(self.in_progress_message)

    def _post_action(self) -> None:
        pass

    def _revert_action(self) -> None:
        motd.restore_ssh_login_message()


class DisablePleskSshBanner(action.ActiveAction):
    def __init__(self):
        self.name = "disable plesk ssh banner"
        self.banner_command_path = "/root/.plesk_banner"

    def _prepare_action(self) -> None:
        if os.path.exists(self.banner_command_path):
            files.backup_file(self.banner_command_path)
            os.unlink(self.banner_command_path)

    def _post_action(self) -> None:
        files.restore_file_from_backup(self.banner_command_path)

    def _revert_action(self) -> None:
        files.restore_file_from_backup(self.banner_command_path)


class HandleConversionStatus(action.ActiveAction):
    def __init__(self):
        self.name = "prepare and send conversion status"

    def _prepare_action(self) -> None:
        plesk.prepare_conversion_flag()

    def _post_action(self) -> None:
        plesk.send_conversion_status(True)

    def _revert_action(self) -> None:
        plesk.remove_conversion_flag()


class CleanApparmorCacheConfig(action.ActiveAction):
    def __init__(self):
        self.name = "clean apparmor cache configuration"
        self.possible_locations = ["/etc/apparmor/cache", "/etc/apparmor.d/cache"]

    def _is_required(self) -> bool:
        return len([location for location in self.possible_locations if os.path.exists(location)]) > 0

    def _prepare_action(self):
        for location in self.possible_locations:
            if os.path.exists(location):
                shutil.move(location, location + ".backup")

    def _post_action(self):
        for location in self.possible_locations:
            location = location + ".backup"
            if os.path.exists(location):
                shutil.rmtree(location)

    def _revert_action(self):
        for location in self.possible_locations:
            if os.path.exists(location):
                shutil.move(location + ".backup", location)

    def estimate_prepare_time(self):
        return 1

    def estimate_post_time(self):
        return 1

    def estimate_revert_time(self):
        return 1
