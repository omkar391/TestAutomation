from pathlib import Path
from typing import Optional, Union
from playwright.sync_api import Locator, Page
from pages.base_page import BasePage
from pages.components.header_nav import HeaderNavComponent
from pages.components.footer import FooterComponent
from utils.data_generator import ContactFormData
from utils.logger import log


class ContactUsPage(BasePage):
    """Page Object representing the Contact Us form (/contact_us) and file upload flow."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.header: HeaderNavComponent = HeaderNavComponent(page)
        self.footer: FooterComponent = FooterComponent(page)

        # Contact Form Locators
        self.heading_get_in_touch: Locator = page.locator(".contact-form h2.title").filter(
            has_text="Get In Touch"
        )
        self.name_input: Locator = page.locator("input[data-qa='name']")
        self.email_input: Locator = page.locator("input[data-qa='email']")
        self.subject_input: Locator = page.locator("input[data-qa='subject']")
        self.message_input: Locator = page.locator("textarea[data-qa='message']")
        self.file_input: Locator = page.locator("input[name='upload_file']")
        self.submit_button: Locator = page.locator("input[data-qa='submit-button']")

        # Post-submission Confirmation Locators
        self.success_alert: Locator = page.locator(".status.alert.alert-success")
        self.home_success_button: Locator = page.locator(
            "#contact-page a.btn-success, #contact-page a:has-text('Home')"
        )

    def open(self) -> "ContactUsPage":
        """Navigate directly to the Contact Us page."""
        log.step("Navigating to Contact Us Page")
        self.navigate("/contact_us")
        return self

    def is_get_in_touch_visible(self) -> bool:
        """Verify visibility of the 'GET IN TOUCH' section heading."""
        self.dismiss_vignette_if_present()
        return self.is_element_visible(self.heading_get_in_touch, timeout=6000)

    def fill_contact_form(self, data: ContactFormData) -> None:
        """Fill all fields of the contact form reusing BasePage explicit fill methods."""
        log.step(f"Filling contact form with dynamic data for '{data.name}'")
        self.fill_text(self.name_input, data.name, "Contact Name Field")
        self.fill_text(self.email_input, data.email, "Contact Email Field")
        self.fill_text(self.subject_input, data.subject, "Contact Subject Field")
        self.fill_text(self.message_input, data.message, "Contact Message Area")

    def upload_file(self, file_path: Union[str, Path]) -> None:
        """Attach a document or media file to the file input element."""
        resolved_path = str(Path(file_path).resolve())
        log.info(f"[UPLOAD] Setting input file: '{resolved_path}'")
        self.file_input.wait_for(state="attached", timeout=5000)
        self.file_input.set_input_files(resolved_path)

    def submit_and_accept_dialog(self) -> None:
        """Submit the contact form and handle the native browser confirm() dialog by clicking OK."""
        log.step("Submitting Contact form and registering JavaScript dialog auto-accept handler")

        def handle_dialog(dialog):
            log.info(f"Accepted browser confirmation dialog with message: '{dialog.message}'")
            dialog.accept()

        self.page.once("dialog", handle_dialog)
        self.click_element(self.submit_button, "Contact Submit Button")
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=6000)
        except Exception:
            pass
        self.dismiss_vignette_if_present()

    def submit_and_dismiss_dialog(self) -> None:
        """Submit the contact form and click Cancel on the confirmation dialog."""
        log.step("Submitting Contact form and registering JavaScript dialog dismissal handler (Cancel)")

        def handle_dialog(dialog):
            log.info(f"Dismissed browser confirmation dialog: '{dialog.message}'")
            dialog.dismiss()

        self.page.once("dialog", handle_dialog)
        self.click_element(self.submit_button, "Contact Submit Button")

    def get_entered_name(self) -> str:
        """Retrieve current value entered in Name input field."""
        return self.name_input.input_value()

    def is_success_message_visible(self) -> bool:
        """Verify whether success confirmation message banner is visible."""
        return self.is_element_visible(self.success_alert, timeout=6000)

    def get_success_message_text(self) -> str:
        """Retrieve confirmation text from success alert banner."""
        return self.get_element_text(self.success_alert, "Contact Success Alert")

    def click_home_button(self) -> None:
        """Click the 'Home' button displayed beneath the success confirmation banner."""
        log.click("Contact Success Page -> Home Button")
        self.click_element(self.home_success_button.first, "Success Page Home Button")
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=5000)
        except Exception:
            pass
        self.dismiss_vignette_if_present()

