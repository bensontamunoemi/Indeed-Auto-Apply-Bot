from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException
import time

USERNAME = ""
PASSWORD = ""
JOB_SEARCH = "Project Management"
LOCATION_SEARCH = "London, ON"


class IndeedAutoApplyBot():

    def __init__(self) -> None:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("detach", True)
        self.browser = webdriver.Chrome(chrome_options)
        url = "https://ca.indeed.com/?from=gnav-homepage&from=gnav-util-homepage"
        self.browser.get(url)
        time.sleep(2)

    def login(self) -> None:
        # Click login link
        login_link = self.browser.find_element(By.LINK_TEXT, value="Sign in")
        login_link.click()
        time.sleep(2)

        # Fill the email field and click next
        email_input = self.browser.find_element(By.NAME, value="__email")
        email_input.send_keys(USERNAME)
        time.sleep(2)

        continue_btn = self.browser.find_element(By.XPATH, value='//*[@id="emailform"]/button')
        continue_btn.click()
        time.sleep(2)

        # Option to sign in with login code if available
        with_code_anchor_tag = self.browser.find_element(By.LINK_TEXT, value="Sign in with login code instead")
        if with_code_anchor_tag:
            with_code_anchor_tag.click()
        time.sleep(2)

        # Wait for 2 minutes for manual actions like CAPTCHA
        print("Please complete any manual actions required (e.g., CAPTCHA). Waiting for 2 minutes...")
        time.sleep(120)  # 120 seconds = 2 minutes

    def find_job(self) -> None:
        """Search for a job."""
        query_input = self.browser.find_element(By.NAME, value="q")
        # location_input = self.browser.find_element(By.NAME, value="l")
        # location_input.send_keys(LOCATION_SEARCH)
        query_input.send_keys(JOB_SEARCH)
        find_btn = self.browser.find_element(By.XPATH, value='//*[@id="jobsearch"]/div/div[2]/button')
        find_btn.click()

    def browse_jobs(self) -> None:
        """Browse job listings and handle any modals or overlays."""
        while True:  # Continue this process until no more pagination is available
            # Wait for job listings to load.
            WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "li.css-5lfssm"))
            )
            job_listings = self.browser.find_elements(By.CSS_SELECTOR, "li.css-5lfssm")

            for job in job_listings:
                try:
                    # Check if the listing has "Easily apply".
                    easily_apply_label = job.find_element(By.CSS_SELECTOR,
                                                          "span.ialbl.iaTextBlack.css-1p29peq.eu4oa1w0")
                    if easily_apply_label and "Easily apply" in easily_apply_label.text:
                        # Scroll the job into view and click on it to display the description.
                        self.browser.execute_script("arguments[0].scrollIntoView();", job)
                        actual_job = job.find_element(By.CSS_SELECTOR, ".resultContent h2 a")
                        if actual_job:
                            actual_job.click()
                            # Apply for job.
                            time.sleep(5)
                            # self.apply_job()
                    else:
                        print("Job does not have 'Easily apply', skipped.")
                except NoSuchElementException:
                    # If "Easily apply" label or the clickable link is not found, skip this job.
                    print("Skipped this job due to missing 'Easily apply' label or link.")

            # Attempt to find and click the "Next" pagination button
            try:
                self.wait_and_click(By.CSS_SELECTOR, 'a[data-testid="pagination-page-next"]')

                WebDriverWait(self.browser, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "li.css-5lfssm"))
                )
                time.sleep(5)
                self.close_modal()

            except (NoSuchElementException, TimeoutException):
                print("No more pages or unable to load the next page.")
                break  # Break out of the loop if no next page is found or page didn't load

    def wait_and_click(self, by, value) -> None:
        """Wait for an element to be clickable and then click it."""
        try:
            element = WebDriverWait(self.browser, 10).until(
                EC.element_to_be_clickable((by, value))
            )
            element.click()
        except ElementClickInterceptedException:
            self.browser.execute_script("arguments[0].click();", self.browser.find_element(by, value))

    def close_modal(self) -> None:
        """Attempt to close a modal if it appears."""
        try:
            # Wait for the close button to be clickable
            WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.ID, 'SA_PRELOAD_ASSETS_IFRAME_ID'))
            )

            close_button = self.browser.find_element(By.XPATH,
                                                     value='//*[@id="mosaic-desktopserpjapopup"]/div[1]/button')
            close_button.click()

            print("Modal closed successfully.")
            time.sleep(2)
        except (TimeoutException, NoSuchElementException):
            print("No modal found or not clickable.")

    def apply_job(self) -> None:
        """Apply for the job online"""
        try:
            # Wait for the apply button to be clickable
            WebDriverWait(self.browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//*[@id='indeed-apply-widget']/div"))
            ).click()

            # Code to switch to the new tab, apply for the job, and then close the tab

            # ID of the original window
            original_window = self.browser.current_window_handle

            # Wait for the new tab to open
            WebDriverWait(self.browser, 10).until(EC.number_of_windows_to_be(2))

            # Switch to the new window (the latest opened tab)
            for window_handle in self.browser.window_handles:
                if window_handle != original_window:
                    self.browser.switch_to.window(window_handle)
                    break

            # Complete the application.
            time.sleep(5)

            # Close the current tab
            self.browser.close()

            # Switch back to the original window
            self.browser.switch_to.window(original_window)

            # Wait a bit for the page to stabilize after returning
            time.sleep(2)

        except TimeoutException:
            # Handle the case where the apply button is not found
            print("Apply button not found for this job, skipping...")
            # Optionally, you could add more logic here to handle different scenarios


bot = IndeedAutoApplyBot()
# bot.login()
bot.find_job()
bot.browse_jobs()
