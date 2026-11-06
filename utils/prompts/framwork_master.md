Act as a Principal SDET and Test Automation Architect. 

Your objective is to generate a production-ready, enterprise-grade UI test automation framework from scratch using Python, pytest, and Playwright. 

Target Application: https://www.automationexercise.com/
Repository Name : UIAutomatio
Scope: Strictly UI End-to-End automation (NO API tests).
Repository & Version Control: GitHub with GitHub Actions CI/CD.

Please build the complete codebase adhering to the following strict enterprise architecture and engineering standards:

---

### 1. Framework Architecture & Design Patterns
- Design Pattern: Page Object Model (POM) combined with Component Object Pattern for shared UI elements (Header, Navigation Bar, Footer, Modals).
- Strict Type Hinting: Enforce PEP 484 type hints across all pages, fixtures, and utility functions (e.g., `Page`, `Locator`, `Optional[str]`).
- Locator Strategy: Follow Playwright best practices—prioritize user-facing, accessibility-first locators (`page.get_by_role`, `page.get_by_label`, `page.get_by_placeholder`, `page.get_by_text`) and resilient data attributes (`data-qa`), avoiding fragile absolute XPaths.
- Ad & Popup Suppression: Implement network route aborts in `conftest.py` to block Google Vignette / ad iframe domains (automationexercise.com is notoriously ad-heavy and blocks UI interactions).

---

### 2. Required Directory Structure
Generate code and configurations for the following layout:
```text
├── .github/
│   └── workflows/
│       └── e2e-tests.yml        # Multi-browser matrix CI pipeline with artifact upload
├── config/
│   └── settings.py              # Pydantic or env-based config (timeouts, base_url, browser)
├── pages/
│   ├── base_page.py             # Reusable Playwright wrappers with explicit waits & logging
│   ├── components/
│   │   ├── header_nav.py        # Shared top navigation component
│   │   └── footer.py            # Shared footer/subscription component
│   ├── home_page.py             # Home page actions
│   ├── login_page.py            # Authentication & Signup page
│   └── products_page.py         # Catalog, search, product detail, and cart modal
├── tests/
│   ├── conftest.py              # Pytest hooks, fixtures (browser context, ad blocker, screenshot on failure)
│   ├── test_auth.py             # Login, logout, invalid credentials tests
│   └── test_products.py         # Search, filter, and add-to-cart tests
├── test_data/
│   ├── models.py                # Pydantic models for user & product data
│   └── users.json               # Seed test data
├── utils/
│   └── logger.py                # Centralized structured logging (loguru or Python logging)
├── .env.example                 # Example environment variables
├── .gitignore                   # Comprehensive Python & Playwright gitignore
├── pytest.ini                   # Pytest options, markers, base URL, reporting flags
├── requirements.txt             # Pinned enterprise dependencies
└── README.md                    # Setup, execution, parallelization, and debugging guide
```

---

### 3. Core Technical Specifications

1. Configuration & Environments:
   - Read configurations dynamically from `.env` using `pydantic-settings` or `python-dotenv` with sensible defaults (base URL: `https://www.automationexercise.com`, headless: True, default timeout: 15s).

2. Fixtures & Hooks (`tests/conftest.py`):
   - Fixture for browser context initialization with custom viewport, trace recording, and video capture.
   - Network interception fixture to automatically block ad domains (`*googleads*`, `*doubleclick*`, `*adservice*`).
   - `pytest_runtest_makereport` hook to automatically attach full-page screenshots and Playwright trace files to Allure / HTML reports on test failure.

3. Logging & Observability:
   - Structured logger logging every significant page action (e.g., "[CLICK] Clicking on 'Signup / Login' button", "[INPUT] Entering text into email field").
   - Test outputs integrated with both `allure-pytest` and `pytest-html`.

4. Test Suite Execution & Parallelism:
   - Configured for parallel execution using `pytest-xdist` (`pytest -n auto`).
   - Categorized test cases using custom Pytest markers (`@pytest.mark.smoke`, `@pytest.mark.regression`).
   - Configured test retries using `pytest-rerunfailures` for handling transient network issues.

5. CI/CD & Code Quality:
   - Complete GitHub Actions workflow file (`.github/workflows/e2e-tests.yml`) executing tests in headless mode across Chromium and Firefox, generating test reports, and uploading traces/screenshots as build artifacts.
   - Production `.gitignore` ensuring zero local artifacts, reports, caches, or virtualenvs are committed.

---

### 4. Deliverables Required
Provide the **complete, fully written code** for every key file:
1. `requirements.txt` & `pytest.ini`
2. `config/settings.py` & `.env.example`
3. `utils/logger.py`
4. `pages/base_page.py` & `pages/components/header_nav.py`
5. `pages/home_page.py`, `pages/login_page.py`, & `pages/products_page.py`
6. `tests/conftest.py`
7. `tests/test_auth.py` & `tests/test_products.py`
8. `.github/workflows/e2e-tests.yml`
9. `.gitignore`

Do not provide stubs, placeholder comments, or truncated snippets. Write out the actual implementation ready to be cloned and executed.