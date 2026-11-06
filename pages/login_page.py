from typing import Optional
from playwright.sync_api import Locator, Page
from pages.base_page import BasePage
from pages.components.header_nav import HeaderNavComponent
from pages.components.footer import FooterComponent
from utils.logger import log


class LoginPage(BasePage):
    """Page Object representing the Authentication and Signup Page (/login)."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.header: HeaderNavComponent = HeaderNavComponent(page)
        self.footer: FooterComponent = FooterComponent(page)

        # Login Form Elements
        self.login_heading: Locator = page.locator(".login-form h2").filter(has_text="Login to your account")
        self.login_email_input: Locator = page.locator("input[data-qa='login-email']")
        self.login_password_input: Locator = page.locator("input[data-qa='login-password']")
        self.login_button: Locator = page.locator("button[data-qa='login-button']")
        self.login_error_message: Locator = page.locator("form[action='/login'] p")

        # Signup Form Elements
        self.signup_heading: Locator = page.locator(".signup-form h2").filter(has_text="New User Signup!")
        self.signup_name_input: Locator = page.locator("input[data-qa='signup-name']")
        self.signup_email_input: Locator = page.locator("input[data-qa='signup-email']")
        self.signup_button: Locator = page.locator("button[data-qa='signup-button']")
        self.signup_error_message: Locator = page.locator("form[action='/signup'] p")

    def open(self) -> "LoginPage":
        """Directly navigate to the /login page."""
        log.step("Navigating to Login / Signup Page")
        self.navigate("/login")
        return self

    def is_login_form_displayed(self) -> bool:
        """Verify presence of the login form and its heading."""
        self.dismiss_vignette_if_present()
        if not self.is_element_visible(self.login_heading, timeout=5000):
            if "/login" not in self.page.url:
                self.navigate("/login")
        return (
            self.is_element_visible(self.login_heading, timeout=5000)
            or self.is_element_visible(self.login_email_input, timeout=3000)
        )

    def is_signup_form_displayed(self) -> bool:
        """Verify presence of the new user signup form and its heading."""
        return self.is_element_visible(self.signup_heading, timeout=5000)

    def login(self, email: str, password: str) -> None:
        """Perform user login action."""
        log.step(f"Submitting login credentials for user '{email}'")
        self.fill_text(self.login_email_input, email, "Login Email Field")
        self.fill_text(self.login_password_input, password, "Login Password Field", mask=True)
        self.click_element(self.login_button, "Login Submit Button")

    def signup_initial(self, name: str, email: str) -> None:
        """Submit initial name and email to proceed with registration."""
        log.step(f"Submitting initial signup info: name='{name}', email='{email}'")
        self.fill_text(self.signup_name_input, name, "Signup Name Field")
        self.fill_text(self.signup_email_input, email, "Signup Email Field")
        self.click_element(self.signup_button, "Signup Submit Button")

    def get_login_error_message(self) -> str:
        """Retrieve displayed login error message."""
        return self.get_element_text(self.login_error_message, "Login Error Alert")

    def is_login_error_displayed(self) -> bool:
        """Check if login error text is visible."""
        return self.is_element_visible(self.login_error_message, timeout=4000)

    def get_signup_error_message(self) -> str:
        """Retrieve displayed signup error message."""
        return self.get_element_text(self.signup_error_message, "Signup Error Alert")

    def is_signup_error_displayed(self) -> bool:
        """Check if signup error text is visible."""
        return self.is_element_visible(self.signup_error_message, timeout=4000)

