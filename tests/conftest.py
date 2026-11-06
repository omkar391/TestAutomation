import os
import re
import base64
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Generator
import pytest
from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

from config.settings import settings
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.products_page import ProductsPage
from pages.contact_us_page import ContactUsPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.payment_page import PaymentPage
from pages.components.header_nav import HeaderNavComponent
from test_data.models import TestUsersRepository, get_test_users
from utils.logger import log

try:
    import allure
except ImportError:
    allure = None

# Ensure report output directories exist
REPORTS_DIR = Path("reports")
SCREENSHOTS_DIR = REPORTS_DIR / "screenshots"
TRACES_DIR = REPORTS_DIR / "traces"
VIDEOS_DIR = REPORTS_DIR / "videos"

for directory in [REPORTS_DIR, SCREENSHOTS_DIR, TRACES_DIR, VIDEOS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Regex pattern for aggressive ad and tracker suppression
AD_DOMAINS_PATTERN = re.compile(
    r"(googleads|doubleclick|googleadservices|googlesyndication|adservice\.google|adnxs|amazon-adsystem|scorecardresearch)"
)


def pytest_configure(config: pytest.Config) -> None:
    """Dynamically assign timestamped filename for pytest-html report to prevent overwriting."""
    htmlpath = getattr(config.option, "htmlpath", None)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    reports_dir = Path("reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    if not htmlpath or htmlpath == "reports/report.html" or Path(htmlpath).name == "report.html":
        timestamped_file = str(reports_dir / f"report_{timestamp}.html")
        config.option.htmlpath = timestamped_file
        log.info(f"Assigned timestamped HTML report target: {timestamped_file}")


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """Copy the generated timestamped report to reports/latest_report.html for convenient access."""
    htmlpath = getattr(session.config.option, "htmlpath", None)
    if htmlpath and Path(htmlpath).exists():
        latest_file = Path("reports") / "latest_report.html"
        try:
            shutil.copyfile(htmlpath, latest_file)
            log.info(f"Updated latest report copy at: {latest_file}")
        except Exception as e:
            log.debug(f"Failed to copy latest_report: {e}")


@pytest.fixture(scope="session")
def users() -> TestUsersRepository:
    """Fixture providing loaded test user datasets."""
    return get_test_users()


@pytest.fixture(scope="session")
def playwright_instance() -> Generator[Playwright, None, None]:
    """Session-scoped Playwright engine instance."""
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(playwright_instance: Playwright, request: pytest.FixtureRequest) -> Generator[Browser, None, None]:
    """Session-scoped Browser instance configured from settings or CLI flags."""
    # CLI --headed overrides settings.HEADLESS
    headless = settings.HEADLESS
    try:
        if request.config.getoption("--headed"):
            headless = False
    except Exception:
        pass

    # CLI --slowmo overrides settings.SLOW_MO
    slow_mo = settings.SLOW_MO
    try:
        cli_slowmo = request.config.getoption("--slowmo")
        if cli_slowmo is not None:
            slow_mo = int(cli_slowmo)
    except Exception:
        pass

    launch_args = ["--disable-dev-shm-usage", "--no-sandbox"]
    if not headless:
        launch_args.append("--start-maximized")

    browser_type = getattr(playwright_instance, settings.BROWSER)
    log.info(f"Launching {settings.BROWSER} browser (headless={headless}, slow_mo={slow_mo}ms)")
    browser_instance = browser_type.launch(
        headless=headless,
        slow_mo=slow_mo,
        args=launch_args,
    )
    yield browser_instance
    log.info(f"Closing {settings.BROWSER} browser")
    browser_instance.close()


@pytest.fixture(scope="function")
def context(browser: Browser, request: pytest.FixtureRequest) -> Generator[BrowserContext, None, None]:
    """Function-scoped BrowserContext with tracing and desktop viewport settings."""
    record_video_dir = str(VIDEOS_DIR) if settings.RECORD_VIDEO != "off" else None
    test_name = request.node.name.replace("[", "_").replace("]", "_")

    is_headed = not settings.HEADLESS
    try:
        if request.config.getoption("--headed"):
            is_headed = True
    except Exception:
        pass

    context_kwargs: Dict[str, Any] = {
        "ignore_https_errors": True,
    }
    if is_headed:
        # Adapt to full maximized desktop window
        context_kwargs["no_viewport"] = True
    else:
        context_kwargs["viewport"] = {
            "width": settings.VIEWPORT_WIDTH,
            "height": settings.VIEWPORT_HEIGHT,
        }

    if record_video_dir:
        context_kwargs["record_video_dir"] = record_video_dir
        context_kwargs["record_video_size"] = {
            "width": settings.VIEWPORT_WIDTH,
            "height": settings.VIEWPORT_HEIGHT,
        }

    browser_context = browser.new_context(**context_kwargs)

    # Start Playwright tracing for rich post-mortem analysis
    if settings.RECORD_TRACE != "off":
        browser_context.tracing.start(
            screenshots=True,
            snapshots=True,
            sources=True,
        )

    yield browser_context

    # Handle Tracing Teardown based on test result
    failed = hasattr(request.node, "rep_call") and request.node.rep_call.failed
    if settings.RECORD_TRACE == "on" or (settings.RECORD_TRACE == "retain-on-failure" and failed):
        trace_file = TRACES_DIR / f"{test_name}_trace.zip"
        browser_context.tracing.stop(path=str(trace_file))
        log.info(f"Playwright trace saved to: {trace_file}")
        if allure and trace_file.exists():
            allure.attach.file(
                str(trace_file),
                name=f"{test_name}-trace",
                extension="zip",
            )
    else:
        try:
            browser_context.tracing.stop()
        except Exception:
            pass

    browser_context.close()


@pytest.fixture(scope="function")
def page(context: BrowserContext) -> Generator[Page, None, None]:
    """Function-scoped Page fixture equipped with automatic ad & vignette route blocking."""
    new_page = context.new_page()

    # Network route interception to block advertising networks and overlays
    def block_ads(route):
        try:
            route.abort()
        except Exception:
            pass

    new_page.route(AD_DOMAINS_PATTERN, block_ads)

    # Set default timeout from configuration
    new_page.set_default_timeout(settings.DEFAULT_TIMEOUT)

    yield new_page

    try:
        new_page.close()
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Page Object Fixtures for Dependency Injection
# ---------------------------------------------------------------------------

@pytest.fixture(scope="function")
def home_page(page: Page) -> HomePage:
    """Fixture providing initialized HomePage object."""
    return HomePage(page)


@pytest.fixture(scope="function")
def login_page(page: Page) -> LoginPage:
    """Fixture providing initialized LoginPage object."""
    return LoginPage(page)


@pytest.fixture(scope="function")
def header_nav(page: Page) -> HeaderNavComponent:
    """Fixture providing initialized HeaderNavComponent object."""
    return HeaderNavComponent(page)


@pytest.fixture(scope="function")
def products_page(page: Page) -> ProductsPage:
    """Fixture providing initialized ProductsPage object."""
    return ProductsPage(page)


@pytest.fixture(scope="function")
def contact_us_page(page: Page) -> ContactUsPage:
    """Fixture providing initialized ContactUsPage object."""
    return ContactUsPage(page)


@pytest.fixture(scope="function")
def cart_page(page: Page) -> CartPage:
    """Fixture providing initialized CartPage object."""
    return CartPage(page)


@pytest.fixture(scope="function")
def checkout_page(page: Page) -> CheckoutPage:
    """Fixture providing initialized CheckoutPage object."""
    return CheckoutPage(page)


@pytest.fixture(scope="function")
def payment_page(page: Page) -> PaymentPage:
    """Fixture providing initialized PaymentPage object."""
    return PaymentPage(page)


# ---------------------------------------------------------------------------
# Pytest Hooks for Failure Diagnostics (Screenshots & Allure / HTML Reports)
# ---------------------------------------------------------------------------

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[Any]):
    """Hook wrapper to capture test result status and attach diagnostics upon failure."""
    outcome = yield
    report = outcome.get_result()

    # Attach report outcome to item node for fixture cleanup inspection
    setattr(item, f"rep_{report.when}", report)

    # Attach screenshot and trace on failure during the call phase
    if report.when == "call" and report.failed:
        test_name = item.name.replace("[", "_").replace("]", "_")
        page_fixture: Optional[Page] = item.funcargs.get("page")

        if page_fixture and not page_fixture.is_closed():
            screenshot_path = SCREENSHOTS_DIR / f"{test_name}_failure.png"
            try:
                screenshot_bytes = page_fixture.screenshot(full_page=True)
                with open(screenshot_path, "wb") as f:
                    f.write(screenshot_bytes)
                log.error(f"Captured failure screenshot saved to: {screenshot_path}")

                # Attach to Allure Report
                if allure:
                    allure.attach(
                        screenshot_bytes,
                        name=f"{test_name}-failure-screenshot",
                        attachment_type=allure.attachment_type.PNG,
                    )

                # Attach to pytest-html Report if extra attribute is available
                pytest_html = item.config.pluginmanager.getplugin("html")
                if pytest_html:
                    extra = getattr(report, "extra", [])
                    encoded = base64.b64encode(screenshot_bytes).decode("utf-8")
                    img_html = f'<div><img src="data:image/png;base64,{encoded}" alt="failure" style="width:600px;" /></div>'
                    extra.append(pytest_html.extras.html(img_html))
                    report.extra = extra

            except Exception as ex:
                log.warning(f"Failed to capture diagnostics screenshot: {ex}")
