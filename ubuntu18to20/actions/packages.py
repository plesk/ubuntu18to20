# Copyright 2024. WebPros International GmbH. All rights reserved.
from pleskdistup.common import action, packages


class RemoveUnusedPackages(action.ActiveAction):
    """ Removes packages that are not used anymore in the target OS after the dist-upgrade.
        These are mostly versioned packages, which have corresponding alternatives in the
        target OS with a different package name, which makes these ones obsolete and useless.
        The alternatives are expected to have been installed by the dist-upgrade itself.
    """

    def __init__(self):
        self.name = "remove unused packages"
        self.unused_packages = [
            "libmagickcore-6.q16-3",
            "libmagickwand-6.q16-3",
            "libmysqlclient20",
            "libprocps6",
            "perl-modules-5.26",
        ]

    def _prepare_action(self) -> action.ActionResult:
        return action.ActionResult()

    def _post_action(self) -> action.ActionResult:
        packages.remove_packages(packages.filter_installed_packages(self.unused_packages))
        return action.ActionResult()

    def _revert_action(self) -> action.ActionResult:
        return action.ActionResult()

    def estimate_post_time(self) -> int:
        return 5
