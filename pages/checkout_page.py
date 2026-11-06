import re
from typing import Any, Dict, List, Optional
from playwright.sync_api import Locator, Page
from pages.base_page import BasePage
from pages.components.header_nav import HeaderNavComponent
from pages.components.footer import FooterComponent
from utils.logger import log


class CheckoutPage(BasePage):
    """Page Object for the Checkout and Order Review page (/checkout)."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.header: HeaderNavComponent = HeaderNavComponent(page)
        self.footer: FooterComponent = FooterComponent(page)

        # Checkout & Address Locators
        self.checkout_heading: Locator = page.locator(".step-one h2.heading").filter(has_text="Address Details")
        self.delivery_address_container: Locator = page.locator("#address_delivery")
        self.invoice_address_container: Locator = page.locator("#address_invoice")
        self.review_order_heading: Locator = page.locator(".step-one h2.heading").filter(has_text="Review Your Order")

        # Order Review Table Locators
        self.order_table: Locator = page.locator("#cart_info")
        self.order_rows: Locator = page.locator("#cart_info tbody tr")

        # Comments & Place Order
        self.comment_textarea: Locator = page.locator("textarea[name='message'], .form-control")
        self.place_order_button: Locator = page.locator("a[href='/payment'], a.check_out")

    def is_loaded(self) -> bool:
        """Verify checkout page is fully loaded with address details and order review."""
        delivery_ok = self.is_element_visible(self.delivery_address_container, timeout=8000)
        table_ok = self.is_element_visible(self.order_table, timeout=5000)
        return delivery_ok or table_ok

    def get_delivery_address_text(self) -> str:
        """Extract delivery address text block."""
        return self.get_element_text(self.delivery_address_container, "Delivery Address Block")

    def get_invoice_address_text(self) -> str:
        """Extract invoice/billing address text block."""
        return self.get_element_text(self.invoice_address_container, "Invoice Address Block")

    def get_review_order_items(self) -> List[Dict[str, Any]]:
        """
        Extract line items from the Review Your Order table.
        Excludes the final total summary row.
        """
        self.order_table.wait_for(state="visible", timeout=6000)
        count = self.order_rows.count()
        items: List[Dict[str, Any]] = []

        for i in range(count):
            row = self.order_rows.nth(i)
            # Check if this row is the total row
            if "Total Amount" in row.inner_text():
                continue

            name_elem = row.locator(".cart_description h4 a")
            price_elem = row.locator(".cart_price p")
            qty_elem = row.locator(".cart_quantity button")
            total_elem = row.locator(".cart_total p")

            if name_elem.count() == 0:
                continue

            name = name_elem.inner_text().strip()
            price_str = price_elem.inner_text().strip() if price_elem.count() > 0 else ""
            qty_str = qty_elem.inner_text().strip() if qty_elem.count() > 0 else ""
            total_str = total_elem.inner_text().strip() if total_elem.count() > 0 else ""

            price_num = int(re.search(r"\d+", price_str).group()) if re.search(r"\d+", price_str) else 0
            qty_num = int(re.search(r"\d+", qty_str).group()) if re.search(r"\d+", qty_str) else 0
            total_num = int(re.search(r"\d+", total_str).group()) if re.search(r"\d+", total_str) else 0

            item_data = {
                "name": name,
                "unit_price_str": price_str,
                "unit_price": price_num,
                "quantity_str": qty_str,
                "quantity": qty_num,
                "total_price_str": total_str,
                "total_price": total_num,
            }
            log.info(f"Checkout Review Item #{len(items) + 1}: {item_data}")
            items.append(item_data)

        return items

    def get_total_amount(self) -> int:
        """Extract numeric total amount from order summary row."""
        try:
            total_row = self.order_rows.filter(has_text="Total Amount").first
            text = total_row.inner_text()
            matches = re.findall(r"\d+", text)
            if matches:
                return int(matches[-1])
        except Exception as e:
            log.warning(f"Failed to extract numeric total amount: {e}")
        return 0

    def enter_order_comment(self, comment: str) -> None:
        """Fill in order comment/description in the message textarea."""
        log.step(f"Entering order comment: '{comment}'")
        self.fill_text(self.comment_textarea, comment, "Order Comment Field")

    def click_place_order(self) -> None:
        """Click 'Place Order' link to proceed to the payment gateway."""
        log.click("Checkout -> Place Order Button")
        self.click_element(self.place_order_button, "Place Order Button")
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=5000)
        except Exception:
            pass
        self.dismiss_vignette_if_present()

