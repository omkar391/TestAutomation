from playwright.sync_api import Locator, Page
from pages.base_page import BasePage
from utils.logger import log


class CartModalComponent(BasePage):
    """Component Object representing the 'Added! Your product has been added to cart.' modal dialog."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.modal_container: Locator = page.locator("#cartModal")
        self.modal_title: Locator = page.locator("#cartModal .modal-title")
        self.modal_body: Locator = page.locator("#cartModal .modal-body")
        self.continue_shopping_button: Locator = page.locator("#cartModal button.close-modal")
        self.view_cart_link: Locator = page.locator("#cartModal a[href='/view_cart'], #cartModal a:has-text('View Cart')")

    def is_displayed(self, timeout: float = 6000) -> bool:
        """Verify cart confirmation modal is currently visible."""
        return self.is_element_visible(self.modal_container, timeout=timeout)

    def get_title(self) -> str:
        """Return heading text of the modal (e.g. 'Added!')."""
        return self.get_element_text(self.modal_title, "Cart Modal Title")

    def get_body_text(self) -> str:
        """Return body message of the modal."""
        return self.get_element_text(self.modal_body, "Cart Modal Body")

    def click_continue_shopping(self) -> None:
        """Click 'Continue Shopping' button to dismiss modal."""
        log.click("Cart Modal -> Continue Shopping")
        self.click_element(self.continue_shopping_button, "Continue Shopping Button")
        self.modal_container.wait_for(state="hidden", timeout=5000)

    def click_view_cart(self) -> None:
        """Click 'View Cart' link to navigate to cart page."""
        log.click("Cart Modal -> View Cart")
        self.click_element(self.view_cart_link.first, "View Cart Link")
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=5000)
        except Exception:
            pass
