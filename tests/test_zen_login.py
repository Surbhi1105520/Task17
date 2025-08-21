import re
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from playwright.sync_api import expect

ZEN_URL = "https://v2.zenclass.in/login"
def test_successful_login(page):
    login_page = LoginPage(page)
    # Visit login
    login_page.visit()
    login_page.login("surbh@gmail.com", "Avni2575")
    assert "/dashboard" in page.url, "Should redirect to dashboard after successful login"
    
def test_unsuccessful_login(page):
    login_page = LoginPage(page)
    login_page.visit()
    login_page.login("wronguser@gmail.com", "WrongPassword123")

    # Expect still on login page
    assert "/login" in page.url, "Should remain on login page with invalid credentials"

    # Optionally check for error message
    error_msg = page.locator("text=Invalid").first
    assert error_msg.is_visible(timeout=5000)


def test_login_input_boxes(page):
    
    page.goto(ZEN_URL, wait_until="domcontentloaded")
    email = (page.get_by_placeholder("Enter your mail").or_(page.get_by_placeholder(re.compile(r"(mail|email)", re.I))).first)
    password = (page.get_by_placeholder("Enter your password").or_(page.get_by_placeholder(re.compile(r"password", re.I))).first
    )

    # Submit button (role-first, then CSS fallback)
    submit = page.get_by_role(
        "button", name=re.compile(r"(submit)", re.I)).first
    if not submit.count():
        submit = page.locator("button[type='submit'], input[type='submit']").first

    # Visibility & enabled checks
    expect(email).to_be_visible(timeout=12000)
    expect(password).to_be_visible(timeout=12000)
    expect(submit).to_be_visible(timeout=12000)

    # Type checks (ensure the boxes accept input)
    email.fill("dummy@example.com")
    assert email.input_value() == "dummy@example.com", "Email box did not accept input"

    password.fill("DummyPass123!")
    assert password.input_value() == "DummyPass123!", "Password box did not accept input"

    # Optional: submit button enabled (may depend on form validation rules)
    assert submit.is_enabled(), "Submit button should be enabled (or enable after inputs)"

VALID_EMAIL = "surbhi11@gmail.com"
VALID_PASS  = "Avni2575"

def test_submit_button_with_invalid_credentials(page):
    """
    Check submit button works: clicking with invalid creds should keep us on /login.
    """
    page.goto(ZEN_URL, wait_until="domcontentloaded")

    email = page.get_by_placeholder("Enter your mail").first
    password = page.get_by_placeholder("Enter your password").first
    submit = page.locator("button[type='submit']").first

    # Fill invalid creds
    email.fill("wrong@example.com")
    password.fill("WrongPass123")

    expect(submit).to_be_enabled()
    submit.click()

    # Stay on login page
    page.wait_for_url("**/login")
    assert "/login" in page.url, "Submit button click should not allow invalid login"

    # Optionally check toast/error
    error_toast = page.locator("text=Invalid").first
    assert error_toast.is_visible(timeout=5000), "Error message not shown for invalid login"


def test_submit_button_with_valid_credentials(page):
    """
    Check submit button works: clicking with valid creds should take us to dashboard.
    """
    page.goto(ZEN_URL, wait_until="domcontentloaded")

    email = page.get_by_placeholder("Enter your mail").first
    password = page.get_by_placeholder("Enter your password").first
    submit = page.locator("button[type='submit']").first

    # Fill valid creds
    email.fill(VALID_EMAIL)
    password.fill(VALID_PASS)

    expect(submit).to_be_enabled()
    submit.click()

    # Should go to dashboard
    page.wait_for_url("**/dashboard", timeout=15000)
    assert "/dashboard" in page.url, "Submit button click should log in successfully"

def test_logout_functionality(page):
    """
    Test logout functionality from the dashboard.
    """
    # First, log in with valid credentials
    login_page = LoginPage(page)
    login_page.visit()
    login_page.login(VALID_EMAIL, VALID_PASS)

    # Ensure we are on the dashboard
    assert "/dashboard" in page.url, "Should redirect to dashboard after successful login"

    # Now, perform logout
    dashboard_page = DashboardPage(page)
    dashboard_page.logout()

    # Check we are back on the login page
    assert "/login" in page.url, "Should redirect to login page after logout"

