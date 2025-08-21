import re
from playwright.sync_api import Page, Locator, expect

class DashboardPage:
    def __init__(self, page: Page):
        self.page = page
        self.title: Locator = page.locator("p.header-name:has-text('Dashboard'))").first
        self.profile_trigger: Locator = page.locator(
            "button[aria-label*=profile i], button[aria-label*=account i], "
            "img[alt*=profile i], img[alt*=user i], "
            ".MuiAvatar-root, .chakra-avatar, .ant-avatar, "
            "[data-testid='Avatar'], [data-testid='account-menu'], "
            "header :is(button,a,div)[class*='user' i], "
            "nav :is(button,a,div)[class*='user' i]"
        ).first

        # Backdrops / modals that often intercept clicks
        self.backdrops: Locator = page.locator(
            ".MuiBackdrop-root, .MuiModal-backdrop, .MuiModal-root, [role='dialog']"
        )
        # Menu container (common MUI/Ant/Chakra patterns)
        self.user_menu: Locator = page.locator(
            "[role='menu'], .MuiMenu-paper, .ant-dropdown, .chakra-menu__menu-list, .user-avatar-menu"
        )

    # ------ helpers ------
    def wait_loaded(self, timeout: int = 15000):
        expect(self.page).not_to_have_url(re.compile(r"/login", re.I), timeout=timeout)
        expect(self.page).to_have_url(re.compile(r"/dashbo?o?ard", re.I), timeout=timeout)
        expect(self.title).to_be_visible(timeout=timeout)

    def is_logged_in(self) -> bool:
        try:
            self.wait_loaded(timeout=12000)
            return True
        except Exception:
            return False

    def _dismiss_any_modal(self, timeout_ms: int = 2000):
        """
        Best-effort to clear overlays that intercept clicks.
        """
        # Try ESC a couple of times
        for _ in range(2):
            try:
                self.page.keyboard.press("Escape")
            except Exception:
                pass

        # Try common close buttons
        close_candidates = [
            "[aria-label='Close']",
            "[aria-label='close']",
            "role=button[name=/close|cancel|dismiss/i]",
            "button:has-text('Close')",
            "button:has-text('Cancel')",
            "button:has-text('Dismiss')",
            "button.MuiButton-root:has-text('Close')",
        ]
        for sel in close_candidates:
            btn = self.page.locator(sel).first
            if btn.count() and btn.is_visible():
                try:
                    btn.click(timeout=600)
                except Exception:
                    pass

        # Click the visible backdrop itself (often closes modals)
        vis_backdrop = self.backdrops.locator(":visible").first
        if vis_backdrop.count():
            try:
                vis_backdrop.click(timeout=600)
            except Exception:
                pass

        # Give it a short moment
        self.page.wait_for_timeout(200)

    def _open_profile_menu(self):
        expect(self.profile_trigger).to_be_visible(timeout=12000)

        # clear overlays, then click avatar
        self._dismiss_any_modal()
        try:
            self.profile_trigger.click(timeout=12000)
        except Exception:
            handle = self.profile_trigger.element_handle()
            if handle:
                self.page.evaluate("el => el.click()", handle)
            else:
                raise AssertionError("Profile trigger has no element handle.")

        # ✅ The locator matches multiple elements; assert on a single one
        expect(self.user_menu.first).to_be_visible(timeout=8000)


  
    # ------ main action ------
    def logout(self):
        """
        Open the user menu and click Logout. Expect to land on /login.
        """
        self._open_profile_menu()

        # Try your exact DOM target first
        candidates = [
            "//div[@class='user-avatar-menu' and normalize-space()='Log out']",
            "role=menuitem[name=/log\\s*out|sign\\s*out/i]",
            "text=/^\\s*Log\\s*out\\s*$/i",
            "button:has-text('Logout')",
            "a:has-text('Logout')",
            "[data-testid='logout']",
            "a[href*='logout']",
            "button[id*='logout' i]",
            "button[name*='logout' i]",
        ]

        for sel in candidates:
            item = self.page.locator(sel).first
            if item.count():
                try:
                    expect(item).to_be_visible(timeout=6000)
                    item.click(timeout=6000)
                    break
                except Exception:
                    continue
        else:
            raise AssertionError("Logout control not found in the opened menu.")

        # Verify we returned to /login
        expect(self.page).to_have_url(re.compile(r"/login", re.I), timeout=15000)
