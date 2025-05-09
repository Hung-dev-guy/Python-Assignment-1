import time
import csv
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

def scrape_all_players_to_csv(base_url="https://www.footballtransfers.com/en/players/uk-premier-league", filename=r"C:\Users\Hungdever\Desktop\My_study\EPL\data\ETV_list.csv"):
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--allow-running-insecure-content')
    options.add_argument('--disable-gpu')
    options.add_argument('log-level=3')

    driver = None
    player_data = []
    page_number = 1

    try:
        print("Initializing undetected_chromedriver...")
        driver = uc.Chrome(options=options, use_subprocess=False)
        print("Undetected_chromedriver driver initialized.")

        while True:
            if page_number == 1:
                current_url = base_url
            else:
                current_url = f"{base_url}/{page_number}"

            print(f"\n--- Processing page {page_number}: {current_url} ---")
            try:
                driver.get(current_url)
            except Exception as e:
                print(f"  Error accessing URL for page {page_number}: {e}. Stop!.")
                break 

            try:
                player_table_body = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.ID, "player-table-body"))
                )
                player_rows = player_table_body.find_elements(By.TAG_NAME, "tr")
                print(f"  Page {page_number}: Found {len(player_rows)} player rows.")

                if not player_rows:
                    print(f"  Page {page_number}: No rows (tr) found in tbody.")
                    break

                rows_processed_on_page = 0
                for i, row in enumerate(player_rows):
                    try:
                        name_element = row.find_element(By.CSS_SELECTOR, "td.td-player span.d-none")
                        player_name = name_element.get_attribute('textContent').strip()
                        etv_element = row.find_element(By.XPATH, "./td[last()]")
                        player_etv = etv_element.get_attribute('textContent').strip()
                        if player_name:
                            player_data.append([player_name, player_etv])
                            rows_processed_on_page += 1
                    except NoSuchElementException:
                        continue
                    except Exception as e:
                        print(f"    Error processing row {i+1} on page {page_number}: {e}")

                print(f"  Page {page_number}: Processed and added {rows_processed_on_page} players.")

            except TimeoutException:
                print(f"  Page {page_number}: Could not find tbody#player-table-body, may have reached the last page")
                break 

            page_number += 1
            sleep_duration = random.uniform(4.0, 8.0)
            time.sleep(sleep_duration)

        print("\n--- Start to write data to CSV file ---")
        if player_data:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['Player Name', 'ETV']) # Write header
                    writer.writerows(player_data) # Write all collected data
                print(f"\nSuccessfully wrote a total of {len(player_data)} players from {page_number-1} pages to file '{filename}'")
                return player_data
            except IOError as e:
                print(f"\nError: Could not write to CSV file '{filename}'. Error: {e}")
                return None
        else:
            print("\nNo player data was collected to write to the file.")
            return None

    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        if driver:
            print("Close browser")
            driver.quit()

if __name__ == "__main__":
    print("--- Start scraping process ---")
    scraped_data_list = scrape_all_players_to_csv(base_url="https://www.footballtransfers.com/en/players/uk-premier-league") 

    if scraped_data_list is not None:
        print(f"\nCompleted! A total of {len(scraped_data_list)} records were processed.")
