from typing import Optional, Union
from playwright.sync_api import Locator, Page, TimeoutError as PlaywrightTimeoutError, expect
from config.settings import settings
from utils.logger import log


class BasePage:
    """Base Page Object providing enterprise wrapper methods, explicit waits,
    automatic ad-vignette mitigation, and structured action logging."""

    def __init__(self, page: Page) -> None:
        self.page: Page = page
        self.default_timeout: int = settings.DEFAULT_TIMEOUT

    def _resolve_locator(self, locator: Union[str, Locator]) -> Locator:
        """Resolve a string selector or return the Locator object directly."""
        if isinstance(locator, str):
            return self.page.locator(locator)
        return locator

    def navigate(self, path: str = "") -> None:
        """Navigate to a relative URL from BASE_URL or an absolute URL."""
        url = path if path.startswith("http") else f"{settings.BASE_URL.rstrip('/')}/{path.lstrip('/')}"
        log.navigate(url)
        self.page.goto(url, wait_until="domcontentloaded", timeout=self.default_timeout)
        self.dismiss_vignette_if_present()

    def get_current_url(self) -> str:
        """Return the current page URL."""
        return self.page.url

    def get_page_title(self) -> str:
        """Return the current page title."""
        return self.page.title()

    def click_element(
        self,
        locator: Union[str, Locator],
        name: str,
        timeout: Optional[int] = None,
        force: bool = False,
    ) -> None:
        """Click on an element with explicit visibility wait, logging, and retry for overlays."""
        loc = self._resolve_locator(locator)
        t = timeout or self.default_timeout
        log.click(name)
        try:
            loc.wait_for(state="visible", timeout=t)
            loc.click(timeout=t, force=force)
        except PlaywrightTimeoutError as e:
            # Check if a Google vignette interstitial intercepted the click
            if self.dismiss_vignette_if_present():
                log.info(f"Dismissed overlay, retrying click on '{name}'")
                loc.click(timeout=t, force=force)
            else:
                log.error(f"Failed to click '{name}' within {t}ms: {e}")
                raise

    def fill_text(
        self,
        locator: Union[str, Locator],
        text: str,
        name: str,
        mask: bool = False,
        timeout: Optional[int] = None,
    ) -> None:
        """Fill text into an input field with explicit wait, clearing, and action logging."""
        loc = self._resolve_locator(locator)
        t = timeout or self.default_timeout
        log.input(name, text, mask=mask)
        try:
            loc.wait_for(state="visible", timeout=t)
            loc.fill(text, timeout=t)
        except PlaywrightTimeoutError as e:
            if self.dismiss_vignette_if_present():
                loc.fill(text, timeout=t)
            else:
                log.error(f"Failed to fill text in '{name}' within {t}ms: {e}")
                raise

    def get_element_text(
        self,
        locator: Union[str, Locator],
        name: str,
        timeout: Optional[int] = None,
    ) -> str:
        """Retrieve and return inner text of an element."""
        loc = self._resolve_locator(locator)
        t = timeout or self.default_timeout
        try:
            loc.wait_for(state="visible", timeout=t)
            text = loc.inner_text(timeout=t).strip()
            log.debug(f"Retrieved text '{text}' from '{name}'")
            return text
        except PlaywrightTimeoutError as e:
            log.error(f"Failed to get text from '{name}' within {t}ms: {e}")
            raise

    def is_element_visible(
        self,
        locator: Union[str, Locator],
        timeout: Optional[int] = None,
    ) -> bool:
        """Check whether an element is visible within the given timeout without throwing."""
        loc = self._resolve_locator(locator)
        t = timeout if timeout is not None else 3000
        try:
            loc.wait_for(state="visible", timeout=t)
            return True
        except (PlaywrightTimeoutError, Exception):
            return False

    def wait_for_element(
        self,
        locator: Union[str, Locator],
        state: str = "visible",
        timeout: Optional[int] = None,
    ) -> Locator:
        """Explicitly wait for element state (visible, hidden, attached, detached)."""
        loc = self._resolve_locator(locator)
        t = timeout or self.default_timeout
        loc.wait_for(state=state, timeout=t)  # type: ignore[arg-type]
        return loc

    def wait_for_url_contains(self, expected_substring: str, timeout: Optional[int] = None) -> None:
        """Wait until current URL contains the expected substring."""
        t = timeout or self.default_timeout
        log.verify(f"Waiting for URL containing '{expected_substring}'")
        self.page.wait_for_url(lambda u: expected_substring in u, timeout=t)

    def scroll_into_view(self, locator: Union[str, Locator]) -> None:
        """Scroll page until element is in the viewport."""
        loc = self._resolve_locator(locator)
        loc.scroll_into_view_if_needed()

    def dismiss_vignette_if_present(self) -> bool:
        """Detect and close Google vignette full-screen ad overlays if they appear."""
        try:
            # Check URL for vignette hash
            if "#google_vignette" in self.page.url:
                log.info("Detected #google_vignette in URL, attempting dismissal...")
                # Attempt to click dismiss button if present in vignette iframe or page
                close_btn = self.page.locator("#dismiss-button, div[id*='dismiss'], button[aria-label='Close ad']")
                if close_btn.count() > 0 and close_btn.first.is_visible():
                    close_btn.first.click(force=True)
                    log.info("Successfully clicked dismiss button on ad vignette")
                    return True
                # Fallback: re-navigate without hash
                clean_url = self.page.url.split("#")[0]
                self.page.goto(clean_url, wait_until="domcontentloaded")
                return True
        except Exception as e:
            log.debug(f"Vignette dismissal check finished with: {e}")
        return False
