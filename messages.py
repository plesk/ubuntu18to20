# Copyright 1999 - 2023. Plesk International GmbH. All rights reserved.

CONVERT_RESTART_MESSAGE = """
\033[92m**************************************************************************************
The distupgrade almost done. The server will now be rebooted in a several seconds.
The finishing stage will takes place after the reboot. Finishing process takes about 5 minutes.
Current server time: {time}.
To monitor the disupgrade status use one of the following commands:
    python3.8 {script_path} --status
or
    python3.8 {script_path} --monitor
**************************************************************************************\033[0m
"""

FINISH_RESTART_MESSAGE = """
\033[92m**************************************************************************************
The distupgrade process has finished. The server will now reboot now.
**************************************************************************************\033[0m
"""

REVET_FINISHED_MESSAGE = """
\033[92m**************************************************************************************
All changes have been reverted. Plesk should now return to normal operation.
**************************************************************************************\033[0m
"""

FAIL_MESSAGE_HEAD = """
\033[91m**************************************************************************************
The conversion process has failed. Here are the last 100 lines of the {} file:
**************************************************************************************\033[0m
"""

FAIL_MESSAGE_TAIL = """
\033[91m**************************************************************************************
The conversion process has failed. See the {} file for more information.
The last 100 lines of the file are shown above.
For assistance, call 'ubuntu18to20 --prepare-feedback' and follow the instructions.
**************************************************************************************\033[0m
"""

TIME_EXCEEDED_MESSAGE = """
\033[91m**************************************************************************************
The conversion process is taking too long. It may be stuck. Please verify if the process is
still running by checking if logfile /var/log/plesk/ubuntu18to20.log continues to update.
It is safe to interrupt the process with Ctrl+C and restart it from the same stage.
**************************************************************************************\033[0m
"""

FEEDBACK_IS_READY_MESSAGE = """
\033[92m**************************************************************************************
The feedback archive is ready. You can find it here: {feedback_archive_path}
For further assistance, create an issue in our GitHub repository - https://github.com/plesk/ubuntu18to20/issues.
Please attach the feedback archive to the created issue and provide as much information about the problem as you can.
**************************************************************************************\033[0m
"""

NOT_SUPPORTED_ERROR = "The distribution is not supported yet, please contact Plesk support for further assistance. Supported conversions are: Ubuntu 18 to Ubuntu 20"