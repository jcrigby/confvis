import os
import requests
from bs4 import BeautifulSoup
import json
import re
import time
import argparse
from datetime import datetime

class LDSConferenceScraper:
    def __init__(self, output_dir="./talks", start_year=2010, end_year=None):
        self.base_url = "https://www.churchofjesuschrist.org/study/general-conference"
        self.output_dir = output_dir
        self.start_year = start_year
        self.end_year = end_year if end_year else datetime.now().year
        
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def get_conference_urls(self):
        """Generate URLs for each conference between start_year and end_year."""
        urls = []
        for year in range(self.start_year, self.end_year + 1):
            for month in ["04", "10"]:  # April and October conferences
                urls.append(f"{self.base_url}/{year}/{month}?lang=eng")
        return urls
    
    def get_talk_urls(self, conference_url):
        """Get all talk URLs from a conference page."""
        print(f"Fetching talks from: {conference_url}")
        response = requests.get(conference_url)
        if response.status_code != 200:
            print(f"Failed to fetch conference page: {conference_url}")
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        talk_links = []
        
        # Find talk links - this selector may need adjustment based on the website structure
        for a in soup.select(".doc-map a[href*='/study/general-conference/']"):
            href = a.get('href')
            if href and '/study/general-conference/' in href and not href.endswith('?lang=eng'):
                # Convert relative URLs to absolute
                if href.startswith('/'):
                    href = f"https://www.churchofjesuschrist.org{href}?lang=eng"
                elif not href.startswith('http'):
                    href = f"https://www.churchofjesuschrist.org/study/general-conference/{href}?lang=eng"
                
                talk_links.append(href)
        
        return talk_links
    
    def extract_talk_content(self, talk_url):
        """Extract the content from a talk page."""
        print(f"Fetching talk: {talk_url}")
        response = requests.get(talk_url)
        if response.status_code != 200:
            print(f"Failed to fetch talk: {talk_url}")
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract title
        title_elem = soup.select_one("h1.title")
        title = title_elem.text.strip() if title_elem else "Unknown Title"
        
        # Extract speaker
        speaker_elem = soup.select_one(".author-name")
        speaker = speaker_elem.text.strip() if speaker_elem else "Unknown Speaker"
        
        # Extract speaker's calling/role
        calling_elem = soup.select_one(".article-author p.role")
        calling = calling_elem.text.strip() if calling_elem else ""
        
        # Extract talk content (paragraphs)
        content = []
        for p in soup.select(".body-block p"):
            content.append(p.text.strip())
        
        # Extract date information from URL
        date_match = re.search(r'/general-conference/(\d{4})/(\d{2})/', talk_url)
        if date_match:
            year, month = date_match.groups()
            month_name = "April" if month == "04" else "October" if month == "10" else month
            date = f"{month_name} {year}"
        else:
            date = "Unknown Date"
        
        # Create talk object
        talk = {
            "title": title,
            "speaker": speaker,
            "calling": calling,
            "date": date,
            "url": talk_url,
            "content": content,
            "full_text": "\n\n".join(content)
        }
        
        return talk
    
    def save_talk(self, talk):
        """Save a talk to a text file."""
        if not talk:
            return
            
        # Create year directory if it doesn't exist
        year_dir = os.path.join(self.output_dir, talk["date"].split()[-1])
        if not os.path.exists(year_dir):
            os.makedirs(year_dir)
            
        # Create a filename from the talk title and speaker
        title_part = re.sub(r'[^\w\s-]', '', talk["title"]).strip().replace(' ', '_')
        speaker_part = re.sub(r'[^\w\s-]', '', talk["speaker"]).strip().replace(' ', '_')
        filename = f"{talk['date'].split()[-1]}_{talk['date'].split()[0]}_{speaker_part}_{title_part}.txt"
        filepath = os.path.join(year_dir, filename)
        
        # Write talk to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"Title: {talk['title']}\n")
            f.write(f"Speaker: {talk['speaker']}\n")
            f.write(f"Calling: {talk['calling']}\n")
            f.write(f"Date: {talk['date']}\n")
            f.write(f"URL: {talk['url']}\n\n")
            f.write(talk['full_text'])
            
        print(f"Saved talk: {filepath}")
        return filepath
    
    def scrape_conferences(self):
        """Scrape all conferences between start_year and end_year."""
        conference_urls = self.get_conference_urls()
        all_talks = []
        
        for conf_url in conference_urls:
            talk_urls = self.get_talk_urls(conf_url)
            print(f"Found {len(talk_urls)} talks in conference: {conf_url}")
            
            for talk_url in talk_urls:
                try:
                    talk = self.extract_talk_content(talk_url)
                    if talk:
                        self.save_talk(talk)
                        all_talks.append(talk)
                except Exception as e:
                    print(f"Error processing talk {talk_url}: {str(e)}")
                
                # Be nice to the server
                time.sleep(1)
        
        # Save a JSON index of all talks
        index_path = os.path.join(self.output_dir, "talk_index.json")
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(all_talks, f, indent=2)
            
        print(f"Scraping complete. Scraped {len(all_talks)} talks.")
        return all_talks

def main():
    parser = argparse.ArgumentParser(description='Scrape LDS General Conference Talks')
    parser.add_argument('--output', type=str, default='./talks', 
                        help='Directory to save the talks (default: ./talks)')
    parser.add_argument('--start', type=int, default=2010, 
                        help='Start year (default: 2010)')
    parser.add_argument('--end', type=int, default=None, 
                        help='End year (default: current year)')
    
    args = parser.parse_args()
    
    scraper = LDSConferenceScraper(
        output_dir=args.output,
        start_year=args.start,
        end_year=args.end
    )
    
    scraper.scrape_conferences()

if __name__ == "__main__":
    main()
