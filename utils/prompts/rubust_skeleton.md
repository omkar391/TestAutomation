building rubust framwork: 

Component	Recommendation
Base Class Model after BasePage: include robust navigation retry, custom loading indicator settlement, shadow DOM interaction, and file download support.
Separation of Concerns	Strict rule: Locators & actions in pages/, assertions in tests/. No assertions inside page classes.
Driver & Login Factories	Keep DriverFactory and LoginFactory in core/ to make supporting new platforms (e.g. mobile, desktop, web) straightforward.
Multi-Environment Setup	Use Python class-based inheritance for environments in config/config.py (e.g. QAConfig, StagingConfig, ProdConfig) with environment variable overrides.
API Client Design	Implement IApiClient, RequestBuilder, and an AbstractService base class. This avoids coupling test code to a single HTTP library.
Test Data Isolation	Keep accounts in a central users.json and map them indirectly via @pytest.mark.parametrize("users", ["admin_user"], indirect=True).
Reporting & Artifacts	Implement pytest_runtest_makereport hook early to automatically save failure screenshots, console logs, and failure DOM artifacts.


To build a **production-ready, robust, and zero-flakiness** test automation framework like this repository, follow these core rules grouped into 7 essential pillars:

---

## 1. Architectural & Design Rules

### Rule 1.1: Strict Separation of Concerns (POM Rule)
* **Page Classes (`pages/`)**: Must contain **only** element locators and page interaction methods (actions). They must **never** contain test assertions, test logic, or `print()` statements.
* **Test Files (`tests/`)**: Must contain **only** test flow orchestration and `assert` statements. Tests must **never** contain raw CSS/XPath selectors or direct driver calls.
* **Base Page (`BasePage`)**: Reusable browser interactions (shadow DOM, scroll, file downloads, smart waits) must be encapsulated in `BasePage`. Page objects inherit from `BasePage`.

### Rule 1.2: Use Factories for Extensibility
* Decouple browser and platform creation via **Factory Patterns** (like `DriverFactory` and `LoginFactory`).
* When you add a new platform (e.g., Electron Desktop, Mobile, or a new Browser), you only update the factory—your test suites stay unchanged.

### Rule 1.3: Interface-Driven API Client Layer
* Never bind API tests directly to one library (like `requests`). 
* Define an interface (`IApiClient`) and wrap it with an `AbstractService` and a `RequestBuilder`. This makes authentication token injection, header propagation, and switching between libraries (e.g., `requests` vs Playwright `APIRequestContext`) seamless.

---

## 2. Synchronization & Stability Rules (Zero Flakiness)

Flakiness kills confidence in automated test suites. Follow these synchronization rules:

### Rule 2.1: Ban Hardcoded `time.sleep()` for Element State
* **Never** use `time.sleep(5)` to wait for an element to appear or an action to finish.
* Use **dynamic state waiting**:
  - `locator.wait_for(state="visible")`
  - `locator.wait_for(state="hidden")`
  - `page.wait_for_url(...)`
* If a fixed wait is unavoidable, wrap it in a centralized helper (`BasePage.wait_ms()` or `BasePage.sleep()`) so it can be monitored and optimized later.

### Rule 2.2: Implement "Loading Indicator Settlement"
Modern Single Page Applications (React, Vue, Angular, Lit/Web Components) detach and re-render DOM nodes during network fetches:
* Create a `wait_for_loading_settled()` method in your `BasePage`.
* Before clicking or hovering over buttons, ensure loading indicators (`md-spinner`, skeletons, `[aria-busy="true"]`) have disappeared.

### Rule 2.3: Build Resilient Navigation with Fallback
* Real network environments have transient DNS blips and latency spikes.
* Wrap page navigation (`page.goto`) with a 2-to-3 retry mechanism:
  - Attempt 1: Wait for `"load"`.
  - Attempt 2/3 on timeout: Fall back to `"domcontentloaded"`.

### Rule 2.4: Abstract Shadow DOM Interactions
* Modern design systems frequently use Shadow DOM (`<md-button>`, `<custom-dropdown>`).
* Standard selectors often fail to reach elements inside shadow roots.
* Provide built-in methods like `click_shadow_element()` in `BasePage` that leverage `el.shadowRoot.querySelector(...)` via JavaScript.

---

## 3. Test Design & Execution Rules (Atomicity & Isolation)

### Rule 3.1: Strict Test Atomicity & Independence
* Every test must be **independent** of every other test.
* A test must **never rely on state** created by a previous test.
* Tests must pass when run individually or in parallel (`pytest-xdist`).

### Rule 3.2: Fixture-Driven Setup and Teardown
* **No direct object instantiation** inside tests (e.g., avoid `login_page = LoginPage(driver)` inside a test function).
* Inject page objects and API clients as pytest fixtures:
  ```python
  def test_search_font(login_page, search_page, translations):
      search_page.enter_search_query("Roboto")
      assert search_page.get_results_count() > 0
  ```
* Every fixture that creates resources (files, test accounts, database rows, queues) must include a teardown step (`yield` followed by cleanup code).

### Rule 3.3: Indirect Parametrization for Personas & Test Data
* Use indirect fixtures to switch users or roles cleanly without hardcoding credentials in the test:
  ```python
  @pytest.mark.parametrize("users", ["admin_user"], indirect=True)
  def test_admin_settings(login_page, users):
      ...
  ```

---

## 4. Configuration & Environment Rules

### Rule 4.1: Zero Hardcoded Environments or Credentials
* Never hardcode URLs, client secrets, database passwords, or auth tokens in test files.
* Use a hierarchical configuration structure (e.g., `config/config.py` with `QAConfig`, `StagingConfig`, `ProdConfig`).
* Allow every configuration setting to be overridden via environment variables or a `.env` file (`python-dotenv`):
  ```python
  db_host = os.getenv("DB_HOST", "default-host.internal")
  ```

### Rule 4.2: Dynamic Token Management with Caching
* For API automation with OAuth2:
  - Centralize token retrieval in a `TokenProvider`.
  - Cache tokens in memory per `(url, username, org)` tuple during test suite execution to avoid spamming the authentication provider and getting rate-limited.

---

## 5. Error Handling, Reporting & Debuggability

When a test fails in CI/CD, the engineer must know **why** within 60 seconds without having to re-run the test locally.

### Rule 5.1: Automatic Failure Artifact Capture
Hook into `pytest_runtest_makereport`:
* **Screenshot on Failure**: Take a full-page screenshot (`page.screenshot(full_page=True)`) automatically when a test fails.
* **Browser Console Logs**: Capture `console.error` and `console.warn` outputs and attach them to the report.
* **Structural DOM Snapshot**: On critical failures, dump the current DOM state, active URL, and visible modals to a failure artifact directory (`artifacts/failure_dom/`).

### Rule 5.2: Structured, Centralized Logging
* Never use raw `print()` statements in production test code.
* Use Python’s `logging` module with standardized log formats:
  ```
  %(asctime)s [%(levelname)s] %(name)s - %(message)s
  ```
* Log meaningful action checkpoints (e.g., `"Navigating to URL: ..."`, `"Clicking element: ..."`, `"Waiting for loading to settle"`).

---

## 6. Cross-Platform & OS Portability Rules

If your team runs tests across Windows, macOS, and Linux (Docker/CI):

### Rule 6.1: Path Handling with `pathlib.Path`
* **Never** hardcode path separators (avoid `r"reports\screenshots"` or `reports/screenshots` string concatenation).
* Always use `pathlib.Path`:
  ```python
  from pathlib import Path
  PROJECT_ROOT = Path(__file__).resolve().parent.parent
  SCREENSHOT_DIR = PROJECT_ROOT / "reports" / "screenshots"
  ```

### Rule 6.2: Platform-Specific Event Loop Policies (Windows)
* On Windows, Playwright’s Python synchronous API requires the **Proactor event loop** to launch subprocesses properly.
* Ensure you set this at session start:
  ```python
  if sys.platform == "win32":
      asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
  ```

---

## 7. Code Formatting & Naming Standards

Follow consistent standards across the entire team:

| Item | Convention | Example |
|---|---|---|
| **Page / Service Classes** | PascalCase | `SearchPage`, `WebLoginPage`, `BeaconWorkflow` |
| **Methods / Functions** | snake_case | `enter_username()`, `wait_for_page_ready()` |
| **Locators / Selectors** | snake_case (at class level) | `sign_in_button = "[data-qa-id='sign-in']"` |
| **Constants / Configs** | UPPER_SNAKE_CASE | `DEFAULT_TIMEOUT = 10000`, `CONNECT_CDP_PORT` |
| **Test Files** | `test_<feature>.py` | `test_search_page.py`, `test_filters.py` |
| **Test Methods** | `test_<action_or_scenario>()` | `test_font_cards_visible_on_search_results()` |
| **Test Categories** | Pytest Markers | `@pytest.mark.smoke`, `@pytest.mark.regression` |

---

### Summary Checklist for Your New Repository

1. [ ] **`core/`**: `BasePage`, `DriverFactory`, and `Platform` abstraction created.
2. [ ] **`config/`**: Multi-environment classes (`QAConfig`, `StagingConfig`) with `.env` overrides.
3. [ ] **`pages/`**: Strict POM (no assertions, no `time.sleep`, shadow DOM handled).
4. [ ] **`tests/conftest.py`**: Fixture-driven injection, automated failure screenshots, and console log capture.
5. [ ] **`api/`**: `IApiClient`, `RequestBuilder`, `TokenProvider`, and service classes separated.
6. [ ] **`pytest.ini`**: Markers registered, live logging enabled, and standard execution flags defined.
7. [ ] **`requirements.txt`**: Pinned dependencies for CI reproducibility.