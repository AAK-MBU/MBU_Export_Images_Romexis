"""
This module handles the processing of images.
"""

import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from mbu_dev_shared_components.romexis.helper_functions import (
    add_black_bar_and_text_to_image
)

from robot_framework import config


def build_source_path(raw_path: str) -> str:
    """Convert relative path to full UNC path."""
    return os.path.join(
        config.ROMEXIS_ROOT_PATH,
        raw_path[3:].replace("romexis_images/", "").replace("/", "\\"),
    )


def format_image_date(date_value) -> str:
    """Format YYYYMMDD integer to DD/MM/YYYY string."""
    try:
        return datetime.strptime(str(date_value), "%Y%m%d").strftime("%d/%m/%Y")
    # pylint: disable-next = broad-exception-caught
    except Exception:
        return None


def process_images_threaded(
    images_data, destination_path, ssn, person_name, db_handler
) -> None:
    """Process images concurrently using threads."""
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = []

        for img in images_data:
            gamma_data = db_handler.get_gamma_data(image_id=img["image_id"])
            source_path = build_source_path(img["file_path"])
            print(f"{source_path=}")

            if not os.path.exists(source_path):
                print(f"Skipping missing file: {source_path}")
                continue

            formatted_date = format_image_date(img.get("image_date"))
            image_type = img.get("image_type")

            futures.append(
                executor.submit(
                    add_black_bar_and_text_to_image,
                    source_path,
                    destination_path,
                    ssn,
                    person_name,
                    formatted_date,
                    image_type,
                    rotation_angle=img.get("rotation_angle", 0),
                    is_mirror=img.get("is_mirror", False),
                    gamma_value=(
                        gamma_data[0]["gamma_value"]
                        if gamma_data and gamma_data[0].get("gamma_value")
                        else 1.0
                    ),
                )
            )

        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Image processing failed: {e}")
                raise


def clear_img_files_in_folder(folder_path: str) -> None:
    """Clear all .img files in the specified folder."""
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) and file_path.endswith(".img"):
                print(f"Removing file: {file_path}")
                os.remove(file_path)
        # pylint: disable-next = broad-exception-caught
        except Exception as e:
            print(f"Error removing file {file_path}: {e}")
