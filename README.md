# 🦋 BuiltmindScraper

**BuiltmindScraper** is a lightweight 🕸️ web scraper and crawler that extracts useful data from websites and stores it in a local **SQLite** database.

---

## ✨ What It Does

🔹 Crawls a website starting from a given URL  
🔹 Extracts content from tags like `h1`–`h6`, `p`, `div`, `span`  
🔹 Finds and stores all links and image sources  
🔹 Handles errors gracefully and logs problematic URLs  
🔹 Uses raw `SQL` queries — easy to understand and modify  
🔹 Adds a delay between requests to be kind to servers 😇

---

## 🧠 Built For

📚 **Learning**: A clear example for beginners in Python, SQL, and web scraping  
🛠️ **Experimenting**: Easily adaptable to other domains  
🔍 **Exploring**: Understand the structure and content of any website

---

## 🗃️ Database Structure

```sql
links(id, url, content, description, location)
images(id, url, location)
extracted_text(id, title, content, location, tag)
problems(id, url)

---

## 🏌️‍♂️Tech Stack
🐍 Python

🍜 BeautifulSoup (for parsing)

🪶 Requests (for fetching)

🛢️ SQLite (for storage)
