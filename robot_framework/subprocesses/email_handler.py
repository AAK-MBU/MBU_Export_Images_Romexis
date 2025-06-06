"""
This module handles sending emails with attachments.
"""


from io import BytesIO
from itk_dev_shared_components.smtp import smtp_util
from robot_framework import config
from robot_framework.subprocesses.zip_handler import (
    process_zip,
)


def send_email_with_attachment(
    zip_path: str, filename: str, queue_element_data
) -> None:
    """
    Send email with the zipped images as attachment.

    Args:
        zip_path (str): Path to the zip file.
        filename (str): Name of the zip file.
        queue_element_data (dict): Data related to the queue element.

    Returns:
        None

    Raises:
        Exception: If there is an error sending the email.
    """
    try:
        path_to_zip = process_zip(zip_path)

        if path_to_zip.is_dir():
            # Multiple zip files (split)
            zip_files = sorted(path_to_zip.glob("*.zip"))
            total_files = len(zip_files)
            for index, zip_file in enumerate(zip_files, start=1):
                with open(zip_file, "rb") as f:
                    attachment_file = BytesIO(f.read())
                    attachment_file.seek(0)
                attachment = smtp_util.EmailAttachment(
                    file=attachment_file,
                    file_name=zip_file.name
                )
                send_individual_email(
                    attachment=attachment,
                    recipient=queue_element_data.get('callerEmail'),
                    queue_element_data=queue_element_data,
                    subject_suffix=f"{index}/{total_files}",
                    multiple_files=True
                )
        else:
            # Single zip file
            with open(path_to_zip, "rb") as f:
                attachment_file = BytesIO(f.read())
                attachment_file.seek(0)
            attachment = smtp_util.EmailAttachment(
                file=attachment_file,
                file_name=filename
            )
            send_individual_email(
                attachment=attachment,
                recipient=queue_element_data.get('callerEmail'),
                queue_element_data=queue_element_data
            )
    except Exception as e:
        print(f"Error adding zip file(s) as attachment: {e}")
        raise


def send_individual_email(
    attachment,
    recipient,
    queue_element_data,
    subject_suffix="",
    multiple_files=False
) -> None:
    """
    Send an individual email with the given attachment.

    Args:
        attachment: The email attachment.
        recipient (str): Recipient email address.
        queue_element_data (dict): Data related to the queue element.
        subject_suffix (str): Suffix to add to the email subject.

    Returns:
        None
    """
    if not recipient:
        raise ValueError("Recipient email address is missing.")

    case_number = queue_element_data.get('requestNumberServiceNow')
    if not case_number:
        raise ValueError("Case number is missing.")

    caller_name = queue_element_data.get('callerName')
    if not caller_name:
        raise ValueError("Caller name is missing.")

    subject = (
        f"Sagsnummer: {case_number} | "
        f"Eksporteret billedmateriale fra Romexis"
    )

    if subject_suffix:
        subject = f"{subject} {subject_suffix}"

    if multiple_files:
        email_body = (
            f"<p>Kære {caller_name}</p>"
            "<p>"
            "Her er vedhæftet det bestilte billedmateriale.<br>"
            "Hvis du ikke skal bruge alle billederne, gør følgende:<br>"
            "• Gem ZIP-mappen med billederne<br>"
            "• Åbn zip-mappen i Stifinder og slet de billeder, som du ikke skal bruge<br>"
            "<br>"
            "Husk at slette denne mail når materialet er anvendt. Senest efter 30 dage.<br>"
            "<br>"
            "<span style='color: red;'>"
            "BEMÆRK:<br>"
            "Normalt sendes alt billedmateriale i en mail.<br>"
            "I denne bestilling er billedmaterialet er så omfattende, at det sendes i flere mails.<br>"
            "I mailens overskrift kan du se, hvor mange mails, der fremsendes. Fx står der 1/2 og 2/2.<br>"
            "</span>"
            "<br>"
            "Venlig hilsen<br>"
            "Robotten"
            "</p>"
        )
    else:
        email_body = (
            f"<p>Kære {caller_name}</p>"
            "<p>"
            "Her er vedhæftet det bestilte billedmateriale.<br>"
            "Hvis du ikke skal bruge alle billederne, gør følgende:<br>"
            "• Gem ZIP-mappen med billederne<br>"
            "• Åbn zip-mappen i Stifinder og slet de billeder, som du ikke skal bruge<br>"
            "<br>"
            "Husk at slette denne mail når materialet er anvendt. Senest efter 30 dage.<br>"
            "<br>"
            "Venlig hilsen"
            "<br>"
            "Robotten"
            "</p>"
        )

    try:
        smtp_util.send_email(
            receiver=recipient,
            sender="no-reply@mbu.aarhus.dk",
            subject=subject,
            body=email_body,
            html_body=True,
            smtp_server=config.SMTP_SERVER,
            smtp_port=config.SMTP_PORT,
            attachments=[attachment],
        )
        print(f"Email sent to {recipient} with attachment: {attachment.file_name}")
    except Exception as e:
        print(f"Error sending email: {e}")
        raise
