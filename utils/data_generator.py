import time
import uuid
from dataclasses import dataclass


@dataclass
class ContactFormData:
    """Container for dynamically generated contact us form data."""

    name: str
    email: str
    subject: str
    message: str


def generate_contact_form_data(file_label: str = "UploadTest") -> ContactFormData:
    """Generate fresh, collision-free contact form values on every iteration."""
    timestamp = int(time.time() * 1000)
    short_uuid = uuid.uuid4().hex[:6]
    sanitized_label = file_label.replace(".", "_")

    return ContactFormData(
        name=f"QA_{sanitized_label}_{short_uuid}",
        email=f"qa_{short_uuid}_{timestamp}@testmail.com",
        subject=f"Inquiry: {file_label} [{short_uuid.upper()}]",
        message=(
            f"Automated test message submitted for target file: '{file_label}'. "
            f"Generated at epoch {timestamp} with unique token: {short_uuid}."
        ),
    )

