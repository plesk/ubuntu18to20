# Copyright 1999 - 2023. Plesk International GmbH. All rights reserved.
from common import action

import os
import shutil


class RestoreCurrentSpamassasinConfiguration(action.ActiveAction):
    def __init__(self):
        self.name = "restore current spamassassin configuration after conversion"
        self.spamassasin_config_path = "/etc/spamassassin/local.cf"
        self.spamassasin_backup_path = "/tmp/spamassasin_local.cf.backup"

    def _is_required(self) -> bool:
        return os.path.exists(self.spamassasin_config_path)

    def _prepare_action(self) -> None:
        shutil.copy(self.spamassasin_config_path, self.spamassasin_backup_path)

    def _post_action(self):
        shutil.copy(self.spamassasin_backup_path, self.spamassasin_config_path)

    def _revert_action(self):
        os.unlink(self.spamassasin_backup_path)
