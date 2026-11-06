# QA Automation Framework Pre-PR Code Review Checklist

This checklist defines the review criteria across all 12 Phases of the Pre-PR inspection process.

---

## Phase 1 & 2: Architecture & Separation of Concerns (POM)
- [ ] **Page Classes (`pages/`)**:
  - Contain only locators, component references, and action methods.
  - Zero assertions (`assert`) inside page classes.
  - Zero test scenario orchestration or business validation logic.
  - Zero raw `print()` statements (use `log.step()` / `log.info()`).
- [ ] **Test Files (`tests/`)**:
  - Contain test flow orchestration, business validation, and assertions only.
  - Zero raw CSS/XPath selectors or direct driver calls bypassing Page Objects.
  - No direct page object instantiation (`LoginPage(page)`) when Pytest fixtures exist.
- [ ] **BasePage (`pages/base_page.py`)**:
  - Encapsulates truly generic browser interactions (smart waits, scroll, shadow DOM, file downloads).
  - No page-specific or one-off logic pushed into BasePage.
- [ ] **Components (`pages/components/`)**:
  - Shared UI sections (Header, Footer, Modals, Navbars) separated into dedicated components.

---

## Phase 3: Synchronization & Flakiness Prevention
- [ ] **Zero Hardcoded Sleeps**:
  - No `time.sleep()` for waiting on elements or network state.
  - Uses Playwright dynamic waits (`locator.wait_for()`, `page.wait_for_url()`, auto-waiting).
- [ ] **Loading-State Settlement**:
  - Spinners, skeletons, and `[aria-busy="true"]` indicators handled via centralized wait methods.
- [ ] **Navigation & Retries**:
  - Proper navigation timeout handling; retries applied only where justified to avoid masking genuine defects.
- [ ] **Shadow DOM**:
  - Handled via framework BasePage methods, avoiding repetitive JavaScript shadow-root scripts.

---

## Phase 4: Test Design & Fixture Architecture
- [ ] **Test Independence**:
  - Tests do not rely on execution order or side-effects from preceding tests.
  - Safe for parallel execution (`pytest -n auto`).
- [ ] **Fixture Usage & Placement**:
  - Shared fixtures live in `conftest.py`.
  - Proper fixture teardown via `yield`.
- [ ] **Data Management & Parametrization**:
  - Test data centralized in `test_data/users.json` and Pydantic models in `test_data/models.py`.
  - Personas injected via indirect parametrization.

---

## Phase 5: Configuration & Security
- [ ] Zero hardcoded credentials, passwords, auth tokens, or API secrets.
- [ ] Zero hardcoded environment URLs or local file system paths.
- [ ] Settings managed via `.env` / `config/settings.py`.

---

## Phase 6: Reporting & Observability
- [ ] Zero `print()` statements; uses `utils.logger.log` with structured, action-oriented logs.
- [ ] Failure screenshots, Playwright traces, and console logs captured via existing hooks without duplicate handlers.

---

## Phase 7 & 8: Code Quality, Typing & Naming Conventions
- [ ] Strict PEP 484 type hints across all page methods, component methods, and fixtures.
- [ ] Uses `pathlib.Path` for filesystem operations (cross-platform compatible).
- [ ] Zero unused imports, circular imports, dead code, or duplicate locators.
- [ ] Naming standards:
  - Classes: `PascalCase`
  - Methods / Functions / Locators: `snake_case`
  - Constants: `UPPER_SNAKE_CASE`
  - Test files: `test_<feature>.py`
  - Test functions: `test_<scenario>()`
  - Markers: `snake_case`

---

## Phase 9 & 10: Duplication & Reuse Analysis
- [ ] Identified any duplicate locators, helper functions, modals, or assertions.
- [ ] Existing methods and fixtures reused rather than re-implemented.

---

## Phase 11 & 12: Test Quality & PR Safety
- [ ] Test objectives are clear with meaningful assertions (no weakened or removed assertions).
- [ ] Safe validation: Analysis first without modifying code until explicit approval.
- [ ] Pytest test collection verified (`python -m pytest --collect-only -q`).
- [ ] Minimal and clean git diff.
