import requests
import sqlite3
import time  # I don't want to overwhelm the website, so let's timeout a bit
from bs4 import BeautifulSoup

# I am going with plain SQL queries not ORM to show easier logic of this code

# Let's make simple db in sqlite to scrape builtminds data
db_name = "web_data_builtmind.db"
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

# links
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS links(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT UNIQUE,
    content TEXT,
    description TEXT,
    location TEXT NOT NULL
    );
"""
)

# images
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS images(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT UNIQUE,
    location TEXT NOT NULL
    );
"""
)

# extracted_text
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS extracted_text(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT ,
    content TEXT ,
    location TEXT NOT NULL,
    tag TEXT 
    );
"""
)

# Problematic urls
cursor.execute(f"""
CREATE TABLE IF NOT EXISTS problems(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT            
               );
""")

conn.commit()

url = "https://www.builtmind.com/sk/sk-sk//"
tags = [
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "span",
    "div",
]  # Let's find content for each tag I like

def fetch_page_content(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses
        response.encoding = "utf-8"
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching page content: {e}")
        return None

# Find links and corresponding visisble text
def find_links(html, location):
    soup = BeautifulSoup(html, "html.parser")
    for bowl in soup.find_all("a"):
        # print(f"{bowl.get("href")}\n{bowl.text}\n")
        filled_bowl = bowl.get("href")
        if filled_bowl:
            try:
                # Need to use parametrization - sk in the end on my link is messink up my query
                conn.execute(
                    "INSERT INTO links (url, content, location) VALUES (?, ?, ?);",
                    (filled_bowl, bowl.text, location),
                )
            except sqlite3.IntegrityError:
                print("Not again, we are trying to ignore UNIQUEness!")
    conn.commit()

# Extract content of webpage - <h> <p>
def find_text_info(html, location):
    soup = BeautifulSoup(html, "html.parser")

    for tag in tags:
        temp = soup.find_all(tag)
        # Try if there are corresponding
        if temp:
            for elmnt in temp:
                temp_dict = {"title": None, "content": None}
                elmnt_text = elmnt.get_text(strip=True)
                if (
                    elmnt_text and temp_dict["title"] != elmnt_text
                ):  # Check if there is not repeating
                    temp_dict["title"] = elmnt_text

                if tag.startswith("h"):
                    lets_p = elmnt.find_next_sibling("p")
                    if lets_p:
                        lets_p_text = lets_p.get_text(strip=True)
                        if lets_p and temp_dict["content"] != lets_p_text:
                            temp_dict["content"] = lets_p_text

                # Save to DB -> location is URL of current page we are scraping
                if temp_dict["content"] or temp_dict["title"]:
                    try:
                        cursor.execute(
                            f"""
                        INSERT INTO extracted_text (title, content, location, tag)
                        VALUES ("{temp_dict['title']}", "{temp_dict['content']}", "{location}", "{tag}")
                        """
                        )
                    except sqlite3.IntegrityError:
                        print("Not writing this one in :-)")
    conn.commit()

# find images
def find_img(html, location):
    soup = BeautifulSoup(html, "html.parser")
    for fork in soup.find_all("img"):
        image_link = fork.get("src")
        if image_link:
            try:
                conn.execute(
                    f"""
                INSERT INTO images (url, location)
                VALUES ("{image_link}","{location}")
                """
                )
            except sqlite3.IntegrityError:
                print("Hups, some error on the way no worry, I just skip this one :)")
    conn.commit()

# Let's scrape the website :-)
#
# 1: Load data from index page (plus save to DB) and leter crawl over the whole website
web_cont = fetch_page_content(url)
# extracted_text
find_text_info(web_cont, url)
# pictures
find_img(web_cont, url)
# links
find_links(web_cont, url)

gathered_links = conn.execute(
    f"""
    SELECT url
    FROM links
    WHERE url LIKE '%builtmind.com%';
"""
)

links_to_crawl = []
for link in gathered_links:
    links_to_crawl.append(link[0])

# Let's spread a bit
for i, page in enumerate(links_to_crawl):
    print(f"This is page number: {i}\n{page}")
    try:
        web_cont = fetch_page_content(page)
        # extracted_text
        find_text_info(web_cont, page)
        # pictures
        find_img(web_cont, page)
        # links
        find_links(web_cont, page)
    except TypeError:
        print("Problem with url")
        try:
            conn.execute("INSERT INTO problems (url) VALUES (?);", (page))
            conn.commit()
        except sqlite3.Error as e:
            print(f"There is really some problem, can't scrape this page {page}: error {e}")
    
    time.sleep(3)

conn.close()
