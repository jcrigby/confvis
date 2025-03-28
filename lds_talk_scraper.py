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
        
        # First, get all session URLs from the conference page
        session_links = []
        
        # Looking for links to sessions (Saturday Morning, etc.)
        for a in soup.select("a"):
            href = a.get('href')
            if href and 'session' in href.lower() and '/study/general-conference/' in href:
                # Convert relative URLs to absolute
                if href.startswith('/'):
                    full_href = f"https://www.churchofjesuschrist.org{href}"
                elif not href.startswith('http'):
                    full_href = f"https://www.churchofjesuschrist.org/study/general-conference/{href}"
                else:
                    full_href = href
                
                # Add lang=eng if not present
                if "?lang=eng" not in full_href:
                    full_href = f"{full_href}?lang=eng"
                    
                session_links.append(full_href)
        
        print(f"Found {len(session_links)} session links")
        
        # For each session, get the talk links
        for session_url in session_links:
            print(f"Fetching session: {session_url}")
            session_response = requests.get(session_url)
            if session_response.status_code != 200:
                print(f"Failed to fetch session page: {session_url}")
                continue
                
            session_soup = BeautifulSoup(session_response.text, 'html.parser')
            
            # Look for talk links within the session
            for talk_link in session_soup.select("a[href*='/study/general-conference/']"):
                href = talk_link.get('href')
                if not href:
                    continue
                    
                # Skip session links and already processed links
                if 'session' in href.lower() or href in talk_links:
                    continue
                    
                # Process only talk links
                if '/study/general-conference/' in href:
                    # Convert relative URLs to absolute
                    if href.startswith('/'):
                        full_href = f"https://www.churchofjesuschrist.org{href}"
                    elif not href.startswith('http'):
                        full_href = f"https://www.churchofjesuschrist.org/study/general-conference/{href}"
                    else:
                        full_href = href
                    
                    # Add lang=eng if not present
                    if "?lang=eng" not in full_href:
                        full_href = f"{full_href}?lang=eng"
                    
                    # Add only if it's a talk link (not another session or the conference index)
                    parts = href.split('/')
                    if len(parts) > 4 and not any(x in href for x in ['session', 'index']):
                        talk_links.append(full_href)
            
            # Be nice to the server
            time.sleep(1)
        
        # Remove duplicates
        talk_links = list(set(talk_links))
        print(f"Found {len(talk_links)} talk links")
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
        if not title_elem:
            title_elem = soup.select_one("h1")
        title = title_elem.text.strip() if title_elem else "Unknown Title"
        
        # If the title is too generic (like conference name), skip this talk
        if 'general conference' in title.lower() and len(title.split()) < 5:
            print(f"Skipping generic conference page: {title}")
            return None
        
        # Extract speaker
        speaker_elem = soup.select_one(".author-name")
        if not speaker_elem:
            speaker_elem = soup.select_one(".articles-author")
        speaker = speaker_elem.text.strip() if speaker_elem else "Unknown Speaker"
        
        # Extract speaker's calling/role
        calling_elem = soup.select_one(".article-author p.role")
        if not calling_elem:
            calling_elem = soup.select_one(".articles-subtitle")
        calling = calling_elem.text.strip() if calling_elem else ""
        
        # Extract talk content (paragraphs)
        content = []
        
        # Try different selectors for paragraphs
        paragraph_selectors = [
            ".body-block p", 
            ".body p",
            "article p",
            "#content p"
        ]
        
        for selector in paragraph_selectors:
            paragraphs = soup.select(selector)
            if paragraphs:
                for p in paragraphs:
                    text = p.text.strip()
                    if text and len(text) > 10:  # Skip very short paragraphs that might be metadata
                        content.append(text)
                break  # Stop if we found paragraphs with this selector
        
        # If no content found, try a more generic approach
        if not content:
            print(f"No content found with standard selectors, trying generic approach for: {talk_url}")
            for p in soup.find_all('p'):
                text = p.text.strip()
                if text and len(text) > 10:
                    content.append(text)
        
        # Extract date information from URL
        date_match = re.search(r'/general-conference/(\d{4})/(\d{2})/', talk_url)
        if date_match:
            year, month = date_match.groups()
            month_name = "April" if month == "04" else "October" if month == "10" else month
            date = f"{month_name} {year}"
        else:
            date = "Unknown Date"
        
        # Skip if empty content
        if not content:
            print(f"No content found for talk: {talk_url}")
            return None
        
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
