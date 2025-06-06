"""
Database handler for retrieving person and image data.
"""
from robot_framework.exceptions import BusinessError


def get_person_info(db_handler, ssn: str) -> tuple:
    """Retrieve and validate person data from the database."""
    person_data = db_handler.get_person_data(external_id=ssn)

    if not person_data:
        raise BusinessError("Ingen person fundet med external_id")

    person = person_data[0]

    if not person.get("person_id"):
        raise BusinessError("Person ID not found in the database record")

    person_id = person["person_id"]

    if not person.get("first_name") and not person.get("last_name"):
        raise BusinessError("Person name not found in the database record")

    person_name = " ".join(
        filter(
            None,
            [
                person.get("first_name"),
                person.get("second_name"),
                person.get("third_name"),
                person.get("last_name"),
            ],
        )
    )

    return person_id, person_name


def get_image_data(db_handler, person_id: str) -> list:
    """Retrieve image IDs and image data from the database."""
    image_ids = db_handler.get_image_ids(patient_id=person_id)
    if not image_ids:
        raise BusinessError(f"No images found for patient_id: {person_id}")

    images_data = db_handler.get_image_data(image_ids=image_ids)
    if not images_data:
        raise BusinessError(f"No image data found for image_ids: {image_ids}")

    return images_data
