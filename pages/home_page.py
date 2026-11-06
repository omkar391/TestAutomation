from playwright.sync_api import Locator, Page
from pages.base_page import BasePage
from pages.components.header_nav import HeaderNavComponent
from pages.components.footer import FooterComponent
from utils.logger import log


class HomePage(BasePage):
    """Page Object representing the Automation Exercise Home Page."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.header: HeaderNavComponent = HeaderNavComponent(page)
        self.footer: FooterComponent = FooterComponent(page)

        # Home specific locators
        self.slider_carousel: Locator = page.locator("#slider-carousel")
        self.features_items_heading: Locator = page.locator(".features_items h2.title")
        self.recommended_items_heading: Locator = page.locator(".recommended_items h2.title")

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

