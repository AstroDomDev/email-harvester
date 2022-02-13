import datetime
import re
import atexit
from difflib import SequenceMatcher
from random import shuffle
from types import NoneType
from urllib.parse import urlsplit

import requests
import requests.exceptions
from bs4 import BeautifulSoup

### Constant Variables ###

valid_endings = (
    ".com",
    ".net",
    ".org",
    ".co",
    ".co.uk",
)

prohibitions = (
    "example",
    "github",
    "sample",
    "google",
    "twitter",
    "facebook",
    "support",
    "nowhere",
    "@company.com",
)

requirements = (
    "",
)

### Helper Functions ###
def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()


def scrape_emails(urls, limiter=500, logging=False, filter=True):
    if __name__ == "__main__":
        print("At any point press ctrl+c to end the scraping loop.")

    ### Local Variable Initialization ###
    processed_urls = set()
    emails = set()
    index = 0

    if logging == True:
        start = datetime.datetime.now()

    ### Scraping Loop ###
    try:
        while len(urls) and index < limiter:

            ### Get random assortment of urls, length cut to 2500 for efficiency ###
            if len(urls) > 2500: shuffle(urls); urls = urls[:1250]

            ### Cycle through urls ###
            url = urls[0]
            urls.pop(0)

            ### Logging ###
            index += 1
            if logging == True:
                print(datetime.datetime.now().strftime("%m-%d, %H:%M:%S:"), f"{index} | {len(urls)} | {url}")

            ### Parse url ###
            parts = urlsplit(url)
            base_url = "{0.scheme}://{0.netloc}".format(parts)
            path = url[:url.rfind('/')+1] if '/' in parts.path else url
            processed_urls.add(url)

            ### Fetch page from url ###
            try: response = requests.get(url, timeout=5)
            # Ignore Errors
            except: continue

            ### Find Emails
            new_emails = set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", response.text, re.I))
            
            ### Parse webpage ###
            soup = BeautifulSoup(response.text, features="html.parser")

            ### Find and Process all anchors/links in document ###
            new_links = 0
            for anchor in soup.find_all("a"):

                ## Extract url from anchor ##
                link = anchor.attrs["href"] if "href" in anchor.attrs else ''

                ## Process links ##
                if similarity(link, url) >= 0.83:
                    continue
                elif "trending" in link:
                    continue
                elif link.startswith('//'):
                    link = "http:" + link
                elif link.startswith('/'):
                    link = base_url + link
                elif not link.startswith('http'):
                    link = path + link
                
                ## Add url to queue if valid ##
                if not link in urls and not link in processed_urls:
                    urls.append(link)
                    new_links += 1

                ## Break loop if more than 50 urls added ##
                if new_links >= 50: break
            
            ### Filter Emails ###
            if filter == True:
                new_emails = set([i for i in new_emails if i.endswith(valid_endings) and not any(rule in i for rule in prohibitions) and any(rule in i for rule in requirements) and i.count('.') <=2])
            emails.update(new_emails)
    except KeyboardInterrupt: print("Loop interrupted... returning data.")


    ### Logging ###
    elapsed = datetime.datetime.now()-start
    print(f"{len(emails)} emails returned in {elapsed}")

    ### Return all emails ###
    return emails if emails != set() else None

if __name__ == "__main__":
    emails = (scrape_emails(["https://twitter.com/"], 5000, logging=True))
    if emails:
        open('emails.txt', 'w').write("\n".join(emails))


