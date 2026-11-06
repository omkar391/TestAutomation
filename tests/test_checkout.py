from typing import Any, Dict, List
import pytest
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.payment_page import PaymentPage
from pages.components.header_nav import HeaderNavComponent
from test_data.models import get_test_users
from utils.logger import log


@pytest.mark.checkout
class TestCheckoutAndOrderPlacement:
    """Enterprise Test Suite for End-to-End Checkout and Payment Gateway Journeys."""

    @pytest.mark.smoke
    @pytest.mark.regression
    @pytest.mark.cart
    def test_login_add_to_cart_proceed_to_checkout_and_place_order(
        self,
        login_page: LoginPage,
        home_page: HomePage,
        cart_page: CartPage,
        checkout_page: CheckoutPage,
        payment_page: PaymentPage,
        header_nav: HeaderNavComponent,
    ) -> None:
        """
        User Journey:
        1. Login to the application with valid credentials.
        2. Add a product to the cart from the home screen.
        3. Navigate to the cart and click 'Proceed To Checkout'.
        4. Assert order details (delivery & billing address, product line items, total amount).
        5. Enter order comment and click 'Place Order'.
        6. Assert the Payment Gateway opens with all payment input fields.
        """
        log.step("Starting test: test_login_add_to_cart_proceed_to_checkout_and_place_order")
        valid_user = get_test_users().valid_users[0]

        # 1. Login first with valid credentials
        login_page.open()
        assert login_page.is_loaded(), "Login page was expected to be loaded."
        login_page.login(valid_user.email, valid_user.password)
        assert header_nav.is_user_logged_in(), "User should be logged in."
        assert valid_user.username in header_nav.get_logged_in_username(), (
            f"Expected user logged in as '{valid_user.username}', found '{header_nav.get_logged_in_username()}'"
        )

        # 2. Add product to cart
        cart_page.clear_cart()
        home_page.open()
        assert home_page.is_loaded(), "Home page was expected to be loaded."
        home_page.add_product_to_cart_by_index(0)
        assert home_page.is_cart_modal_displayed(), "Cart confirmation modal should be displayed."
        home_page.click_view_cart_from_modal()

        # Verify on cart page
        assert cart_page.wait_for_url_contains("/view_cart"), "Expected URL to contain '/view_cart'"
        assert cart_page.is_loaded(), "Cart page should be loaded."
        cart_items = cart_page.get_cart_items()
        assert len(cart_items) >= 1, "Expected at least 1 product in cart."
        expected_product_name = cart_items[0]["name"]
        expected_unit_price = cart_items[0]["unit_price"]

        # 3. Click 'Proceed To Checkout'
        cart_page.click_proceed_to_checkout()

        # 4. Assert Order Details on /checkout page
        assert checkout_page.wait_for_url_contains("/checkout"), "Expected URL to contain '/checkout'"
        assert checkout_page.is_loaded(), "Checkout page should be loaded."

        delivery_text = checkout_page.get_delivery_address_text()
        assert delivery_text, "Delivery address section should not be empty."
        log.verify(f"Delivery address verified: {delivery_text[:80]}...")

        invoice_text = checkout_page.get_invoice_address_text()
        assert invoice_text, "Invoice address section should not be empty."
        log.verify(f"Invoice address verified: {invoice_text[:80]}...")

        # Assert reviewed order line items
        reviewed_items = checkout_page.get_review_order_items()
        assert len(reviewed_items) >= 1, "Expected at least 1 order item in review table."
        assert expected_product_name in reviewed_items[0]["name"], (
            f"Expected item '{expected_product_name}', got '{reviewed_items[0]['name']}'"
        )
        assert reviewed_items[0]["unit_price"] == expected_unit_price, (
            f"Expected price {expected_unit_price}, got {reviewed_items[0]['unit_price']}"
        )

        total_amount = checkout_page.get_total_amount()
        assert total_amount >= expected_unit_price, (
            f"Expected total amount >= {expected_unit_price}, found {total_amount}"
        )
        log.verify(f"Verified total amount: Rs. {total_amount}")

        # 5. Enter order comment and click 'Place Order'
        checkout_page.enter_order_comment("Automated test order - verifying checkout flow")
        checkout_page.click_place_order()

        # 6. Assert Payment Gateway opens
        assert payment_page.wait_for_url_contains("/payment"), "Expected URL to contain '/payment'"
        assert payment_page.is_loaded(), "Payment page should be loaded."
        assert payment_page.is_payment_form_displayed(), (
            "Payment gateway form (Name on Card, Card Number, CVC, Expiry, Pay button) should be visible."
        )
        log.verify("Payment Gateway opened successfully with all required card input fields.")

    @pytest.mark.regression
    def test_complete_checkout_payment_and_order_confirmation(
        self,
        login_page: LoginPage,
        home_page: HomePage,
        cart_page: CartPage,
        checkout_page: CheckoutPage,
        payment_page: PaymentPage,
        header_nav: HeaderNavComponent,
    ) -> None:
        """Verify full checkout cycle from login, cart, order review, payment submission to order confirmation."""
        log.step("Starting test: test_complete_checkout_payment_and_order_confirmation")
        valid_user = get_test_users().valid_users[0]

        # 1. Login
        login_page.open()
        login_page.login(valid_user.email, valid_user.password)
        assert header_nav.is_user_logged_in()

        # 2. Add product to cart & proceed to checkout
        cart_page.clear_cart()
        home_page.open()
        home_page.add_product_to_cart_by_index(0)
        home_page.click_view_cart_from_modal()
        cart_page.click_proceed_to_checkout()

        # 3. Assert Checkout page and place order
        assert checkout_page.wait_for_url_contains("/checkout")
        checkout_page.enter_order_comment("End-to-end full order payment confirmation test")
        checkout_page.click_place_order()

        # 4. Fill payment form and submit
        assert payment_page.wait_for_url_contains("/payment")
        assert payment_page.is_payment_form_displayed()
        payment_page.fill_payment_details(
            name_on_card="Test admin",
            card_number="4100000000000000",
            cvc="311",
            expiry_month="11",
            expiry_year="2027",
        )
        payment_page.click_pay_and_confirm_order()

        # 5. Verify order placed confirmation
        assert payment_page.is_order_placed_successfully(), (
            "Expected order confirmation message ('Order Placed!' / 'Congratulations! Your order has been confirmed!')"
        )
        log.verify("Order confirmed and placed successfully!")

