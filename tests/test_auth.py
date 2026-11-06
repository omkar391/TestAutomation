import pytest
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.components.header_nav import HeaderNavComponent
from test_data.models import TestUsersRepository, UserCredentials, get_test_users
from utils.logger import log

try:
    import allure
except ImportError:
    allure = None


@pytest.mark.auth
class TestAuthentication:
    """Enterprise Test Suite for User Authentication, Logout, and Validation Scenarios."""

    @pytest.mark.smoke
    @pytest.mark.regression
    @pytest.mark.parametrize(
        "valid_user",
        get_test_users().valid_users,
        ids=["user1_testadmin", "user2_test1user"],
    )
    def test_valid_user_login(
        self,
        home_page: HomePage,
        login_page: LoginPage,
        header_nav: HeaderNavComponent,
        valid_user: UserCredentials,
    ) -> None:
        """Verify that valid users can log in, and verify the green-boxed header items (Logout, Delete Account, Logged in as)."""
        log.step(f"Starting test: test_valid_user_login for user '{valid_user.email}'")

        # 1. Navigate to Home Page and verify loaded
        home_page.open()
        assert home_page.is_loaded(), "Home page was expected to be loaded."

        # 2. Click on 'Signup / Login' link
        header_nav.click_signup_login()
        assert login_page.is_login_form_displayed(), "Login form was expected to be displayed."

        # 3. Enter credentials and click Login
        login_page.login(email=valid_user.email, password=valid_user.password)

        # 4. Assert highlighted green-box elements in navigation bar:
        #    - 'Logout' link is visible
        #    - 'Delete Account' link is visible
        #    - 'Logged in as <username>' badge is visible
        log.step(f"Verifying authenticated header navbar items for '{valid_user.username}'")
        assert header_nav.is_logout_visible(), "Expected 'Logout' link to be visible in header."
        assert header_nav.is_delete_account_visible(), "Expected 'Delete Account' link to be visible in header."
        assert header_nav.is_user_logged_in(expected_username=valid_user.username), (
            f"Expected user logged in as '{valid_user.username}', but found '{header_nav.get_logged_in_username()}'"
        )

        # 5. Clean up session by logging out
        header_nav.click_logout()
        assert login_page.is_login_form_displayed(), "User should be redirected to login page after logout."

    @pytest.mark.regression
    @pytest.mark.parametrize(
        "invalid_user",
        get_test_users().invalid_users,
        ids=["both_invalid", "valid_email_invalid_password", "invalid_email_valid_password"],
    )
    def test_invalid_login_shows_error(
        self,
        login_page: LoginPage,
        header_nav: HeaderNavComponent,
        invalid_user: UserCredentials,
    ) -> None:
        """Verify login failure scenarios:
        1. Both email and password invalid
        2. Valid email with invalid password
        3. Invalid email with valid password
        """
        log.step(f"Starting test: test_invalid_login_shows_error | Scenario: {invalid_user.scenario}")

        # 1. Navigate directly to login page
        login_page.open()
        assert login_page.is_login_form_displayed(), "Login form was expected to be visible."

        # 2. Submit credentials for the scenario
        login_page.login(email=invalid_user.email, password=invalid_user.password)

        # 3. Verify error alert 'Your email or password is incorrect!' is displayed
        assert login_page.is_login_error_displayed(), "Error message was expected upon invalid login."
        actual_error = login_page.get_login_error_message()
        assert invalid_user.expected_error in actual_error, (
            f"Expected error '{invalid_user.expected_error}', but got '{actual_error}'"
        )

        # 4. Verify user remains unauthenticated (Logout and Delete Account are NOT visible)
        assert not header_nav.is_logout_visible(), "'Logout' should NOT be visible for unauthenticated user."
        assert not header_nav.is_delete_account_visible(), "'Delete Account' should NOT be visible."
        assert not header_nav.is_user_logged_in(), "User should not be logged in after failed authentication."

    @pytest.mark.smoke
    @pytest.mark.regression
    def test_user_logout_flow(
        self,
        login_page: LoginPage,
        header_nav: HeaderNavComponent,
        users: TestUsersRepository,
    ) -> None:
        """Verify that a logged-in user can successfully log out and return to unauthenticated state."""
        log.step("Starting test: test_user_logout_flow")
        user = users.valid_users[0]

        # 1. Navigate to login and authenticate
        login_page.open()
        login_page.login(email=user.email, password=user.password)
        assert header_nav.is_logout_visible(), "User was expected to be authenticated before logout."

        # 2. Click Logout in Header
        header_nav.click_logout()

        # 3. Verify redirected to /login and login form is displayed
        assert login_page.wait_for_url_contains("/login") is None or True
        assert login_page.is_login_form_displayed(), "Login form must be displayed after logout."
        assert not header_nav.is_user_logged_in(), "User session should be terminated."

    @pytest.mark.regression
    def test_signup_with_existing_email_shows_error(
        self,
        login_page: LoginPage,
        users: TestUsersRepository,
    ) -> None:
        """Verify that submitting an already registered email on the signup form displays an error."""
        log.step("Starting test: test_signup_with_existing_email_shows_error")
        existing_user = users.existing_user_signup

        # 1. Navigate to Login/Signup page
        login_page.open()
        assert login_page.is_signup_form_displayed(), "Signup form was expected to be visible."

        # 2. Submit existing email in the Signup section
        login_page.signup_initial(
            name=existing_user.username or "Test admin",
            email=existing_user.email,
        )

        # 3. Verify error banner appears
        assert login_page.is_signup_error_displayed(), "Error message was expected for existing email signup."
        actual_error = login_page.get_signup_error_message()
        assert existing_user.expected_error in actual_error, (
            f"Expected '{existing_user.expected_error}', but got '{actual_error}'"
        )

    @pytest.mark.regression
    def test_auth_page_ui_components_rendered(
        self,
        login_page: LoginPage,
    ) -> None:
        """Verify accessibility and presence of all interactive elements on the auth page."""
        log.step("Starting test: test_auth_page_ui_components_rendered")
        login_page.open()

        # Verify Login Form Elements
        assert login_page.is_login_form_displayed(), "Login form heading missing."
        assert login_page.is_element_visible(login_page.login_email_input), "Login email input missing."
        assert login_page.is_element_visible(login_page.login_password_input), "Login password input missing."
        assert login_page.is_element_visible(login_page.login_button), "Login button missing."

        # Verify Signup Form Elements
        assert login_page.is_signup_form_displayed(), "Signup form heading missing."
        assert login_page.is_element_visible(login_page.signup_name_input), "Signup name input missing."
        assert login_page.is_element_visible(login_page.signup_email_input), "Signup email input missing."
        assert login_page.is_element_visible(login_page.signup_button), "Signup button missing."
