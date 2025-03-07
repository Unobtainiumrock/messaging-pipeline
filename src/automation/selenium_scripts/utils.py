"""Selenium utilities for web automation."""
import logging
import time
from typing import Optional, Dict, Any, Callable
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)


def create_driver(headless: bool = True) -> webdriver.Chrome:
    """
    Create and configure a Chrome WebDriver instance.

    Args:
        headless: Whether to run Chrome in headless mode

    Returns:
        WebDriver: Configured Chrome WebDriver instance
    """
    logger.info("Setting up Chrome WebDriver")
    chrome_options = webdriver.ChromeOptions()

    if headless:
        chrome_options.add_argument("--headless")

    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.maximize_window()

    # Set default timeout
    driver.implicitly_wait(10)

    logger.info("Chrome WebDriver created successfully")
    return driver


def safe_find_element(
    driver: webdriver.Chrome,
    by: By,
    value: str,
    timeout: int = 10,
    wait_condition: str = "presence",
) -> Optional[webdriver.remote.webelement.WebElement]:
    """
    Safely find an element with timeout.

    Args:
        driver: WebDriver instance
        by: Locator type (e.g., By.ID)
        value: Locator value
        timeout: Maximum wait time in seconds
        wait_condition: Type of wait condition (presence, visibility, clickable)

    Returns:
        WebElement if found, None otherwise
    """
    try:
        wait = WebDriverWait(driver, timeout)

        if wait_condition == "presence":
            condition = EC.presence_of_element_located((by, value))
        elif wait_condition == "visibility":
            condition = EC.visibility_of_element_located((by, value))
        elif wait_condition == "clickable":
            condition = EC.element_to_be_clickable((by, value))
        else:
            logger.warning(f"Unknown wait condition: {wait_condition}, using presence")
            condition = EC.presence_of_element_located((by, value))

        element = wait.until(condition)
        return element

    except TimeoutException:
        logger.warning(f"Timeout waiting for element: {by}={value}")
        return None
    except Exception as e:
        logger.error(f"Error finding element {by}={value}: {str(e)}")
        return None


def safe_click(driver: webdriver.Chrome, by: By, value: str, timeout: int = 10) -> bool:
    """
    Safely click an element with timeout.

    Args:
        driver: WebDriver instance
        by: Locator type (e.g., By.ID)
        value: Locator value
        timeout: Maximum wait time in seconds

    Returns:
        True if successful, False otherwise
    """
    element = safe_find_element(driver, by, value, timeout, "clickable")

    if element:
        try:
            element.click()
            return True
        except Exception as e:
            logger.error(f"Error clicking element {by}={value}: {str(e)}")

            # Try JavaScript click as fallback
            try:
                driver.execute_script("arguments[0].click();", element)
                logger.info(f"Clicked element {by}={value} using JavaScript")
                return True
            except Exception as js_e:
                logger.error(f"JavaScript click also failed: {str(js_e)}")
                return False

    return False


def wait_for_page_load(driver: webdriver.Chrome, timeout: int = 10) -> bool:
    """
    Wait for page to finish loading.

    Args:
        driver: WebDriver instance
        timeout: Maximum wait time in seconds

    Returns:
        True if page loaded, False otherwise
    """
    try:
        # Wait for the document to be in ready state
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        return True
    except TimeoutException:
        logger.warning(f"Timeout waiting for page to load: {driver.current_url}")
        return False
    except Exception as e:
        logger.error(f"Error waiting for page load: {str(e)}")
        return False


def fill_form(driver: webdriver.Chrome, form_data: Dict[str, str]) -> bool:
    """
    Fill a form with the provided data.

    Args:
        driver: WebDriver instance
        form_data: Dictionary mapping element IDs to values

    Returns:
        True if successful, False otherwise
    """
    success = True

    for element_id, value in form_data.items():
        try:
            element = safe_find_element(driver, By.ID, element_id)

            if not element:
                # Try by name if ID doesn't work
                element = safe_find_element(driver, By.NAME, element_id)

            if element:
                element.clear()
                element.send_keys(value)
                logger.debug(f"Filled field {element_id} with value")
            else:
                logger.warning(f"Could not find form field: {element_id}")
                success = False

        except Exception as e:
            logger.error(f"Error filling form field {element_id}: {str(e)}")
            success = False

    return success


def retry_operation(operation: Callable, max_retries: int = 3, retry_delay: int = 1) -> Any:
    """
    Retry an operation multiple times with delay.

    Args:
        operation: Callable to execute
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds

    Returns:
        Result of the operation if successful

    Raises:
        Exception: Last exception if all retries fail
    """
    last_exception = None

    for attempt in range(max_retries):
        try:
            return operation()
        except Exception as e:
            last_exception = e
            logger.warning(f"Retry {attempt+1}/{max_retries} failed: {str(e)}")

            if attempt < max_retries - 1:
                time.sleep(retry_delay)

    if last_exception:
        raise last_exception


def wait_for_element(
    driver: webdriver.Chrome, selector: str, timeout: int = 10
) -> Optional[webdriver.remote.webelement.WebElement]:
    """
    Wait for an element to be visible on the page.

    Args:
        driver: WebDriver instance
        selector: CSS selector for the element
        timeout: Maximum wait time in seconds

    Returns:
        WebElement if found, None otherwise
    """
    try:
        wait = WebDriverWait(driver, timeout)
        return wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
    except TimeoutException:
        logger.warning(f"Timeout waiting for element: {selector}")
        return None
    except Exception as e:
        logger.error(f"Error finding element: {selector}: {str(e)}")
        return None


def navigate_to_url(driver: webdriver.Chrome, url: str) -> bool:
    """
    Navigate to a URL and wait for the page to load.

    Args:
        driver: WebDriver instance
        url: URL to navigate to

    Returns:
        True if navigation successful, False otherwise
    """
    logger.info(f"Navigating to {url}")
    driver.get(url)
    return wait_for_page_load(driver)


def click_element(driver: webdriver.Chrome, by: By, value: str) -> bool:
    """
    Safely click an element on the page.

    Args:
        driver: WebDriver instance
        by: Locator type (e.g., By.ID)
        value: Locator value

    Returns:
        True if successful, False otherwise
    """
    element = safe_find_element(driver, by, value)
    if element:
        element.click()
        return True
    return False
