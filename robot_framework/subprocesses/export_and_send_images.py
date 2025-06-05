"""Export images from the Romexis database and send them via email."""

import os
from mbu_dev_shared_components.romexis.db_handler import RomexisDbHandler
from robot_framework.subprocesses.db_handler import (
    get_person_info,
    get_image_data,
)
from robot_framework.subprocesses.image_handler import (
    process_images_threaded,
    clear_img_files_in_folder
)
from robot_framework.subprocesses.zip_handler import (
    create_zip_from_images
)
from robot_framework.subprocesses.email_handler import (
    send_email_with_attachment
)
from robot_framework import config


def export_and_send_images(
    ssn: str,
    connection_string: str,
    orchestrator_connection,
    queue_element_data
) -> None:
    """Main orchestration function."""
    try:
        db_handler = RomexisDbHandler(conn_str=connection_string)

        person_id, person_name = get_person_info(db_handler, ssn)
        images_data = get_image_data(db_handler, person_id)

        destination_path = os.path.join(config.TEMP_ROOT_PATH, ssn, "img")
        orchestrator_connection.log_trace("Exporting images.")
        process_images_threaded(
            images_data, destination_path, ssn, person_name, db_handler
        )

        orchestrator_connection.log_trace("Removing .img-files from temp folder.")
        clear_img_files_in_folder(folder_path=destination_path)

        orchestrator_connection.log_trace("Zipping images.")
        zip_full_path, zip_filename = create_zip_from_images(
            ssn=ssn, person_name=person_name, source_folder=destination_path
        )

        orchestrator_connection.log_trace("Sending the zip-file.")
        send_email_with_attachment(
            zip_path=zip_full_path,
            filename=zip_filename,
            queue_element_data=queue_element_data,
        )
        orchestrator_connection.log_trace("Email sent successfully.")
    except Exception as e:
        print(f"Error during export and send process: {e}")
        raise
