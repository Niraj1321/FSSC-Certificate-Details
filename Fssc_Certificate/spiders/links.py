import json
import os
import html
import re
from urllib.parse import urlencode
import scrapy
import pandas as pd
from datetime import datetime

from scrapy import Spider
from twisted.internet.defer import Deferred


class LinksSpider(scrapy.Spider):
    name = "links"

    custom_settings = {
        "DOWNLOAD_DELAY": 0.5,
        "AUTOTHROTTLE_ENABLED": True,
        "RETRY_TIMES": 3,
        "CONCURRENT_REQUESTS": 6,
        "LOG_LEVEL": "INFO"
    }

    headers = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "user-agent": "Mozilla/5.0"
    }

    folder_path = "Page_save"

    def __init__(self):
        os.makedirs(self.folder_path, exist_ok=True)
        self.all_data = []

    # -------------------- START --------------------
    def start_requests(self):
        yield self.make_request(offset=0, page=1, p_cnt=0)

    # -------------------- REQUEST BUILDER --------------------
    def make_request(self, offset, page, p_cnt):
        try:
            relative_path = os.path.join(self.folder_path, f"{page}.html")
            absolute_path = os.path.abspath(relative_path)

            #  Use local file if exists
            if os.path.exists(absolute_path):
                return scrapy.Request(
                    url=f"file:///{absolute_path}",
                    callback=self.parse,
                    meta={"page": page, "p_cnt": p_cnt},
                    dont_filter=True
                )

            #  Otherwise hit API
            base_url = "https://www.fssc.com/wp-admin/admin-ajax.php"
            params = {
                "action": "certificate_getCertificates",
                "offset": str(offset),
                "limit": "200",
            }

            url = f"{base_url}?{urlencode(params)}"

            return scrapy.Request(
                url=url,
                headers=self.headers,
                callback=self.parse,
                meta={"page": page, "p_cnt": p_cnt},
                dont_filter=True
            )

        except Exception as e:
            self.logger.error(f"Request creation failed: {e}", exc_info=True)

    # -------------------- PARSE --------------------
    def parse(self, response):
        page = response.meta.get("page", 1)
        p_cnt = response.meta.get("p_cnt", 0)

        self.logger.info(f"Processing Page: {page}")

        file_path = os.path.join(self.folder_path, f"{page}.html")

        #  Save API response
        try:
            if response.url.startswith("http") and not os.path.exists(file_path):
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(response.text)
        except IOError as e:
            self.logger.error(f"File write failed: {file_path} | {e}")

        #  Parse JSON safely
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decode failed on page {page}: {e}")
            return

        total = int(data.get("total", 0))

        # -------------------- DATA LOOP --------------------
        for cert in data.get("certificates", []):
            try:
                #  Address
                address_data = (cert.get("organisation") or {}).get("address") or {}
                address_data.pop("coordinates", None)

                full_address = " ".join(v for v in address_data.values() if v)

                #Product Type (FIXED NoneType issue)
                product_type = " | ".join(
                    [
                        x.get("name", "")
                        for x in (cert.get("categoryProductType") or {}).get("categories", [])
                    ]
                )

                #Category Details (FIXED)
                category_details = [
                    {
                        "FSSC Category": x.get("label"),
                        "Category Description": x.get("shortName")
                    }
                    for x in (cert.get("categoryFoodChain") or {}).get("categories", [])
                ]

                # Status
                status = "Active" if cert.get("status") == "Valid" else "Inactive"

                #  Append Data
                self.all_data.append({
                    "Url": f"https://www.fssc.com/public-register/{cert.get('coid')}",
                    "Organization Name": cert.get("title", "").replace('"', ''),
                    "Certification Scheme": cert.get("scheme"),
                    "Certificate Issue Date": cert.get("issued"),
                    "Certificate Valid Until": cert.get("validUntil"),
                    "COID": cert.get("coid"),
                    "Address": full_address,
                    "Product Types": product_type,
                    "Scope Statement": html.unescape(cert.get("scopeStatement", "")),
                    "Certificate Details": category_details,
                    "Status": status
                })

                p_cnt += 1

            except KeyError as e:
                self.logger.warning(f"Missing key: {e}")
                continue

            except Exception as e:
                self.logger.error(f"Error parsing record: {e}", exc_info=True)
                continue

        # -------------------- PAGINATION --------------------
        try:
            if p_cnt < total:
                yield self.make_request(offset=p_cnt, page=page + 1, p_cnt=p_cnt)
            else:
                self.logger.info(f"Scraping completed. Total records: {p_cnt}")
                self.save_data()

        except Exception as e:
            self.logger.error(f"Pagination error: {e}", exc_info=True)

    # -------------------- SAVE DATA --------------------
    def save_data(self):
        today = datetime.today().strftime("%Y-%m-%d")
        base_name = f"Fssc_Certificate_{today}"

        # Save JSON
        try:
            with open(f"{base_name}.json", "w", encoding="utf-8") as f:
                json.dump(self.all_data, f, indent=2)
        except Exception as e:
            self.logger.error(f"JSON save failed: {e}")

        # Save Excel
        try:
            df = pd.DataFrame(self.all_data)
            df = df.applymap(self.clean_excel_value)
            df.to_excel(f"{base_name}.xlsx", index=False)
        except Exception as e:
            self.logger.error(f"Excel save failed: {e}")

        self.logger.info("Data saved successfully")

    # -------------------- CLEAN DATA --------------------
    def clean_excel_value(self, value):
        if isinstance(value, str):
            return re.sub(r'[\x00-\x1F]', '', value)
        return value

    def close(self,spider: Spider, reason: str):
        self.save_data()



# -------------------- RUN --------------------
if __name__ == "__main__":
    from scrapy.cmdline import execute
    execute("scrapy crawl links".split())