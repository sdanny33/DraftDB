import csv
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter

DB_ROOT = Path(__file__).parent.parent

DEFAULT_WORKERS = 8      # lower than before: too many threads gets requests rate-limited/dropped
MAX_ATTEMPTS = 5         # per link, per pass
RETRY_PASSES = 3         # extra passes over links that still failed (with fewer workers)
TIMEOUT = 30

REPLACEMENTS = [
    (re.compile(r'Shiny: Yes  '), ''),
    (re.compile(r'IVs: .*'), ''),
    (re.compile(r'\(F\) '), ''),
    (re.compile(r'\(M\) '), ''),
    (re.compile(r'Hidden Power: .*'), ''),
]
PAREN_RE = re.compile(r'.*\(([^)]*)\)\s*(.*)')


class FetchError(Exception):
    pass


def make_session(pool_size):
    session = requests.Session()
    adapter = HTTPAdapter(pool_connections=pool_size, pool_maxsize=pool_size)
    session.mount('https://', adapter)
    session.mount('http://', adapter)
    session.headers['User-Agent'] = 'Mozilla/5.0 (team-scraper)'
    return session


def replace_parenthetical(line):
    """Removes nicknames, keeping the mon's real name."""
    m = PAREN_RE.match(line)
    if m:
        return f"{m.group(1).strip()} {m.group(2).strip()}".strip()
    return line


def clean_pre(text):
    for pattern, replacement in REPLACEMENTS:
        text = pattern.sub(replacement, text)
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        return ''
    lines = [replace_parenthetical(line) for line in lines]
    return '\n'.join(lines) + '\n'


def fetch(session, link):
    """GET with backoff. Raises FetchError if it never succeeds, so nothing is dropped silently."""
    last = 'unknown error'
    for attempt in range(MAX_ATTEMPTS):
        try:
            response = session.get(link, timeout=TIMEOUT)
        except requests.RequestException as e:
            last = f'{type(e).__name__}: {e}'
        else:
            if response.status_code == 200:
                return response
            last = f'status {response.status_code}'
            if response.status_code == 429 or response.status_code >= 500:
                retry_after = response.headers.get('Retry-After', '')
                if retry_after.isdigit():
                    time.sleep(min(int(retry_after), 60))
                    continue
            elif response.status_code in (404, 410):
                break  # genuinely gone, retrying won't help
        time.sleep(2 ** attempt)
    raise FetchError(last)


def process_link(session, link):
    response = fetch(session, link)
    soup = BeautifulSoup(response.content, 'html.parser')
    return ''.join(clean_pre(pre.get_text()) for pre in soup.find_all('pre'))


def run_pass(links, workers, session):
    """Returns (results, failed) where results maps link -> extracted text."""
    results, failed = {}, {}
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(process_link, session, link): link for link in links}
        for n, future in enumerate(as_completed(futures), 1):
            link = futures[future]
            try:
                results[link] = future.result()
            except Exception as e:
                failed[link] = str(e)
            if n % 25 == 0 or n == len(links):
                print(f'  {n}/{len(links)} processed ({len(failed)} failed)')
    return results, failed


def scrape_website(fileName, outputFile, max_workers=DEFAULT_WORKERS):
    with open(fileName, 'r') as file:
        links = [row[0].strip() for row in csv.reader(file) if row and row[0].strip()]
    links = list(dict.fromkeys(links))  # dedupe, keep order
    total = len(links)

    results = {}
    pending = links
    workers = max_workers
    for p in range(RETRY_PASSES + 1):
        if not pending:
            break
        print(f'Pass {p + 1}: {len(pending)} links, {workers} workers')
        session = make_session(workers)
        got, failed = run_pass(pending, workers, session)
        results.update(got)
        pending = list(failed)
        workers = max(1, workers // 2)  # back off harder each retry pass
        if pending:
            time.sleep(5)

    # Write in the same order as links.csv so runs are reproducible
    empty = []
    with open(outputFile, 'w', newline='') as output_file:
        for link in links:
            text = results.get(link)
            if text:
                output_file.write(text)
            elif text == '':
                empty.append(link)

    print(f'\nDone: {len(results)}/{total} pages fetched, {len(pending)} failed.')

    if empty:
        failed_path = Path(outputFile).with_name('no_pre_links.csv')
        with open(failed_path, 'w', newline='') as f:
            csv.writer(f).writerows([l] for l in empty)
        print(f'{len(empty)} pages loaded but had no <pre> team data -> {failed_path.name}')

    if pending:
        failed_path = Path(outputFile).with_name('failed_links.csv')
        with open(failed_path, 'w', newline='') as f:
            csv.writer(f).writerows([l] for l in pending)
        print(f'{len(pending)} links never loaded -> {failed_path.name}')


def main():
    scrape_website(DB_ROOT / 'teams' / 'links.csv', DB_ROOT / 'teams' / 'output.csv')


if __name__ == "__main__":
    main()