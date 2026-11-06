from pathlib import Path
import pytest
from pages.home_page import HomePage
from pages.contact_us_page import ContactUsPage
from pages.components.header_nav import HeaderNavComponent
from utils.data_generator import generate_contact_form_data
from utils.logger import log

FILES_DIR = Path("test_data/files_for_contact_page")
TARGET_FILES = [
    "headphones.jpeg",
    "mobile_charger.dotx",
    "mouse.json",
    "Pen_Product_Information.pps",
    "Retail_Store_Tables.xls",
    "pdf_sample_file_10MB.pdf",
]


@pytest.mark.contact
class TestContactUs:
    """Enterprise Test Suite covering Contact Us Form Submission, Multi-Type File Uploads,
    Dialog Interaction, and Negative Validation."""

    @pytest.mark.smoke
    @pytest.mark.regression
    @pytest.mark.parametrize(
        "filename",
        TARGET_FILES,
        ids=[
            "file_jpeg_image",
            "file_dotx_word_template",
            "file_json_data",
            "file_pps_powerpoint",
            "file_xls_spreadsheet",
            "file_pdf_10mb_document",
        ],
    )
    def test_contact_us_form_file_upload(
        self,
        home_page: HomePage,
        header_nav: HeaderNavComponent,
        contact_us_page: ContactUsPage,
        filename: str,
    ) -> None:
        """Verify the complete 11-step Contact Us flow with file upload:
        1. Launch browser & verify Home Page
        2. Click 'Contact Us'
        3. Verify 'GET IN TOUCH' is visible
        4. Enter dynamic name, email, subject, message
        5. Upload file
        6. Click 'Submit' & accept OK dialog
        7. Verify 'Success! Your details have been submitted successfully.'
        8. Click 'Home' and verify return to Home Page
        """
        file_path = FILES_DIR / filename
        assert file_path.exists(), f"Target test file not found: {file_path}"
        log.step(f"Starting test_contact_us_form_file_upload for file '{filename}'")

        # 1. Open Home Page and verify loaded
        home_page.open()
        assert home_page.is_loaded(), "Home page was expected to be visible."

        # 2. Click 'Contact Us' button in header
        header_nav.click_contact_us()

        # 3. Verify 'GET IN TOUCH' heading is visible
        assert contact_us_page.is_get_in_touch_visible(), "'GET IN TOUCH' should be visible."

        # 4. Generate dynamic data and fill form fields
        dynamic_data = generate_contact_form_data(file_label=file_path.stem)
        contact_us_page.fill_contact_form(dynamic_data)

        # 5. Upload target file
        contact_us_page.upload_file(file_path)

        # 6. Click 'Submit' button and accept OK on confirmation dialog
        contact_us_page.submit_and_accept_dialog()

        # 7. Verify success message
        assert contact_us_page.is_success_message_visible(), (
            f"Success message should be visible after uploading '{filename}'."
        )
        assert (
            "Success! Your details have been submitted successfully."
            in contact_us_page.get_success_message_text()
        )

        # 8. Click 'Home' button and verify return to Home Page
        contact_us_page.click_home_button()
        assert home_page.is_loaded(), "Expected to land back on Home Page."

    @pytest.mark.regression
    def test_contact_us_form_submission_without_file(
        self,
        home_page: HomePage,
        header_nav: HeaderNavComponent,
        contact_us_page: ContactUsPage,
    ) -> None:
        """Verify that submitting the Contact Us form without any file attachment succeeds."""
        log.step("Starting test: test_contact_us_form_submission_without_file")

        # 1. Open Home Page & navigate to Contact Us
        home_page.open()
        assert home_page.is_loaded(), "Home page should be visible."
        header_nav.click_contact_us()
        assert contact_us_page.is_get_in_touch_visible(), "'GET IN TOUCH' should be visible."

        # 2. Generate dynamic data and fill form without uploading a file
        dynamic_data = generate_contact_form_data(file_label="TextOnly")
        contact_us_page.fill_contact_form(dynamic_data)

        # 3. Submit and accept dialog
        contact_us_page.submit_and_accept_dialog()

        # 4. Verify success confirmation
        assert contact_us_page.is_success_message_visible(), "Success message expected."
        assert (
            "Success! Your details have been submitted successfully."
            in contact_us_page.get_success_message_text()
        )

        # 5. Return to Home Page
        contact_us_page.click_home_button()
        assert home_page.is_loaded(), "Expected return to Home Page."

    @pytest.mark.regression
    def test_contact_us_dialog_cancel_retains_form_data(
        self,
        home_page: HomePage,
        header_nav: HeaderNavComponent,
        contact_us_page: ContactUsPage,
    ) -> None:
        """Verify that clicking Cancel on the confirmation alert cancels submission and preserves user input."""
        log.step("Starting test: test_contact_us_dialog_cancel_retains_form_data")

        # 1. Navigate to Contact Us
        contact_us_page.open()
        assert contact_us_page.is_get_in_touch_visible(), "'GET IN TOUCH' should be visible."

        # 2. Fill form with dynamic data
        dynamic_data = generate_contact_form_data(file_label="CancelTest")
        contact_us_page.fill_contact_form(dynamic_data)

        # 3. Click Submit and DISMISS (Cancel) the dialog
        contact_us_page.submit_and_dismiss_dialog()

        # 4. Verify user remains on Contact Us page, no success message, and data is preserved
        assert not contact_us_page.is_success_message_visible(), "Success message should NOT appear after Cancel."
        assert contact_us_page.is_get_in_touch_visible(), "'GET IN TOUCH' form should remain visible."
        assert contact_us_page.get_entered_name() == dynamic_data.name, "Entered Name should be retained in form."
