from typing import List, Dict, Any
import pytest
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.products_page import ProductsPage
from pages.cart_page import CartPage
from pages.components.header_nav import HeaderNavComponent
from test_data.models import get_test_users
from utils.logger import log


@pytest.mark.cart
class TestAddToCart:
    """Comprehensive Test Suite for Add to Cart Module and Cart Verifications."""

    @pytest.mark.smoke
    @pytest.mark.regression
    def test_add_to_cart_from_home_and_details_with_login(
        self,
        login_page: LoginPage,
        home_page: HomePage,
        products_page: ProductsPage,
        cart_page: CartPage,
        header_nav: HeaderNavComponent,
    ) -> None:
        """
        Primary User Journey:
        1. Login with valid credentials.
        2. From home screen, click 'Add to cart' on 1st card -> popup appears with 2 options.
        3. Verify modal options ('Continue Shopping' and 'View Cart').
        4. Click 'Continue Shopping' to dismiss popup.
        5. Click 'View Product' on 1st card -> open details page.
        6. Add to cart again from details view -> popup appears.
        7. Click 'View Cart' to navigate to cart page.
        8. Check and assert item count (quantity = 2), unit price, total price, and calculations.
        """
        log.step("Starting test: test_add_to_cart_from_home_and_details_with_login")
        valid_user = get_test_users().valid_users[0]

        # 1. Login with valid credentials
        login_page.open()
        assert login_page.is_loaded(), "Login page was expected to be loaded."
        login_page.login(valid_user.email, valid_user.password)
        assert header_nav.is_user_logged_in(), "User should be logged in."
        assert valid_user.username in header_nav.get_logged_in_username(), (
            f"Expected user logged in as '{valid_user.username}', found '{header_nav.get_logged_in_username()}'"
        )
        # Ensure cart is clean so counts reflect exactly this test session
        cart_page.clear_cart()

        # 2. Navigate to Home Page & click Add to Cart on 1st product card
        home_page.open()
        assert home_page.is_loaded(), "Home page was expected to be loaded."
        home_page.add_product_to_cart_by_index(0)

        # 3. Verify Modal Pop-up and 2 options
        assert home_page.is_cart_modal_displayed(), "Cart confirmation modal should appear."
        assert home_page.get_cart_modal_title() == "Added!", "Modal title should be 'Added!'"
        assert "Your product has been added to cart." in home_page.get_cart_modal_body(), (
            "Modal message should confirm product addition."
        )

        # 4. Click 'Continue Shopping' and verify modal closes
        home_page.click_continue_shopping()
        assert not home_page.is_cart_modal_displayed(), "Modal should be dismissed after clicking Continue Shopping."

        # 5. Open product details via '+ View Product' on 1st card
        home_page.click_view_product_by_index(0)
        assert products_page.wait_for_url_contains("/product_details/1"), (
            "Expected URL to contain '/product_details/1'"
        )

        details = products_page.get_product_detail_info()
        assert "Blue Top" in details["name"], f"Expected product 'Blue Top', got '{details['name']}'"
        assert "500" in details["price"], f"Expected price containing '500', got '{details['price']}'"

        # 6. Add to cart again from details view
        products_page.click_add_to_cart_detail()

        # 7. Modal appears again -> Click 'View Cart'
        assert products_page.is_cart_modal_displayed(), "Cart confirmation modal should appear from details view."
        products_page.click_view_cart_from_modal()
        assert cart_page.wait_for_url_contains("/view_cart"), "Expected redirect to '/view_cart'"
        assert cart_page.is_loaded(), "Cart page should be loaded."

        # 8. Check cart table item count, price, and quantity
        cart_items = cart_page.get_cart_items()
        assert len(cart_items) == 1, f"Expected 1 unique product in cart, found {len(cart_items)}"

        item = cart_items[0]
        log.verify(f"Verified Cart Item: {item}")
        assert "Blue Top" in item["name"], f"Expected product name 'Blue Top', got '{item['name']}'"
        assert item["unit_price"] == 500, f"Expected unit price 500, got {item['unit_price']}"
        assert item["quantity"] == 2, f"Expected quantity 2 (1 from home + 1 from details), got {item['quantity']}"
        assert item["total_price"] == 1000, f"Expected total price 1000 (500 x 2), got {item['total_price']}"
        assert item["total_price"] == item["unit_price"] * item["quantity"], (
            f"Mathematical calculation mismatch: {item['total_price']} != {item['unit_price']} * {item['quantity']}"
        )

    @pytest.mark.regression
    def test_cart_modal_continue_shopping_vs_view_cart(
        self,
        home_page: HomePage,
        cart_page: CartPage,
    ) -> None:
        """Verify modal behaviors: 'Continue Shopping' dismisses popup while 'View Cart' redirects to cart."""
        log.step("Starting test: test_cart_modal_continue_shopping_vs_view_cart")

        # 1. Open home page
        home_page.open()
        assert home_page.is_loaded(), "Home page should be loaded."

        # 2. Add product -> Modal appears
        home_page.add_product_to_cart_by_index(0)
        assert home_page.is_cart_modal_displayed(), "Modal should be visible."

        # 3. Click 'Continue Shopping' -> Dismisses modal without leaving page
        home_page.click_continue_shopping()
        assert not home_page.is_cart_modal_displayed(), "Modal should be closed."
        assert "/view_cart" not in home_page.get_current_url(), "User should remain on current page."

        # 4. Add product again -> Modal appears
        home_page.add_product_to_cart_by_index(0)
        assert home_page.is_cart_modal_displayed(), "Modal should be visible."

        # 5. Click 'View Cart' -> Navigates to /view_cart
        home_page.click_view_cart_from_modal()
        assert cart_page.wait_for_url_contains("/view_cart"), "Expected navigation to '/view_cart'"
        assert cart_page.is_loaded(), "Cart page should be loaded."

    @pytest.mark.regression
    def test_add_multiple_distinct_products_to_cart(
        self,
        products_page: ProductsPage,
        cart_page: CartPage,
    ) -> None:
        """Verify adding multiple distinct products populates individual cart table rows with accurate subtotals."""
        log.step("Starting test: test_add_multiple_distinct_products_to_cart")

        # 0. Ensure fresh cart state
        cart_page.clear_cart()

        # 1. Open products catalog
        products_page.open()
        assert products_page.is_loaded(), "Products page should be loaded."

        # 2. Add 1st product -> Continue Shopping
        products_page.add_product_to_cart_by_index(0)
        assert products_page.is_cart_modal_displayed()
        products_page.click_continue_shopping()

        # 3. Add 2nd product -> View Cart
        products_page.add_product_to_cart_by_index(1)
        assert products_page.is_cart_modal_displayed()
        products_page.click_view_cart_from_modal()

        # 4. Assert cart table displays both products
        assert cart_page.wait_for_url_contains("/view_cart")
        assert cart_page.is_loaded()

        items = cart_page.get_cart_items()
        assert len(items) == 2, f"Expected 2 rows in cart table, but found {len(items)}"

        # Assert each product details
        for idx, item in enumerate(items):
            assert item["name"], f"Row {idx} should have a product name."
            assert item["unit_price"] > 0, f"Row {idx} unit price should be > 0."
            assert item["quantity"] >= 1, f"Row {idx} quantity should be at least 1."
            assert item["total_price"] == item["unit_price"] * item["quantity"], (
                f"Row {idx} total price calculation mismatch."
            )

    @pytest.mark.regression
    def test_product_detail_custom_quantity_addition(
        self,
        products_page: ProductsPage,
        cart_page: CartPage,
    ) -> None:
        """Verify adding a specific quantity (e.g. 4) from the Product Details page reflects correctly in cart."""
        log.step("Starting test: test_product_detail_custom_quantity_addition")

        # 0. Ensure fresh cart state
        cart_page.clear_cart()

        # 1. Open products page and view 1st product details
        products_page.open()
        products_page.view_product_details_by_index(0)
        assert products_page.wait_for_url_contains("/product_details/")

        # 2. Set quantity to 4
        target_qty = 4
        products_page.set_product_quantity(target_qty)

        # 3. Add to cart & navigate to cart
        products_page.click_add_to_cart_detail()
        assert products_page.is_cart_modal_displayed()
        products_page.click_view_cart_from_modal()

        # 4. Verify cart quantity and total calculation
        assert cart_page.wait_for_url_contains("/view_cart")
        items = cart_page.get_cart_items()
        assert len(items) >= 1, "Expected at least 1 item in cart."

        added_item = items[-1]
        assert added_item["quantity"] == target_qty, (
            f"Expected quantity {target_qty}, got {added_item['quantity']}"
        )
        assert added_item["total_price"] == added_item["unit_price"] * target_qty, (
            f"Expected total {added_item['unit_price'] * target_qty}, got {added_item['total_price']}"
        )

    @pytest.mark.regression
    def test_remove_product_from_cart(
        self,
        home_page: HomePage,
        cart_page: CartPage,
    ) -> None:
        """Verify deleting an item from the cart table removes the row and displays empty cart when clear."""
        log.step("Starting test: test_remove_product_from_cart")

        # 0. Ensure fresh cart state
        cart_page.clear_cart()

        # 1. Add product to cart from Home
        home_page.open()
        home_page.add_product_to_cart_by_index(0)
        assert home_page.is_cart_modal_displayed()
        home_page.click_view_cart_from_modal()

        # 2. Verify item is in cart
        assert cart_page.wait_for_url_contains("/view_cart")
        initial_count = cart_page.get_cart_rows_count()
        assert initial_count >= 1, "Expected at least 1 item in cart before deletion."

        # 3. Remove the first item
        cart_page.remove_item_by_index(0)

        # 4. Assert row count decreased or cart is empty
        new_count = cart_page.get_cart_rows_count()
        assert new_count < initial_count or cart_page.is_empty(), (
            f"Cart rows should have decreased from {initial_count}, current count: {new_count}"
        )
