from typing import Optional
from playwright.sync_api import Locator, Page
from pages.base_page import BasePage
from pages.components.header_nav import HeaderNavComponent
from pages.components.footer import FooterComponent
from utils.logger import log


class PaymentPage(BasePage):
    """Page Object representing the Payment Gateway page (/payment)."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.header: HeaderNavComponent = HeaderNavComponent(page)
        self.footer: FooterComponent = FooterComponent(page)

        # Payment Form Locators
        self.payment_heading: Locator = page.locator(".step-one h2.heading, h2.heading").filter(has_text="Payment")
        self.name_on_card_input: Locator = page.locator("input[data-qa='name-on-card']")
        self.card_number_input: Locator = page.locator("input[data-qa='card-number']")
        self.cvc_input: Locator = page.locator("input[data-qa='cvc']")
        self.expiry_month_input: Locator = page.locator("input[data-qa='expiry-month']")
        self.expiry_year_input: Locator = page.locator("input[data-qa='expiry-year']")
        self.pay_button: Locator = page.locator("button[data-qa='pay-button']")

        # Order Placed / Success Locators
        self.order_placed_heading: Locator = page.locator("h2[data-qa='order-placed'], h2:has-text('Order Placed!')")
        self.success_message: Locator = page.locator("p:has-text('Congratulations! Your order has been confirmed!')")

    def is_loaded(self) -> bool:
        """Verify payment page is loaded with heading and payment form."""
        heading_ok = self.is_element_visible(self.payment_heading, timeout=6000)
        card_ok = self.is_element_visible(self.name_on_card_input, timeout=4000)
        return heading_ok or card_ok

    def is_payment_form_displayed(self) -> bool:
        """Verify all primary credit card form fields are visible and interactable."""
        return (
            self.is_element_visible(self.name_on_card_input, timeout=3000)
            and self.is_element_visible(self.card_number_input, timeout=3000)
            and self.is_element_visible(self.cvc_input, timeout=3000)
            and self.is_element_visible(self.expiry_month_input, timeout=3000)
            and self.is_element_visible(self.expiry_year_input, timeout=3000)
            and self.is_element_visible(self.pay_button, timeout=3000)
        )

    def fill_payment_details(
        self,
        name_on_card: str = "Test admin",
        card_number: str = "4111111111111111",
        cvc: str = "123",
        expiry_month: str = "12",
        expiry_year: str = "2028",
    ) -> None:
        """Fill in payment credit card details."""
        log.step("Submitting payment card details")
        self.fill_text(self.name_on_card_input, name_on_card, "Name on Card Field")
        self.fill_text(self.card_number_input, card_number, "Card Number Field", mask=True)
        self.fill_text(self.cvc_input, cvc, "CVC Field", mask=True)
        self.fill_text(self.expiry_month_input, expiry_month, "Expiry Month Field")
        self.fill_text(self.expiry_year_input, expiry_year, "Expiry Year Field")

    def click_pay_and_confirm_order(self) -> None:
        """Click 'Pay and Confirm Order' button."""
        log.click("Payment -> Pay and Confirm Order Button")
        self.click_element(self.pay_button, "Pay and Confirm Order Button")
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=5000)
        except Exception:
            pass
        self.dismiss_vignette_if_present()

    def is_order_placed_successfully(self) -> bool:
        """Verify confirmation of placed order."""
        return (
            self.is_element_visible(self.order_placed_heading, timeout=6000)
            or self.is_element_visible(self.success_message, timeout=4000)
        )

