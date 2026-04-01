import csv
import requests
from bs4 import BeautifulSoup
import re

# Function to scrape website and process data
def scrape_website(fileName, outputFile):

    # Read links from CSV file
    links = []
    with open(fileName, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            links.append(row[0])

    # Process each link
    for link in links:
        print(f'Scraping {link}...')
        response = requests.get(link)
    
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all <pre> tags and extract text
            all_pre = soup.find_all('pre')
            for pre in all_pre:
                extract = pre.get_text()

                # Clean the uneeded text
                replacements = [
                    (r'Shiny: Yes  ', ''),
                    (r'IVs: .*', ''),
                    (r'\((F)\) ', ''),
                    (r'\((M)\) ', '')                ]
                for pattern, replacement in replacements:
                    extract = re.sub(pattern, replacement, extract)

                # Remove empty lines
                lines = [line for line in extract.splitlines() if line.strip()]
                if not lines:
                    continue
                
                # Removes the nicknames and gets the mons name
                def replace_parenthetical(line):
                    m = re.match(r'.*\(([^)]*)\)\s*(.*)', line)
                    if m:
                        name = m.group(1).strip()
                        rest = m.group(2).strip()
                        return f"{name} {rest}".strip()
                    return line

                lines = [replace_parenthetical(line) for line in lines]

                clean_extract = '\n'.join(lines) + '\n'
                extract = clean_extract

                # Append cleaned data to output file
                with open(outputFile, 'a', newline='') as output_file:
                    output_file.write(extract)
        else:
            print(f'Failed to retrieve {link}, status code: {response.status_code}')

# Run the scraper
if __name__ == "__main__":
    scrape_website('links.csv', 'output.csv')