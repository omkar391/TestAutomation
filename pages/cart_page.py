import re
from typing import Any, Dict, List, Optional
from playwright.sync_api import Locator, Page
from pages.base_page import BasePage
from pages.components.header_nav import HeaderNavComponent
from pages.components.footer import FooterComponent
from utils.logger import log


class CartPage(BasePage):
    """Page Object for the Shopping Cart page (/view_cart)."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.header: HeaderNavComponent = HeaderNavComponent(page)
        self.footer: FooterComponent = FooterComponent(page)

        # Cart Locators
        self.cart_breadcrumb: Locator = page.locator(".breadcrumb li.active")
        self.cart_table: Locator = page.locator("#cart_info_table")
        self.cart_rows: Locator = page.locator("#cart_info_table tbody tr")
        self.empty_cart_indicator: Locator = page.locator("#empty_cart")
        self.proceed_to_checkout_btn: Locator = page.locator("a.check_out")

    def open(self) -> "CartPage":
        """Directly navigate to the Shopping Cart page."""
        log.step("Navigating to Shopping Cart Page (/view_cart)")
        self.navigate("/view_cart")
        return self

    def is_loaded(self) -> bool:
        """Verify cart page is loaded."""
        table_ok = self.is_element_visible(self.cart_table, timeout=6000)
        empty_ok = self.is_element_visible(self.empty_cart_indicator, timeout=3000)
        breadcrumb_ok = self.is_element_visible(self.cart_breadcrumb, timeout=3000)
        return table_ok or empty_ok or breadcrumb_ok

    def get_cart_rows_count(self) -> int:
        """Return the number of product rows currently in the cart table."""
        try:
            self.cart_table.wait_for(state="visible", timeout=4000)
            return self.cart_rows.count()
        except Exception:
            return 0

    def get_cart_items(self) -> List[Dict[str, Any]]:
        """
        Extract detailed information for every item currently present in the cart.
        
        Returns a list of dicts with:
        - name: str
        - unit_price_str: str (e.g. 'Rs. 500')
        - unit_price: int (e.g. 500)
        - quantity_str: str (e.g. '2')
        - quantity: int (e.g. 2)
        - total_price_str: str (e.g. 'Rs. 1000')
        - total_price: int (e.g. 1000)
        """
        self.cart_table.wait_for(state="visible", timeout=6000)
        count = self.cart_rows.count()
        items: List[Dict[str, Any]] = []

        for i in range(count):
            row = self.cart_rows.nth(i)
            name_elem = row.locator(".cart_description h4 a")
            price_elem = row.locator(".cart_price p")
            qty_elem = row.locator(".cart_quantity button")
            total_elem = row.locator(".cart_total p")

            name = name_elem.inner_text().strip() if name_elem.count() > 0 else ""
            price_str = price_elem.inner_text().strip() if price_elem.count() > 0 else ""
            qty_str = qty_elem.inner_text().strip() if qty_elem.count() > 0 else ""
            total_str = total_elem.inner_text().strip() if total_elem.count() > 0 else ""

            # Extract numeric digits for exact mathematical assertions
            price_numeric = int(re.search(r"\d+", price_str).group()) if re.search(r"\d+", price_str) else 0
            qty_numeric = int(re.search(r"\d+", qty_str).group()) if re.search(r"\d+", qty_str) else 0
            total_numeric = int(re.search(r"\d+", total_str).group()) if re.search(r"\d+", total_str) else 0

            item_data = {
                "name": name,
                "unit_price_str": price_str,
                "unit_price": price_numeric,
                "quantity_str": qty_str,
                "quantity": qty_numeric,
                "total_price_str": total_str,
                "total_price": total_numeric,
            }
            log.info(f"Cart Row #{i + 1}: {item_data}")
            items.append(item_data)

        return items

    def remove_item_by_index(self, index: int = 0) -> None:
        """Click the delete button ('X') on a specific cart row."""
        log.step(f"Removing cart item at index {index}")
        initial_count = self.get_cart_rows_count()
        row = self.cart_rows.nth(index)
        delete_btn = row.locator(".cart_quantity_delete")
        self.click_element(delete_btn, f"Delete button for cart row {index}")
        
        # Wait for either row count to decrease or empty cart to display
        try:
            self.page.wait_for_function(
                f"() => document.querySelectorAll('#cart_info_table tbody tr').length < {initial_count} || document.querySelector('#empty_cart') !== null",
                timeout=5000,
            )
        except Exception:
            self.page.wait_for_timeout(1000)

    def clear_cart(self) -> None:
        """Ensure the shopping cart is completely empty before or after tests."""
        log.step("Checking and clearing any existing cart items")
        self.open()
        try:
            while self.get_cart_rows_count() > 0:
                self.remove_item_by_index(0)
                self.page.wait_for_timeout(500)
        except Exception as e:
            log.debug(f"Cart clearing finished with: {e}")

    def is_empty(self) -> bool:
        """Check if the cart is empty."""
        empty_visible = self.is_element_visible(self.empty_cart_indicator, timeout=3000)
        return empty_visible or self.get_cart_rows_count() == 0

    def click_proceed_to_checkout(self) -> None:
        """Click 'Proceed To Checkout' button."""
        log.click("Cart -> Proceed To Checkout")
        self.click_element(self.proceed_to_checkout_btn, "Proceed To Checkout Button")
