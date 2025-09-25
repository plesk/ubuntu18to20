# The tool to dist-upgrade servers with Plesk from Ubuntu 18 to 20

## Introduction
This utility is the official tool to dist-upgrade servers with Plesk from Ubuntu 18 to 20.

The utility uses [Plesk dist-upgrader](https://github.com/plesk/dist-upgrader).

## Preparation
To avoid downtime and data loss, make sure you have read and understood the following information before using the utility:
1. **Upgrade Plesk to the last version.**
2. **Create a full server backup.** Before the upgrade, make a full server backup (which includes a full backup of all the databases).
3. Notify the customers about upcoming downtime. Expected downtime is 20-30 minutes.
4. **Remote management module must be installed on the server**.
5. We strongly recommend that you **create a snapshot you can use as a recovery point** in case the conversion process fails.
6. Read the [Known issues](#known-issues) section below for the list of known issues.

## Timing
The conversion process should run between 20 and 30 minutes. **Plesk services, hosted websites, and e-mails will be unavailable during the entirety of the conversion process**.

## Known issues
### Blockers
Do not use the utility if any of the following is true:
- **Your system is in a container (like Virtuozzo containers, Docker Containers, etc).**

## Requirements
- Last Plesk version.
- At least 5 GB of free disk space.
- At least 2 GB of RAM.

## Conversion phases
The conversion process consists of two phases:
1. The "convert" phase contains preparation and upgrading actions.
2. The "finish" phase is the last phase containing all finishing actions.

During each phase a conversion plan consisting of stages, which in turn consist of actions, is executed. You can see the general stages in the `--help` output and the detailed plan in the `--show-plan` output.

## Using the utility
To retrieve the latest available version of the tool, please navigate to the "Releases" section. Once there, locate the most recent version of the tool and download the attached archive.

To prepare the latest version of the tool for use, please run the following commands:
```shell
> wget https://github.com/plesk/ubuntu18to20/releases/download/v2.2.2/ubuntu18to20-2.2.2.zip
> unzip ubuntu18to20-2.2.2.zip
> chmod 755 ubuntu18to20
```

To monitor the conversion process, we recommend using the ['screen' utility](https://www.gnu.org/software/screen/) to run the utility in the background. To do so, run the following command:
```shell
> screen -S ubuntu18to20
> ./ubuntu18to20
```
If you lose your SSH connection to the server, you can reconnect to the screen session by running the following command:
```shell
> screen -r ubuntu18to20
```

You can also call ubuntu18to20 in the background:
```shell
> ./ubuntu18to20 &
```

And monitor its status with the '--status' or '--monitor' flags:
```shell
> ./ubuntu18to20 --status
> ./ubuntu18to20 --monitor
... live monitor session ...
```

The conversion process requires 3 reboots. It will be resumed automatically after reboot by the `plesk-dist-upgrader` systemd service. In addition to `--status` and `--monitor`, you can check the status of the conversion process by running the following command:
```shell
> systemctl status plesk-dist-upgrader
```

Running dist-upgrader without any arguments initiates the conversion process. The utility performs preliminary checks, and if any issues are detected, it provides descriptions of the problems along with guidance on how to resolve them.
Following the preliminary checks, the tool proceeds with the dist-upgrade process, which is divided into multiple stages. Some stages end with a reboot. You can check the list of stages and steps by `./ubuntu18to20 --show-plan`.
When dist-upgrade is finished, you will see the following login message:
```
===============================================================================
Message from the Plesk dist-upgrader tool:
The server has been upgraded to Ubuntu 20.
You can remove this message from the /etc/motd file.
===============================================================================
```

## Logs
If something goes wrong, read the logs to identify the problem.
The dist-upgrader writes its log to the `/var/log/plesk/ubuntu18to20.log` file, as well as to stdout.
After the first reboot, the process is resumed by the `plesk-dist-upgrader` service, so its output is available in system logs (see `systemctl status plesk-dist-upgrader` and `journalctl -u plesk-dist-upgrader`).

## Revert
If the utility fails during the the "convert" stage before actual dist-upgrade of packages, you can use the dist-upgrader utility with the `-r` or `--revert` options to restore Plesk to normal operation. The dist-upgrader will undo some of the changes it made and restart Plesk services. Once you have resolved the root cause of the failure, you can attempt the conversion again.
Note:
- You cannot use revert to undo the changes after the dist-upgrade of packages, because packages provided by the new OS version are already installed.
- `--revert` mode is not perfect, it can fail or be unable to restore the initial state of the system. So, the importance of creating full server backup or snapshot before starting dist-upgrade can't be stressed enough.

### Checking the status of the conversion process and monitoring its progress
To check the status of the conversion process, use the `--status` option. You can see the current stage of the conversion process, the elapsed time, and the estimated time until finish.
```shell
> ./ubuntu18to20 --status
```

To monitor the progress of the conversion process in real time, use the `--monitor` option.
```shell
> ./ubuntu18to20 --monitor
( stage 3 / action re-installing plesk components  ) 02:26 / 06:18
```

## Issue handling
If for some reason the process has failed, inspect the log. By default, it's put to `/var/log/plesk/ubuntu18to20.log`. If the process was interrupted before the first reboot, you can restart it with the `--resume` option. If the problem has happened after the first reboot, you can restart the process by running `systemctl restart plesk-dist-upgrader`.

If something goes wrong, you will be informed on the next login with this message:
```
===============================================================================
Message from Plesk dist-upgrader tool:
Something went wrong during dist-upgrade by ubuntu18to20.
See the /var/log/plesk/ubuntu18to20.log file for more information.
You can remove this message from the /etc/motd file.
===============================================================================
```

### Send feedback
If you got any error, please [create an issue on github](https://github.com/plesk/ubuntu18to20/issues). Describe your problem and attach the feedback archive or at least the log to the issue. The feedback archive can be created by calling the tool with the `--prepare-feedback` option:
```shell
> ./ubuntu18to20 --prepare-feedback
```
