from typing import Optional
from playwright.sync_api import Locator, Page
from pages.base_page import BasePage
from pages.components.header_nav import HeaderNavComponent
from pages.components.footer import FooterComponent
from pages.components.cart_modal import CartModalComponent
from utils.logger import log


class HomePage(BasePage):
    """Page Object representing the Automation Exercise Home Page."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.header: HeaderNavComponent = HeaderNavComponent(page)
        self.footer: FooterComponent = FooterComponent(page)
        self.cart_modal: CartModalComponent = CartModalComponent(page)

        # Home specific locators
        self.slider_carousel: Locator = page.locator("#slider-carousel")
        self.features_items_heading: Locator = page.locator(".features_items h2.title")
        self.recommended_items_heading: Locator = page.locator(".recommended_items h2.title")

        # Product cards on Home Page
        self.product_items: Locator = page.locator(".features_items .single-products")
        self.view_product_links: Locator = page.locator(".features_items a[href*='/product_details/']")

    def open(self) -> "HomePage":
        """Navigate directly to the Home Page."""
        log.step("Opening Home Page")
        self.navigate("/")
        return self

    def is_loaded(self) -> bool:
        """Verify home page has completely loaded with key elements visible."""
        slider_ok = self.is_element_visible(self.slider_carousel, timeout=10000)
        items_ok = self.is_element_visible(self.features_items_heading, timeout=5000)
        log.verify(f"Home page loaded: slider={slider_ok}, features_items={items_ok}")
        return slider_ok or items_ok

    def get_features_heading_text(self) -> str:
        """Retrieve features items section heading."""
        return self.get_element_text(self.features_items_heading, "Features Items Heading")

    def add_product_to_cart_by_index(self, index: int = 0) -> None:
        """Add a specific product card to the cart from the home page features grid."""
        log.step(f"Home Page: Adding product item #{index + 1} to cart")
        target_product = self.product_items.nth(index)
        self.scroll_into_view(target_product)
        add_btn = target_product.locator(".productinfo a.add-to-cart")
        self.click_element(add_btn, f"Home Page: Add to Cart Button (Item {index})")

    def click_view_product_by_index(self, index: int = 0) -> None:
        """Click 'View Product' link on a product card on the home page."""
        log.click(f"Home Page: View Product Details Link (Item {index})")
        target_link = self.view_product_links.nth(index)
        self.scroll_into_view(target_link)
        self.click_element(target_link, f"Home Page: View Product Link {index}")
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=5000)
        except Exception:
            pass
        self.dismiss_ad_overlay()

    def is_cart_modal_displayed(self) -> bool:
        """Verify the cart confirmation modal is visible."""
        return self.cart_modal.is_displayed()

    def get_cart_modal_title(self) -> str:
        """Get the modal dialog title."""
        return self.cart_modal.get_title()

    def get_cart_modal_body(self) -> str:
        """Get the modal dialog body text."""
        return self.cart_modal.get_body_text()

    def click_continue_shopping(self) -> None:
        """Dismiss the modal by clicking 'Continue Shopping'."""
        self.cart_modal.click_continue_shopping()

    def click_view_cart_from_modal(self) -> None:
        """Navigate to cart from the modal confirmation."""
        self.cart_modal.click_view_cart()
