from typing import List, Optional
from playwright.sync_api import Locator, Page
from pages.base_page import BasePage
from pages.components.header_nav import HeaderNavComponent
from pages.components.footer import FooterComponent
from utils.logger import log


class ProductsPage(BasePage):
    """Page Object for Products catalog, search, product details, and add-to-cart modals."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.header: HeaderNavComponent = HeaderNavComponent(page)
        self.footer: FooterComponent = FooterComponent(page)

        # Catalog & Search Locators
        self.all_products_heading: Locator = page.locator(".features_items h2.title").filter(
            has_text="All Products"
        )
        self.search_input: Locator = page.locator("#search_product")
        self.search_button: Locator = page.locator("#submit_search")
        self.searched_products_heading: Locator = page.locator(".features_items h2.title").filter(
            has_text="Searched Products"
        )
        self.product_items: Locator = page.locator(".features_items .single-products")
        self.product_names: Locator = page.locator(".features_items .single-products .productinfo p")
        self.view_product_links: Locator = page.locator("a[href*='/product_details/']")

        # Product Detail View Locators
        self.product_detail_name: Locator = page.locator(".product-information h2")
        self.product_detail_category: Locator = page.locator(".product-information p:has-text('Category:')")
        self.product_detail_price: Locator = page.locator(".product-information span span")
        self.product_detail_availability: Locator = page.locator(".product-information p:has-text('Availability:')")
        self.product_detail_condition: Locator = page.locator(".product-information p:has-text('Condition:')")
        self.product_detail_brand: Locator = page.locator(".product-information p:has-text('Brand:')")
        self.product_quantity_input: Locator = page.locator("#quantity")
        self.add_to_cart_detail_button: Locator = page.locator("button.cart")

        # Cart Confirmation Modal Locators (#cartModal)
        self.cart_modal: Locator = page.locator("#cartModal")
        self.cart_modal_heading: Locator = page.locator("#cartModal .modal-title")
        self.cart_modal_body: Locator = page.locator("#cartModal .modal-body")
        self.continue_shopping_button: Locator = page.locator("#cartModal button.close-modal")
        self.view_cart_modal_link: Locator = page.locator("#cartModal a[href='/view_cart'], #cartModal u")

    def open(self) -> "ProductsPage":
        """Navigate directly to the Products Catalog page."""
        log.step("Navigating to Products Catalog Page")
        self.navigate("/products")
        return self

    def is_loaded(self) -> bool:
        """Verify products catalog is displayed."""
        return self.is_element_visible(self.all_products_heading, timeout=10000)

    def search(self, keyword: str) -> None:
        """Execute a search query on the catalog."""
        log.step(f"Searching for products with keyword: '{keyword}'")
        self.fill_text(self.search_input, keyword, "Product Search Field")
        self.click_element(self.search_button, "Search Submit Button")

    def is_searched_products_displayed(self) -> bool:
        """Verify 'SEARCHED PRODUCTS' section heading is visible."""
        return self.is_element_visible(self.searched_products_heading, timeout=5000)

    def get_displayed_product_names(self) -> List[str]:
        """Extract all visible product titles from the search/catalog grid."""
        self.product_names.first.wait_for(state="visible", timeout=5000)
        count = self.product_names.count()
        names: List[str] = []
        for i in range(count):
            text = self.product_names.nth(i).inner_text().strip()
            if text:
                names.append(text)
        log.info(f"Retrieved {len(names)} product items from catalog grid")
        return names

    def add_product_to_cart_by_index(self, index: int = 0) -> None:
        """Add a specific product card to the cart from the grid."""
        log.step(f"Adding product item #{index + 1} to cart")
        target_product = self.product_items.nth(index)
        self.scroll_into_view(target_product)
        add_btn = target_product.locator(".productinfo a.add-to-cart")
        self.click_element(add_btn, f"Add to Cart Button (Item {index})")

    def is_cart_modal_displayed(self) -> bool:
        """Verify the 'Added! Your product has been added to cart.' modal is visible."""
        try:
            self.cart_modal.wait_for(state="visible", timeout=6000)
            return True
        except Exception:
            return False

    def click_continue_shopping(self) -> None:
        """Dismiss the cart confirmation modal by clicking 'Continue Shopping'."""
        log.click("Cart Modal -> Continue Shopping Button")
        self.click_element(self.continue_shopping_button, "Continue Shopping Button")
        self.cart_modal.wait_for(state="hidden", timeout=5000)

    def click_view_cart_from_modal(self) -> None:
        """Navigate to cart from the modal confirmation."""
        log.click("Cart Modal -> View Cart Link")
        self.click_element(self.view_cart_modal_link, "View Cart Modal Link")

    def view_product_details_by_index(self, index: int = 0) -> None:
        """Click 'View Product' link on a product card to open details view."""
        log.click(f"View Product Details Link (Item {index})")
        target_link = self.view_product_links.nth(index)
        self.scroll_into_view(target_link)
        self.click_element(target_link, f"View Product Link {index}")

    def get_product_detail_info(self) -> dict:
        """Extract attributes from product details view."""
        return {
            "name": self.get_element_text(self.product_detail_name, "Detail Product Name"),
            "category": self.get_element_text(self.product_detail_category, "Detail Category"),
            "price": self.get_element_text(self.product_detail_price, "Detail Price"),
            "availability": self.get_element_text(self.product_detail_availability, "Detail Availability"),
            "condition": self.get_element_text(self.product_detail_condition, "Detail Condition"),
            "brand": self.get_element_text(self.product_detail_brand, "Detail Brand"),
        }

