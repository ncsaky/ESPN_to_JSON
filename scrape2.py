import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def fetch_page_with_selenium(url):
    """
    Fetch play-by-play data for an NBA game from ESPN using Selenium.

    Args:
        url (str): The URL of the ESPN play-by-play page.

    Returns:
        list: A list of strings, each containing a play-by-play entry.
    """
    # Set up Selenium WebDriver with Chrome in headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run browser in headless mode
    service = ChromeService(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(url)

        # Wait for the play-by-play table to load for the first quarter
        table_selector = (
            "#fittPageContainer > div.pageContent > div > div > div:nth-child(6) > "
            "div > div.PageLayout__Main > section.Card.Card--PlayByPlay > div > div > "
            "div > div > div > div.Table__Scroller > table > tbody"
        )
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, table_selector))
        )

        play_by_play_data = []

        # Extract data for the first quarter
        first_quarter_data = extract_espn_data(driver, table_selector)
        play_by_play_data.extend(first_quarter_data)

        # Locate tabs for additional quarters
        quarter_tabs = driver.find_elements(By.CSS_SELECTOR, "nav ul li button")
        quarter_tabs = [tab for tab in quarter_tabs if tab.text in ['1st', '2nd', '3rd', '4th']]

        # Loop through the quarter tabs, starting from the 2nd quarter
        for tab in quarter_tabs[1:]:
            tab.click()
            time.sleep(2)  # Allow time for the quarter's table to load

            # Extract data for the current quarter
            quarter_data = extract_espn_data(driver, table_selector)
            play_by_play_data.extend(quarter_data)

        driver.quit()
        return play_by_play_data

    except Exception as e:
        driver.quit()
        print(f"An error occurred while fetching play-by-play data: {e}")
        return None


def extract_espn_data(driver, table_selector):
    """
    Extract play-by-play data from the specified table using Selenium.

    Args:
        driver (WebDriver): Selenium WebDriver instance.
        table_selector (str): CSS selector for the table containing play-by-play data.

    Returns:
        list: A list of strings, each containing a play-by-play entry.
    """
    play_by_play = []

    try:
        # Locate table rows directly using Selenium
        rows = driver.find_elements(By.CSS_SELECTOR, f"{table_selector} > tr")
        for row in rows:
            # Extract time and play description
            time_cell = row.find_element(By.CSS_SELECTOR, "td.playByPlay__time").text
            text_cell = row.find_element(By.CSS_SELECTOR, "td.playByPlay__text").text
            play_by_play.append(f"{time_cell} - {text_cell}")
    except Exception as e:
        print(f"An error occurred while extracting data from the table: {e}")

    return play_by_play


def save_to_file(data, filename):
    """
    Save play-by-play data to a text file.

    Args:
        data (list): List of strings containing play-by-play entries.
        filename (str): Path to the output file.
    """
    try:
        with open(filename, 'w') as file:
            for entry in data:
                file.write(f"{entry}\n")
        print(f"Play-by-play data saved to {filename}")
    except Exception as e:
        print(f"An error occurred while saving data to file: {e}")


def main():
    """
    Main function to fetch and save NBA play-by-play data from ESPN.
    """
    espn_url = "https://www.espn.com/nba/playbyplay/_/gameId/401656363"  # Example game URL
    output_file = "play_by_play.txt"

    print("Fetching play-by-play data...")
    play_by_play = fetch_page_with_selenium(espn_url)

    if play_by_play:
        print(f"Successfully fetched {len(play_by_play)} entries.")
        save_to_file(play_by_play, output_file)
    else:
        print("Failed to fetch play-by-play data.")


if __name__ == "__main__":
    main()
