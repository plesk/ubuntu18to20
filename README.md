# The tool to distupgrade an Ubuntu 18 server with Plesk to to Ubuntu 20

Ubuntu 18 to Ubuntu 20 distupgrade tool

## Introduction
This script is the official tool for distupgrade an Ubuntu 18 server with Plesk to Ubuntu 20. The script is based on the official ubuntu distupgrade tool. The script includes additional repository and configuration support provided by Plesk.

## Preparation
To avoid downtime and data loss, make sure you have read and understood the following information before using the script:
1. **Upgrade Plesk to the last version.**
2. **Create a full server backup.** Before the upgrade, make a full server backup (which includes a full backup of all the databases).
3. Notify the customers about upcoming downtime. Expected downtime is between 25 and 35 minutes.
4. **Remote management module must be installed on the server**.
5. We strongly recommend that you **create a snapshot you can use as a recovery point** in case the conversion process fails.
6. Read the [Known issues](#known-issues) section below for the list of known issues.

## Timing
The conversion process should run between 25 and 35 minutes. **Plesk services, hosted websites, and emails will be unavailable during the entirety of the conversion process**.

## Known issues
### Blockers
Do not use the script if any of the following is true:
- **You are running an OS other than Ubuntu 18**. The script was designed to convert Ubuntu 18 servers only. Please, don't use it for other distributions.
- **PHP 7.1 and earlier are not supported** in Ubuntu 20, and will not receive any updates after the conversion. These PHP versions are deprecated and may have security vulnerabilities. So we force to remove this versions before the conversion.
- **Distupgrade inside containers (like Virtuozzo containers, Docker Containers, etc) are not supported**. 

## Requirements
- Last Plesk version.
- Ubuntu 18
- grub is installed
- At least 5 GB of free disk space.
- At least 2 GB of RAM.

## Using the script
To retrieve the latest available version of the tool, please navigate to the "Releases" section. Once there, locate the most recent version of the tool and download the zip archive. The zip archive will contain the ubuntu18to20 tool binary.

To prepare the latest version of the tool for use from a command line, please run the following commands:
```shell
> wget https://github.com/plesk/ubuntu18to20/releases/download/v1.0.0/ubuntu18to20-1.0.0.zip
> unzip ubuntu18to20-1.0.0.zip
> chmod 755 ubuntu18to20
```

To monitor the conversion process, we recommend using the ['screen' utility](https://www.gnu.org/software/screen/) to run the script in the background. To do so, run the following command:
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

After reboot to the Ubuntu 20, you can check the status of the conversion process by running the following command:
```shell
> python3.8 ./ubuntu18to20 --status
> python3.8 ./ubuntu18to20 --monitor
... live monitor session ...
```

Running ubuntu18to20 without any arguments initiates the conversion process. The script performs preliminary checks, and if any issues are detected, it provides descriptions of the problems along with guidance on how to resolve them.
Following the preliminary checks, the tool proceeds with the distupgrade process, which is divided into two stages: the distupgrade stage, lasting approximately 20 minutes, and the finishing stage. The distupgrade stage involves the actual upgrade process, after which the server reboots.
Upon reboot, the finishing stage commences, typically taking about 5 minutes to complete. This stage triggers a second reboot at its conclusion.
Upon your next SSH login, you will encounter the following message:
```
===============================================================================
Message from the Plesk ubuntu18to20 tool:
The server has been upgraded to Ubuntu 20.
You can remove this message from the /etc/motd file.
===============================================================================
```

### Conversion stage options
The conversion process consists of two stage options: "start", and "finish". To run stages individually, use the "--start", and "--finish" flags, or the "-s" flag with name of the stage you want to run.
1. The "start" stage start distupgrade process.
2. The "finish" stage must be called on the first boot of Ubuntu 20. You can rerun this stage if something goes wrong during the first boot to ensure that the problem is fixed and Plesk is ready to use.

### Other arguments

### Logs
If something goes wrong, read the logs to identify the problem. You can also read the logs to check the status of the finish stage during the first boot.
The ubuntu18to20 writes its log to the '/var/log/plesk/ubuntu18to20.log' file, as well as to stdout.

### Revert
If the script fails during the the "start" stage before the distupgrade performs, you can use the ubuntu18to20 script with the '-r' or '--revert' flags to restore Plesk to normal operation. The ubuntu18to20 will undo some of the changes it made and restart Plesk services. Once you have resolved the root cause of the failure, you can attempt the conversion again.
Note:
- You cannot use revert to undo the changes after the distupgrade take it's place, because packages provided by Ubuntu 20 already installed.

### Check the status of the conversion process and monitor its progress
To check the status of the conversion process, use the '--status' flag. You can see the current stage of the conversion process, the elapsed time, and the estimated time until finish.
```shell
> ./ubuntu18to20 --status
```

To monitor the progress of the conversion process in real time, use the '--monitor' flag.
```shell
> ./ubuntu18to20 --monitor
( stage 3 / action re-installing plesk components  ) 02:26 / 06:18
```

After the first reboot you should call the script directly by python3.8 interpreter:
```shell
> python3.8 ./ubuntu18to20 --status
> python3.8 ./ubuntu18to20 --monitor
... live monitor session ...
```

## Issue handling
### ubuntu18to20 finish fails on the first boot
If something goes wrong during the finish stage, you will be informed on the next SSH login with this message:
```
===============================================================================
Message from Plesk ubuntu18to20 tool:
Something went wrong during the final stage of Ubuntu 18 to Ubuntu 20 conversion
See the /var/log/plesk/ubuntu18to20.log file for more information.
You can remove this message from the /etc/motd file.
===============================================================================
```
You can read the ubuntu18to20 log to troubleshoot the issue. If the ubuntu18to20 finish stage fails for any reason, once you have resolved the root cause of the failure, you can retry by running 'python3.8 ubuntu18to20 -s finish'.

### Send feedback
If you got any error, please [create an issue on github](https://github.com/plesk/ubuntu18to20/issues). To do generate feedback archive by calling the tool with '-f' or '--prepare-feedback' flags.
```shell
> ./ubuntu18to20 --prepare-feedback
```
Describe your problem and attach the feedback archive to the issue.