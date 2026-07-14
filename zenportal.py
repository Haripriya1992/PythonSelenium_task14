import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# ---- test data ----
VALID_EMAIL = "haripriyamadhavaraj@gmail.com"
VALID_PASSWORD = "Hari@1992"

INVALID_EMAIL = "wrong_user@example.com"
INVALID_PASSWORD = "wrongpass123"


# ======================================================================
# PAGE OBJECT CLASS (OOP + Page Object Model)
# ======================================================================
class ZenLoginPage:
    URL = "https://www.zenclass.in/login"

    EMAIL_FIELD = (By.XPATH, "//input[@placeholder='Enter your mail']")
    PASSWORD_FIELD = (By.XPATH, "//input[contains(@placeholder,'password')]")
    SUBMIT_BTN = (By.CSS_SELECTOR, "button.primary-btn.sign-in-pad")
    AVATAR_ICON = (By.CSS_SELECTOR, ".avatar-container")
    LOGOUT_BTN = (By.XPATH, "//div[@class='user-avatar-menu' and contains(text(),'Log out')]")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)  # Explicit Wait

    def load(self):
        self.driver.get(self.URL)

    def _find(self, locator):
        try:
            return self.wait.until(EC.presence_of_element_located(locator))
        except TimeoutException:
            raise NoSuchElementException(f"Element not found: {locator}")

    def _click(self, locator):
        try:
            element = self.wait.until(EC.element_to_be_clickable(locator))
            element.click()
        except TimeoutException:
            raise NoSuchElementException(f"Element not clickable: {locator}")

    def is_visible(self, locator):
        try:
            return self.wait.until(EC.visibility_of_element_located(locator)).is_displayed()
        except TimeoutException:
            return False

    def enter_email(self, email):
        self._find(self.EMAIL_FIELD).send_keys(email)

    def enter_password(self, password):
        self._find(self.PASSWORD_FIELD).send_keys(password)

    def click_submit(self):
        self._click(self.SUBMIT_BTN)

    def login(self, email, password):
        self.enter_email(email)
        self.enter_password(password)
        self.click_submit()

    def logout(self):
        """Logout is inside a dropdown - click the avatar icon first
        to reveal the menu, then click 'Log out' inside it."""
        self._click(self.AVATAR_ICON)
        self._click(self.LOGOUT_BTN)

    def wait_for_url_change(self, old_url):
        try:
            self.wait.until(lambda d: d.current_url != old_url)
            return True
        except TimeoutException:
            return False

@pytest.fixture()
def driver():
    drv = None
    try:
        drv = webdriver.Chrome()
        drv.maximize_window()
        yield drv
    finally:
        if drv is not None:
            drv.quit()

# a) Successful Login (positive)
def test_a_successful_login(driver):
    zen = ZenLoginPage(driver)
    zen.load()
    old_url = driver.current_url

    zen.login(VALID_EMAIL, VALID_PASSWORD)
    zen.wait_for_url_change(old_url)

    print("URL after successful login:", driver.current_url)
    assert driver.current_url != old_url


# b) Unsuccessful Login (negative)
def test_b_unsuccessful_login(driver):
    zen = ZenLoginPage(driver)
    zen.load()
    old_url = driver.current_url

    zen.login(INVALID_EMAIL, INVALID_PASSWORD)
    zen.wait_for_url_change(old_url)

    print("URL after failed login:", driver.current_url)
    # login should fail, so URL should stay the same
    assert driver.current_url == old_url


# c) Validate Username, Password input box (positive)
def test_c_validate_username_password_fields(driver):
    zen = ZenLoginPage(driver)
    zen.load()

    assert zen.is_visible(zen.EMAIL_FIELD), "Email field not visible"
    assert zen.is_visible(zen.PASSWORD_FIELD), "Password field not visible"


# d) Validate Submit button working or not (positive)
def test_d_validate_submit_button(driver):
    zen = ZenLoginPage(driver)
    zen.load()

    assert zen.is_visible(zen.SUBMIT_BTN), "Submit button not visible"

    old_url = driver.current_url
    zen.login(VALID_EMAIL, VALID_PASSWORD)
    changed = zen.wait_for_url_change(old_url)

    print("Did submit button navigate anywhere?", changed)
    assert changed


# e) Validate the functionality of the Logout button (positive)
def test_e_validate_logout_functionality(driver):
    zen = ZenLoginPage(driver)
    zen.load()

    zen.login(VALID_EMAIL, VALID_PASSWORD)
    zen.wait_for_url_change(zen.URL)
    dashboard_url = driver.current_url

    assert zen.is_visible(zen.LOGOUT_BTN), "Logout button not visible after login"
    zen.logout()
    zen.wait_for_url_change(dashboard_url)

    print("URL after logout:", driver.current_url)
    assert driver.current_url != dashboard_url

if __name__ == "__main__":
    pytest.main([
        __file__,
        "-v",
        "--html=report.html",
        "--self-contained-html"
    ])