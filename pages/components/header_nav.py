from typing import Optional
from playwright.sync_api import Locator, Page
from utils.logger import log


class HeaderNavComponent:
    """Component Object representing the shared top navigation bar."""

    def __init__(self, page: Page) -> None:
        self.page: Page = page
        self.nav_container: Locator = page.locator(".shop-menu, .header-middle")

        # Top Navigation Items
        self.home_link: Locator = page.locator("a[href='/']").filter(has_text="Home")
        self.products_link: Locator = page.locator("a[href='/products']")
        self.cart_link: Locator = page.locator("a[href='/view_cart']")
        self.signup_login_link: Locator = page.locator("a[href='/login']")
        self.logout_link: Locator = page.locator("a[href='/logout']")
        self.delete_account_link: Locator = page.locator("a[href='/delete_account']")
        self.logged_in_as_text: Locator = page.locator("li:has-text('Logged in as')")
        self.contact_us_link: Locator = page.locator("a[href='/contact_us']")

    def click_home(self) -> None:
        """Click 'Home' navigation link."""
        log.click("Header -> Home Link")
        self.home_link.first.click()

    def click_products(self) -> None:
        """Click 'Products' navigation link."""
        log.click("Header -> Products Link")
        self.products_link.first.click()

    def click_cart(self) -> None:
        """Click 'Cart' navigation link."""
        log.click("Header -> Cart Link")
        self.cart_link.first.click()

    def click_contact_us(self) -> None:
        """Click 'Contact us' link in header navigation."""
        log.click("Header -> Contact Us Link")
        self.contact_us_link.first.click()
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=5000)
        except Exception:
            pass
        if "#google_vignette" in self.page.url:
            clean_url = self.page.url.split("#")[0]
            if "/contact_us" not in clean_url:
                clean_url = f"{clean_url.rstrip('/')}/contact_us"
            self.page.goto(clean_url, wait_until="domcontentloaded")

    def click_signup_login(self) -> None:
        """Click 'Signup / Login' navigation link."""
        log.click("Header -> Signup / Login Link")
        self.signup_login_link.first.click()
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=5000)
        except Exception:
            pass
        if "#google_vignette" in self.page.url:
            clean_url = self.page.url.split("#")[0]
            if "/login" not in clean_url:
                clean_url = f"{clean_url.rstrip('/')}/login"
            self.page.goto(clean_url, wait_until="domcontentloaded")

    def click_logout(self) -> None:
        """Click 'Logout' link to terminate current session."""
        log.click("Header -> Logout Link")
        self.logout_link.first.click()

    def click_delete_account(self) -> None:
        """Click 'Delete Account' link."""
        log.click("Header -> Delete Account Link")
        self.delete_account_link.first.click()

    def get_logged_in_username(self) -> Optional[str]:
        """Extract the logged-in username from 'Logged in as <username>' badge."""
        try:
            if self.logged_in_as_text.is_visible(timeout=5000):
                full_text = self.logged_in_as_text.inner_text().strip()
                # Text is typically "Logged in as <name>" or has a <b> tag with username
                b_element = self.logged_in_as_text.locator("b")
                if b_element.count() > 0:
                    username = b_element.first.inner_text().strip()
                    log.info(f"Verified active user: '{username}'")
                    return username
                # Fallback text parsing
                if "Logged in as" in full_text:
                    username = full_text.split("Logged in as")[-1].strip()
                    log.info(f"Verified active user: '{username}'")
                    return username
        except Exception as e:
            log.debug(f"Logged in user check exception: {e}")
        return None

    def is_user_logged_in(self, expected_username: Optional[str] = None) -> bool:
        """Verify whether an authenticated user session is currently active."""
        username = self.get_logged_in_username()
        if not username:
            return False
        if expected_username:
            matches = username.lower() == expected_username.lower()
            log.verify(f"Logged in username '{username}' matches expected '{expected_username}': {matches}")
            return matches
        return True

    def is_logout_visible(self) -> bool:
        """Check if 'Logout' link is visible."""
        return self.logout_link.is_visible()

    def is_delete_account_visible(self) -> bool:
        """Check if 'Delete Account' link is visible."""
        return self.delete_account_link.is_visible()

    def assert_authenticated_header_items(self, expected_username: Optional[str] = None) -> None:
        """Assert all header elements displayed upon successful login (including green-boxed Logout & Delete Account)."""
        log.verify("Asserting authenticated header items: Logout, Delete Account, Logged in as")
        assert self.logout_link.is_visible(), "Expected 'Logout' link to be visible in header after login."
        assert self.delete_account_link.is_visible(), "Expected 'Delete Account' link to be visible in header after login."
        assert self.is_user_logged_in(expected_username=expected_username), (
            f"Expected user to be logged in as '{expected_username}', but got '{self.get_logged_in_username()}'"
        )

    def is_signup_login_visible(self) -> bool:
        """Check if 'Signup / Login' link is visible (unauthenticated state)."""
        return self.signup_login_link.is_visible()

