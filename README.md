This Python-based web scraper is designed to extract company contact information (website, email, and phone number) from various online sources. It uses a combination of techniques, including search engine lookups, website crawling, and intelligent contact page discovery, to maximize the accuracy and completeness of the extracted data.

## Features

* **Search Engine Lookups:** Uses multiple search engines (Google, Bing, DuckDuckGo, etc.) to identify the official website of a company.
* **Contact Page Discovery:**  Automatically finds contact pages by analyzing website structure, sitemaps, and common contact page patterns.
* **Contact Extraction:** Extracts contact information from visible website content, metadata, microdata, and JavaScript.
* **Multi-threading:** Processes multiple companies concurrently for faster scraping.
* **Error Handling:** Includes retry mechanisms and detailed logging to ensure smooth operation.
* **Customizable Configuration:** Allows you to adjust settings like search engines, contact paths, and user agents.

## Requirements

* Python 3.7+
* pandas
* requests
* beautifulsoup4
* selenium
* fake_useragent
* tldextract
* openpyxl

## Usage

1. **Prepare Input Data:** Create an Excel file named `data.xlsx` with a column named "Company Name" containing the list of companies you want to scrape.
2. **Run the Scraper:** Execute the `main.py` script.
3. **Output:** The extracted contact information will be saved in an Excel file named `mined_company_data.xlsx`.

