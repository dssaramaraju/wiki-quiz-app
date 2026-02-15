import requests
from bs4 import BeautifulSoup


def scrape_wikipedia(url: str):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            raise Exception("Invalid URL or page not found")

        soup = BeautifulSoup(response.text, "html.parser")

        # Title
        title = soup.find("h1").text.strip()

        # Paragraphs
        paragraphs = soup.find_all("p")

        summary = ""
        for p in paragraphs:
            if p.text.strip():
                summary = p.text.strip()
                break

        content = " ".join([p.text.strip() for p in paragraphs if p.text.strip()])

        return {
            "title": title,
            "summary": summary,
            "content": content
        }

    except Exception as e:
        raise Exception(f"Error scraping Wikipedia: {str(e)}")
