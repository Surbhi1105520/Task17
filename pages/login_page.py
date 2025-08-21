from playwright.sync_api import Page, expect

class LoginPage:
    def __init__(self, page: Page):
        self.page = page
        self.email_input = page.get_by_placeholder("Enter your mail")
        self.password_input = page.get_by_placeholder("Enter your password")
        self.submit_btn = page.locator("button[type='submit']")

    def visit(self):
        self.page.goto("https://v2.zenclass.in/login", wait_until="domcontentloaded")

    def login(self, email: str, password: str):
        expect(self.email_input).to_be_visible(timeout=10000)
        self.email_input.fill(email)

        expect(self.password_input).to_be_visible(timeout=10000)
        self.password_input.fill(password)

        expect(self.submit_btn).to_be_enabled(timeout=10000)
        self.submit_btn.click()
