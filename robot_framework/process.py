"""This module contains the main process of the robot."""

import json

from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection
from OpenOrchestrator.database.queues import QueueElement

from robot_framework.subprocesses.export_and_send_images import export_and_send_images
from robot_framework.subprocesses.shared_functions import delete_temp_files_and_folders


def process(
    orchestrator_connection: OrchestratorConnection,
    queue_element: QueueElement | None = None,
) -> None:
    """Do the primary process of the robot."""
    orchestrator_connection.log_trace("Running process.")

    queue_element_data = json.loads(queue_element.data)

    orchestrator_connection.log_trace("Starting export and sending images.")
    orchestrator_connection.log_trace(
        "Reference: " + queue_element_data["requestNumberServiceNow"]
    )

    try:
        export_and_send_images(
            ssn=queue_element_data["patient_cpr"].replace("-", ""),
            connection_string=orchestrator_connection.get_constant(
                "romexis_db_connstr"
            ).value,
            orchestrator_connection=orchestrator_connection,
            queue_element_data=queue_element_data,
        )
        orchestrator_connection.log_trace("Export and sending images done.")
    except Exception as e:
        print(f"Error during process: {e}")
        raise
    finally:
        delete_temp_files_and_folders(orchestrator_connection=orchestrator_connection)
