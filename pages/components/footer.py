from playwright.sync_api import Locator, Page
from utils.logger import log


class FooterComponent:
    """Component Object representing the shared footer and subscription widget."""

    def __init__(self, page: Page) -> None:
        self.page: Page = page
        self.footer_container: Locator = page.locator("footer#footer, footer")
        self.subscription_heading: Locator = page.locator("footer h2").filter(has_text="Subscription")
        self.subscription_email_input: Locator = page.locator("#susbscribe_email")
        self.subscribe_button: Locator = page.locator("#subscribe")
        self.success_alert: Locator = page.locator(".alert-success, #success-subscribe")

    def scroll_to_footer(self) -> None:
        """Scroll down to footer section."""
        log.info("Scrolling down to page footer")
        self.footer_container.scroll_into_view_if_needed()

    def subscribe(self, email: str) -> None:
        """Submit an email address to the newsletter subscription widget."""
        self.scroll_to_footer()
        log.input("Footer Subscription Email", email)
        self.subscription_email_input.fill(email)
        log.click("Footer Subscribe Button")
        self.subscribe_button.click()

    def is_subscription_success_visible(self) -> bool:
        """Verify whether subscription confirmation message is displayed."""
        try:
            self.success_alert.wait_for(state="visible", timeout=5000)
            return True
        except Exception:
            return False
