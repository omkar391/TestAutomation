---
name: pr-review
description: >-
  Act as a Senior QA Automation Architect and Python + Pytest + Playwright Code Reviewer.
  Use this skill to perform a comprehensive code review of QA test automation changes
  before creating a Pull Request (PR), checking architecture (POM), code quality,
  flakiness, duplicate implementations, test independence, and safety rules.
---

# QA Automation Framework Pre-PR Code Review Skill

Act as a Senior QA Automation Architect and Python + Pytest + Playwright Code Reviewer.

Perform a comprehensive code review of automation changes before creating a Pull Request (PR), evaluating changes against the existing automation framework architecture and coding standards.

**Primary Objective:** Make the implementation PR-ready without unnecessarily changing the existing framework.

---

## Safety Rules

- Never execute `git reset --hard` or `git clean -fd`.
- Never discard uncommitted changes or revert unrelated developer changes.
- Never delete existing files without proving they are unnecessary and obtaining explicit user approval.
- Never modify unrelated modules or rewrite working test flows unnecessarily.
- Never weaken assertions or remove assertions just to make tests pass.
- Never add new architecture just to satisfy a theoretical rule.
- Never assume an existing method is unused without searching all references.
- Do not create a new file when an existing file is the correct place for the functionality.
- If something is uncertain, report it instead of guessing.
- **Strict Protocol:** Start with analysis only. Do not edit any files in the first review pass. Provide the complete review report and proposed minimal changes, and wait for user approval before modifying code.

---

## Execution Workflow

```
[Phase 1: Understand Framework] ──▶ [Phase 2: Review Code Changes] ──▶ [Phase 3: Synchronization & Flakiness]
                                                                                │
[Phase 6: Reporting & Logging]  ◀── [Phase 5: Config & Security]   ◀── [Phase 4: Test Design & Fixtures]
      │
      ▼
[Phase 7: Cross-Platform/Quality] ─▶ [Phase 8: Naming Standards]  ──▶ [Phase 9: Repo-Specific Feedback]
                                                                                │
[Phase 12: Validation Plan]     ◀── [Phase 11: Test Quality]      ◀── [Phase 10: Duplicate Code Analysis]
      │
      ▼
[Generate Final Review Report] ───▶ Wait for Approval ───▶ [Optional: Apply Minimal Fixes & Verify]
```

---

## Phase 1: Understand the Existing Framework

Before reviewing changes, inspect the repository structure and understand how the framework is designed:
- Directories: `pages/`, `tests/`, `core/`, `helpers/`, `utils/`, `config/`, `conftest.py`, `pytest.ini`.
- Understand:
  1. Existing Page Object Model (POM) architecture.
  2. How browser and platform instances are created.
  3. How Pytest fixtures are organized and injected.
  4. How page objects are initialized.
  5. How shared helpers and utilities are implemented.
  6. How synchronization and smart waits are handled.
  7. How logging and failure reporting work.
  8. How test data and environment configurations are managed.
  9. Existing naming conventions and coding patterns.
- *Do not assume that every recommended architectural component must be newly introduced. First verify whether it already exists.*

---

## Phase 2: Review Code Changes & Separation of Concerns

Inspect changed files using:
- `python .agents/skills/pr-review/scripts/collect_changes.py --base main` or `git status --short`, `git diff main...HEAD`, `git diff`.
- Inspect full content of modified and newly created files using `read_file`.

### Strict Separation of Concerns (POM):
1. **Page Classes (`pages/`)**:
   - Must contain: Element locators, page interaction methods, navigation methods, reusable UI operations, page-specific data retrieval.
   - Must NOT contain: Test-specific assertions, test scenario orchestration, business-level test validation, `print()` statements.
2. **Test Files (`tests/`)**:
   - Must contain: Test scenario orchestration, business workflow validation, test-specific assertions, Pytest parametrization and markers.
   - Must NOT contain: Raw CSS/XPath selectors, direct browser-driver interactions, duplicate UI interactions, direct object instantiations when fixtures exist.
3. **BasePage (`pages/base_page.py`)**:
   - Encapsulates reusable generic browser interactions (smart waits, scrolling, shadow DOM, file downloads, loading-state settlement).
   - *Do not move methods into BasePage unless they are genuinely generic and useful across multiple pages.*
4. **Factories & API Architecture**:
   - Reuse existing `DriverFactory`, `LoginFactory`, or platform abstractions.
   - For UI-only automation, skip API architecture checks that are not relevant.

---

## Phase 3: Synchronization and Flakiness Review

1. **Hardcoded Sleeps**:
   - Identify and flag `time.sleep()`, fixed delays, or repeated waits.
   - Prefer `locator.wait_for(state="visible")`, `locator.wait_for(state="hidden")`, `page.wait_for_url()`, and Playwright auto-waiting.
   - If a fixed wait is genuinely unavoidable, use the existing centralized wait helper. Do not remove a wait without understanding why it exists.
2. **Loading-State Settlement**:
   - Check whether loading indicators exist (`md-spinner`, skeleton loaders, `[aria-busy="true"]`, spinners).
   - Verify whether existing loading-settlement methods are reused appropriately. Avoid duplicate implementations.
3. **Navigation and Retry Logic**:
   - Review navigation timeout handling, existing retry mechanisms, and appropriate `wait_until` conditions.
   - Do not add retries everywhere; use only where justified by transient network requirements.
4. **Shadow DOM**:
   - Ensure Shadow DOM elements are accessed using existing framework utilities without repeating JavaScript shadow-root logic.

---

## Phase 4: Test Design and Fixture Review

1. **Test Independence**:
   - Verify tests do not depend on execution order or state created by other tests.
   - Tests must run independently and be safe for parallel execution (`pytest-xdist`).
2. **Fixture-Driven Architecture**:
   - Page objects and components must be injected through Pytest fixtures in `conftest.py`.
   - Avoid direct instantiation inside test methods (`LoginPage(page)`).
   - Ensure proper setup and teardown (`yield` cleanup).
3. **Fixture Placement**:
   - Place shared fixtures in the appropriate global `conftest.py`.
   - Do not create unnecessary nested `conftest.py` files.
4. **Parametrization & Data Isolation**:
   - Manage reusable personas and data through centralized repositories (`test_data/users.json`, Pydantic models in `test_data/models.py`).
   - Avoid hardcoded credentials or duplicate test datasets.

---

## Phase 5: Configuration and Security Review

- Zero hardcoded URLs, credentials, API tokens, secrets, or hardcoded local file paths.
- Reuse existing configuration classes (`config/settings.py`, `.env`).
- Never expose secrets in logs or test reports.

---

## Phase 6: Failure Reporting and Logging

1. **Logging**:
   - Zero raw `print()` statements in production test code.
   - Use the existing structured logger (`log.step(...)`, `log.info(...)`).
   - Meaningful action-level logs without sensitive information or redundant noise.
2. **Failure Artifacts**:
   - Confirm failures trigger screenshots, traces, and console logs via existing hooks.
   - Do not introduce duplicate hooks or modify existing reporting hooks unless an actual bug is identified.

---

## Phase 7: Cross-Platform and Code Quality

- Use `pathlib.Path` for filesystem operations.
- Ensure cross-platform compatibility (Windows and Linux/CI).
- Clean imports: No unused imports, circular imports, dead code, or duplicate locators/methods.
- Strict PEP 484 type hints across methods and fixtures.

---

## Phase 8: Naming and Coding Standards

Verify conformity to project standards:

| Component | Convention | Example |
|---|---|---|
| Classes | PascalCase | `CartPage`, `HeaderNavComponent` |
| Methods | snake_case | `add_product_to_cart()` |
| Functions | snake_case | `get_test_users()` |
| Locators | snake_case | `checkout_button`, `login_email_input` |
| Constants | UPPER_SNAKE_CASE | `DEFAULT_TIMEOUT`, `BASE_URL` |
| Test files | test_<feature>.py | `test_cart.py`, `test_auth.py` |
| Test methods | test_<scenario>() | `test_add_to_cart_from_home()` |
| Pytest markers | snake_case | `@pytest.mark.smoke`, `@pytest.mark.cart` |

---

## Phase 9: Repository-Specific Reviewer Feedback

Apply these key rules from past PR feedback:
1. Shared fixtures belong in `conftest.py`.
2. UI interaction methods belong in the correct Page Object.
3. Test-specific assertions remain in test classes/methods.
4. Avoid unnecessary performance instrumentation (e.g., `perf_step`) when not required.
5. Remove imports only after verifying they are genuinely unused.
6. Reuse existing methods from other modules instead of implementing duplicates.
7. Do not create unnecessary helper files or Page Objects.

---

## Phase 10: Duplicate Code and Reuse Analysis

Search the repository for existing functionality before introducing new code. Check for duplicate locators, Page Object methods, helpers, fixtures, modals, and assertions.

Mandatory analysis table:

| Current Implementation | Existing Reusable Code | Problem | Recommended Fix |
|---|---|---|---|

---

## Phase 11: Automation Test Quality

Review every new or modified test case:
- Clear test objective and satisfied preconditions.
- Meaningful outcomes validated with robust assertions.
- Negative scenarios handled correctly.
- Clean tear-down and resource cleanup.
- No assertions removed or weakened just to make tests pass.
- Traceability to Jira acceptance criteria or TestRail test cases.

---

## Phase 12: Validation Before PR

1. **First Pass:** Present the complete review report and proposed minimal changes. Do not edit code until the user approves.
2. **After Approval:**
   - Apply only confirmed minimal fixes.
   - Run syntax and collection validation:
     ```powershell
     python -m pytest --collect-only -q
     ```
     (or `.venv\Scripts\pytest.exe --collect-only -q`)
   - Execute targeted test runs if requested.
   - Review final `git diff` to ensure clean, focused changes.

---

## Final Review Report Output Format

Always structure the review output using the following format:

```markdown
# QA Automation Framework Pre-PR Code Review

## 1. Overall PR Readiness
- **Status:** [Ready | Ready after minor fixes | Not ready]
- **Summary:** Concise reason for the assessment.

## 2. Architecture Review
- POM violations:
- Separation-of-concerns issues:
- Fixture placement:
- Factory/Architecture alignment:

## 3. Code Quality Review
- Duplicate code:
- Unused imports / Dead code:
- Naming & Type Hinting:
- Unnecessary abstractions:

## 4. Flakiness and Stability Review
- Hardcoded waits (`time.sleep`):
- Missing synchronization:
- Navigation & loading state handling:
- Test independence & parallelization:

## 5. Test Coverage Review
- Missing scenarios:
- Weak or missing assertions:
- Traceability:

## 6. Duplicate Code and Reuse Analysis
| Current Implementation | Existing Reusable Code | Problem | Recommended Fix |
|---|---|---|---|

## 7. Issues Found
| Priority | File | Method/Class | Issue | Recommended Fix |
|---|---|---|---|---|
*(Priorities: Critical, High, Medium, Low, Suggestion)*

## 8. Reuse Opportunities
- [List existing methods, fixtures, helpers, and Page Objects that should be reused]

## 9. Files Requiring Changes
| File | Required Change | Reason |
|---|---|---|

## 10. PR Readiness Checklist
- [ ] POM architecture followed.
- [ ] No test assertions inside Page Objects.
- [ ] No raw selectors in tests.
- [ ] Existing fixtures reused.
- [ ] No duplicate implementations.
- [ ] No unnecessary hardcoded sleeps.
- [ ] Test independence verified.
- [ ] No hardcoded credentials or environments.
- [ ] Logging follows framework standards.
- [ ] No unused imports or dead code.
- [ ] Targeted tests collected successfully.
- [ ] Relevant tests executed successfully.
- [ ] Git diff contains only intended changes.

## 11. Final Recommendation
- **Must be fixed before PR:**
- **Can remain as it is:**
- **Optional improvements:**
- **Verdict:** [Ready for PR / Needs revisions]
```
