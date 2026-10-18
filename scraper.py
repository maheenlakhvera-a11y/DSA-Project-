import re
import time
import threading
import requests
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from bs4 import BeautifulSoup
from PyQt6.QtCore import QThread, pyqtSignal

TARGET = 15000
CATEGORY = "cs.AI"
START_YEAR = 2019
END_YEAR = 2024
SHOW = 2000
DELAY = 3
MAILTO = "maheenmohsin02@gmail.com"
BASE_URL = "https://arxiv.org/list"


def build_headers():
    return {"User-Agent": f"UET-Lahore-DSA-Student-Project (mailto:{MAILTO})"}


def fetch_month(category, year, month, skip=0):
    url = f"{BASE_URL}/{category}/{year}-{month:02d}"
    params = {"skip": skip, "show": SHOW}
    r = requests.get(url, params=params, headers=build_headers(), timeout=60)
    r.raise_for_status()
    return r.text


def fetch_url(url):
    # NAYA LOGIC: URL mein automatically 'show=2000' add karo taake 50 ke bajaye poora data aaye
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)
    
    if "arxiv.org" in parsed.netloc:
        if "show" not in query_params:
            query_params["show"] = ["2000"]
        parsed = parsed._replace(query=urlencode(query_params, doseq=True))
        url = urlunparse(parsed)

    r = requests.get(url, headers=build_headers(), timeout=60)
    r.raise_for_status()
    return r.text


def parse_custom_url(url):
    match = re.search(r"/list/(.+)", url)
    if not match:
        return None, None, None, None

    parts = match.group(1).strip("/").split("/")
    if not parts:
        return None, None, None, None

    category = parts[0]
    start_year = None
    end_year = None
    month = None

    if len(parts) == 1:
        pass
    elif len(parts) == 2:
        date_part = parts[1].split("?")[0] # Remove query params if any
        if "-" in date_part:
            sub_parts = date_part.split("-")
            if len(sub_parts) == 2:
                if len(sub_parts[1]) == 2:
                    start_year = int(sub_parts[0])
                    end_year = int(sub_parts[0])
                    month = int(sub_parts[1])
                else:
                    start_year = int(sub_parts[0])
                    end_year = int(sub_parts[1])
        else:
            start_year = int(date_part)
            end_year = int(date_part)

    return category, start_year, end_year, month


def _div_text(div, prefix):
    if div is None:
        return ""
    text = " ".join(div.get_text(" ", strip=True).split())
    if text.lower().startswith(prefix.lower()):
        text = text[len(prefix):].strip()
    return text


def parse_listing(html, year=0, month=0, category="N/A"):
    soup = BeautifulSoup(html, "lxml")
    container = soup.find("dl", id="articles") or soup
    dts = container.find_all("dt")
    dds = container.find_all("dd")
    n = min(len(dts), len(dds))
    dts, dds = dts[:n], dds[:n]

    rows = []
    for dt, dd in zip(dts, dds):
        link = dt.find("a", title="Abstract")
        if link:
            arxiv_id = link.get_text(strip=True).replace("arXiv:", "").strip()
        else:
            m = re.search(r"arXiv:(\S+)", dt.get_text(" ", strip=True))
            arxiv_id = m.group(1) if m else ""
        if not arxiv_id:
            continue

        title = _div_text(dd.find("div", class_="list-title"), "Title:")
        if not title:
            continue

        authors_div = dd.find("div", class_="list-authors")
        authors = []
        if authors_div:
            authors = [a.get_text(strip=True) for a in authors_div.find_all("a")]
        first_author = authors[0] if authors else "N/A"

        subjects_text = _div_text(dd.find("div", class_="list-subjects"), "Subjects:")
        subjects = [s.strip() for s in subjects_text.split(";") if s.strip()]
        primary_subject = subjects[0] if subjects else "N/A"

        comments = _div_text(dd.find("div", class_="list-comments"), "Comments:")
        pages_m = re.search(r"(\d+)\s*pages", comments, re.I)
        figs_m = re.search(r"(\d+)\s*figures?", comments, re.I)

        journal_ref = _div_text(dd.find("div", class_="list-journal-ref"), "Journal-ref:")

        rows.append({
            "arxiv_id": arxiv_id, "title": title, "first_author": first_author,
            "author_count": len(authors), "primary_subject": primary_subject,
            "subject_count": len(subjects), "pages": int(pages_m.group(1)) if pages_m else 0,
            "figures": int(figs_m.group(1)) if figs_m else 0,
            "comments": comments if comments else "N/A", "journal_ref": journal_ref if journal_ref else "N/A",
            "year": year, "month": month, "title_words": len(title.split()),
            "category": category,
        })
    return rows


class ScraperThread(QThread):
    progress = pyqtSignal(int)
    batch_ready = pyqtSignal(list)
    status = pyqtSignal(str)
    finished_scraping = pyqtSignal(list)
    incomplete_data = pyqtSignal(int) 
    error_occurred = pyqtSignal(str)

    def __init__(self, custom_url=None):
        super().__init__()
        self.data = []
        self.seen = set()
        self.running = True
        self.custom_url = custom_url
        self._pause_event = threading.Event()
        self._pause_event.set()

    def pause(self):
        self._pause_event.clear()
        self.status.emit("Paused")

    def resume(self):
        self._pause_event.set()
        self.status.emit("Scraping...")

    def stop(self):
        self.running = False
        self._pause_event.set()

    def _fetch_with_retry(self, cat, year, month, skip):
        for attempt in range(1, 4):
            self._pause_event.wait()
            if not self.running: return None
            self.status.emit(f"Scraping {year}-{month:02d} ({cat})...")
            try:
                return fetch_month(cat, year, month, skip)
            except Exception as e:
                self.status.emit(f"Error: {e} (retry {attempt}/3)")
                time.sleep(5 * attempt)
        return None

    def run(self):
        try:
            # ---------- BONUS: custom URL mode ----------
            if self.custom_url:
                self.status.emit(f"Parsing URL: {self.custom_url}")
                cat, sy, ey, month = parse_custom_url(self.custom_url)

                if cat is None:
                    self.status.emit("Invalid URL format.")
                    self.error_occurred.emit("Invalid URL format. Please provide a valid arXiv URL.")
                    self.finished_scraping.emit([])
                    return

                if sy and ey and sy == ey and month:
                    self.status.emit(f"Fetching single month: {sy}-{month:02d} ({cat})")
                    html = fetch_url(self.custom_url)
                    rows = parse_listing(html, sy, month, cat)
                    for row in rows:
                        if row["arxiv_id"] in self.seen: continue
                        self.seen.add(row["arxiv_id"])
                        self.data.append(row)
                        self.progress.emit(len(self.data))
                    
                    if len(self.data) < TARGET:
                        self.incomplete_data.emit(len(self.data))
                    else:
                        self.finished_scraping.emit(list(self.data))
                    return

                if sy and ey:
                    months = [(y, m) for y in range(sy, ey + 1) for m in range(1, 13)]
                    self.status.emit(f"Fetching range: {sy} to {ey} ({cat})")
                else:
                    months = [(y, m) for y in range(START_YEAR, END_YEAR + 1) for m in range(1, 13)]
                    self.status.emit(f"Fetching default range ({cat})")

                for (year, m) in months:
                    if not self.running or len(self.data) >= TARGET: break
                    html = self._fetch_with_retry(cat, year, m, 0)
                    if html:
                        rows = parse_listing(html, year, m, cat)
                        for row in rows:
                            if row["arxiv_id"] in self.seen: continue
                            self.seen.add(row["arxiv_id"])
                            self.data.append(row)
                            if len(self.data) >= TARGET: break
                    self.progress.emit(len(self.data))
                    self.batch_ready.emit(list(self.data))
                    time.sleep(DELAY)
                
                if len(self.data) < TARGET:
                    self.incomplete_data.emit(len(self.data))
                else:
                    self.finished_scraping.emit(list(self.data))
                return

            # ---------- Normal mode ----------
            self.status.emit("Normal Mode Scraping...")
            months = [(y, m) for y in range(START_YEAR, END_YEAR + 1) for m in range(1, 13)]
            per_month = TARGET // len(months) + 1

            for (year, month) in months:
                if not self.running or len(self.data) >= TARGET: break
                html = self._fetch_with_retry(CATEGORY, year, month, 0)
                if html is None: continue
                rows = parse_listing(html, year, month, category=CATEGORY)[:per_month]
                for row in rows:
                    if row["arxiv_id"] in self.seen: continue
                    self.seen.add(row["arxiv_id"])
                    self.data.append(row)
                    if len(self.data) >= TARGET: break
                self.progress.emit(len(self.data))
                self.batch_ready.emit(list(self.data))
                time.sleep(DELAY)

            self.finished_scraping.emit(list(self.data))

        except Exception as e:
            # GLOBAL ERROR CATCH
            self.status.emit(f"Fatal Error: {e}")
            self.error_occurred.emit(str(e))
            self.finished_scraping.emit([])