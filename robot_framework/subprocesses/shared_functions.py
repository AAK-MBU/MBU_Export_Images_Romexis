"""
Shared functions for the robot framework.
"""

import os
import shutil
from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection
from robot_framework import config


def delete_temp_files_and_folders(orchestrator_connection: OrchestratorConnection) -> None:
    """Delete temporary files and folders."""
    orchestrator_connection.log_trace("Deleting temporary files and folders.")
    try:
        for root, dirs, _ in os.walk(config.TEMP_ROOT_PATH, topdown=True):
            for dir_obj in dirs:
                dir_path = os.path.join(root, dir_obj)
                shutil.rmtree(dir_path)
                print("Temporary files and folder where deleted.")
            break
    # pylint: disable-next = broad-exception-caught
    except Exception as e:
        orchestrator_connection.log_trace(
            "Error deleting temporary file: " + str(e)
        )
        raise e
