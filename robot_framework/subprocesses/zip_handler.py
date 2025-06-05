"""
This module handles the creation and splitting of ZIP files.
It includes functions to create a ZIP file from images, split a ZIP file into smaller parts
if it exceeds a specified size, and process the ZIP file to check its size and split it if necessary.
"""

import os
import zipfile
from pathlib import Path
from mbu_dev_shared_components.solteqtand.helper_functions import (
    zip_folder_contents,
)
from robot_framework import config


def create_zip_from_images(
    ssn: str, person_name: str, source_folder: str
) -> tuple[str, str]:
    """Zip processed image files."""
    zip_file_path = os.path.join(config.TEMP_ROOT_PATH, ssn, "edi_portal")

    if not os.path.exists(zip_file_path):
        os.makedirs(zip_file_path, exist_ok=True)

    zip_filename = f"{person_name}.zip"
    zip_full_path = os.path.join(zip_file_path, zip_filename)

    print("Creating zip file...")
    zip_folder_contents(source_folder, zip_full_path)
    print("Zip file was created.")

    return zip_full_path, zip_filename


def split_zip(
    input_zip_path: str, output_dir: str | None = None, max_size: int | None = None
) -> Path:
    """
    Split a ZIP file into smaller parts if it exceeds the specified size.

    Args:
        input_zip_path (str): Path to the input ZIP file.
        output_dir (str | None): Directory to save the split ZIP files. If None, a new directory will be created.
        max_size (int | None): Maximum size of each split ZIP file in bytes.

    Returns:
        Path: Path to the directory containing the split ZIP files.
    """
    input_zip_path = Path(input_zip_path)
    if output_dir is None:
        output_dir = input_zip_path.parent / f"{input_zip_path.stem}_split"
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(input_zip_path, "r") as original_zip:
        file_infos = original_zip.infolist()

        buckets = []
        current_bucket = []
        current_size = 0

        for info in file_infos:
            if info.file_size > max_size:
                raise ValueError(
                    f"File '{info.filename}' is larger than the max split size of {max_size} bytes."
                )

            if current_size + info.file_size > max_size:
                buckets.append(current_bucket)
                current_bucket = []
                current_size = 0

            current_bucket.append(info)
            current_size += info.file_size

        if current_bucket:
            buckets.append(current_bucket)

        for i, bucket in enumerate(buckets):
            part_zip_path = output_dir / f"{input_zip_path.stem}_part{i+1}.zip"
            with zipfile.ZipFile(
                part_zip_path, "w", compression=zipfile.ZIP_DEFLATED
            ) as part_zip:
                for info in bucket:
                    data = original_zip.read(info.filename)
                    part_zip.writestr(info, data)

    print(f"Split into {len(buckets)} ZIP file(s) at: {output_dir}")

    return output_dir


def process_zip(input_zip_path: str, max_size: int | None = None) -> Path:
    """
    Check the size of the ZIP file and split if necessary.

    Args:
        input_zip_path (str): Path to the input ZIP file.
        max_size (int | None): Maximum size of each split ZIP file in bytes. Default is 50 MB.

    returns:
        Path | None: Path to the directory containing the split ZIP files, or None if no splitting was needed.
    """
    input_zip_path = Path(input_zip_path)
    zip_size = input_zip_path.stat().st_size

    if max_size is None:
        max_size = 50 * 1024 * 1024

    if zip_size > max_size:
        print(f"ZIP size is {zip_size / (1024 * 1024):.2f} MB — splitting...")
        output_dir = split_zip(
            input_zip_path=input_zip_path, output_dir=None, max_size=max_size
        )
        return output_dir
    else:
        print(f"ZIP size is {zip_size / (1024 * 1024):.2f} MB — no splitting needed.")
        return input_zip_path
