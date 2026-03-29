# FSSC Certificate Scraper (Scrapy Project)

## 📌 Overview

This project is a **Scrapy-based web scraper** designed to extract certificate data from the FSSC public register API. It handles pagination, JSON parsing, local caching of responses, and exports structured data into **JSON and Excel formats**.

The spider is optimized with error handling, safe parsing, and supports incremental crawling using offset-based pagination.

---

## 🚀 Features

* Scrapes certificate data from FSSC API (`admin-ajax.php`)
* Handles pagination using offset and limit
* Saves raw API responses locally for reuse
* Avoids duplicate requests using local file caching
* Safe JSON parsing with error handling
* Extracts nested fields (organization, categories, address)
* Cleans and formats data for Excel compatibility
* Exports data to:

  * JSON
  * Excel (.xlsx)
* Logs scraping progress and errors

---

## 🛠️ Tech Stack

* Python 3.x
* Scrapy
* Pandas
* JSON
* HTML decoding
* Regex
* OS / File handling

---



## ⚙️ How It Works

### 1. Start Request

* The spider starts from offset `0` and page `1`.

### 2. Request Handling

* Checks if response already exists locally (`Page_save/{page}.html`).
* If exists → loads from file.
* Otherwise → fetches from API.

### 3. API Endpoint

```
https://www.fssc.com/wp-admin/admin-ajax.php
?action=certificate_getCertificates&offset={offset}&limit=200
```

### 4. Parsing

* Parses JSON response safely.
* Extracts:

  * Organization name
  * Address
  * Product categories
  * Food chain categories
  * Certificate details
  * Status

### 5. Pagination

* Uses `total` count from API response.
* Continues requests until all records are scraped.

### 6. Data Storage

* Stores all records in memory (`self.all_data`).
* Saves output once scraping is complete.

---

## ▶️ Installation

1. Clone the repository:

```bash
git clone https://github.com/Niraj1321/FSSC-Certificate-Details.git


2. Create virtual environment:

```bash
python -m venv venv
```

3. Activate environment:

* Windows:

```bash
venv\Scripts\activate
```

* Linux/Mac:

```bash
source venv/bin/activate
```

4. Install dependencies:

```bash
pip install -r requirements.txt
```

---

## ▶️ Running the Spider

Run the spider using Scrapy CLI:

```bash
scrapy crawl links
```

Or run directly via Python entry point:

```bash
python links.py
```

---

## 📊 Output Files

After execution, the following files are generated:

* `Fssc_Certificate_YYYY-MM-DD.json`
* `Fssc_Certificate_YYYY-MM-DD.xlsx`

---

## 🧠 Key Implementation Details

### Safe Nested Parsing

Handles missing or null values using:

```python
(cert.get("categoryProductType") or {}).get("categories", [])
```

### Address Extraction

* Extracts nested address fields
* Removes unwanted keys like `coordinates`
* Joins values into a single string

### Product Types

* Extracted using category product type list
* Joined using `|` separator

### Category Details

* Stored as structured dictionary list:

```json
{
  "FSSC Category": "",
  "Category Description": ""
}
```

### Status Mapping

* `Valid` → Active
* Others → Inactive

---

## ⚠️ Error Handling

* JSON decode errors are logged and skipped
* Missing keys handled using `.get()` and fallback defaults
* File I/O errors are logged
* Pagination errors handled safely

---

## 🌐 About the FSSC Public Register Site

The FSSC Public Register is an official database provided by the Foundation FSSC that lists all organizations currently certified under the **FSSC 22000 and FSSC 24000 schemes**. Users can search and verify the certification status of organizations by name or COID (Certified Organization Identification Code) directly on the website. This register is updated regularly and provides detailed information about certificate validity, scope statements, and other certification details. ([fssc.com](https://www.fssc.com/public-register/?utm_source=chatgpt.com))

## 🚧 Challenges Faced (429 Too Many Requests)

While scraping this website, a **429 (Too Many Requests)** error was encountered due to rate limiting from the server.

### Cause:

* Excessive requests in a short time
* High concurrency
* Lack of sufficient delay between requests

### Impact:

* Temporary blocking of requests
* Incomplete or delayed data fetching

### Solutions Implemented:

* Enabled `DOWNLOAD_DELAY` to slow down requests
* Enabled `AUTOTHROTTLE_ENABLED` to dynamically adjust request rate
* Reduced `CONCURRENT_REQUESTS` to avoid overload
* Used local caching to minimize repeated API calls

### Additional Possible Improvements:

* Use proxy rotation
* Implement IP rotation
* Add retry with exponential backoff
* Randomize user agents and headers
* Introduce request fingerprinting control

---

## 🔐 Performance Optimizations

* Local caching of API responses
* Reduced duplicate network calls
* Controlled concurrency via Scrapy settings
* Download delay and auto-throttling enabled

---

## ⚙️ Custom Settings

```python
DOWNLOAD_DELAY = 0.5
AUTOTHROTTLE_ENABLED = True
RETRY_TIMES = 3
CONCURRENT_REQUESTS = 6
LOG_LEVEL = "INFO"
```

---

## 📌 Example Output Fields

* Url
* Organization Name
* Certification Scheme
* Certificate Issue Date
* Certificate Valid Until
* COID
* Address
* Product Types
* Scope Statement
* Certificate Details
* Status

---

## 📈 Future Improvements

* Add proxy rotation
* Implement retry/backoff strategies
* Store data directly into MySQL/MongoDB
* Add deduplication layer
* Parallel crawling with distributed setup

---

## 👤 Author

Niraj Chauhan

---

## 📜 License

For educational and professional use. Modify as needed.

---

## ✅ Notes

* Ensure stable internet connection for API requests
* Respect website usage policies
* Cached files help reduce repeated API hits
