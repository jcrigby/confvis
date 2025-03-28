# LDS Conference Talk Scraper (Updated)

This tool scrapes LDS General Conference talks and saves them as text files for use with the clustering tool. It has been updated to navigate the complex structure of the Church's website.

## Installation

1. Make sure you have Python 3.7+ installed
2. Install the required packages:
   ```
   pip install requests beautifulsoup4
   ```

## Usage

```
python lds_talk_scraper.py --output ./talks --start 2010 --end 2023
```

Arguments:
- `--output`: Directory to save the scraped talks (default: ./talks)
- `--start`: First year to scrape (default: 2010)
- `--end`: Last year to scrape (default: current year)

## How It Works

This updated scraper follows a two-step process to find all talks:

1. **Session Discovery**: First, it identifies all the session pages (Saturday Morning, Sunday Afternoon, etc.) for each conference.
2. **Talk Extraction**: Then it visits each session page to find and extract individual talks.

This approach is more robust than trying to find all talks directly from the main conference page.

## Output

The script will:
1. Create a directory structure organized by year
2. Save each talk as a text file with filename: `YYYY_MM_Speaker_Title.txt`
3. Include metadata (title, speaker, calling, date) at the top of each file
4. Create a `talk_index.json` file with an index of all downloaded talks

## Improved Features

The updated scraper includes:
- Multiple CSS selector patterns to handle different page layouts
- Fallback mechanisms if standard selectors don't work
- Better filtering to avoid duplicates and non-talk pages
- More robust error handling
- Detailed logging of the scraping process

## Notes

- The scraper introduces a 1-second delay between requests to avoid overwhelming the Church's servers
- The full scraping process might take some time, particularly for a large date range
- If you encounter issues with specific conferences, try adjusting the year range

## Integration with Clustering Tool

The output of this scraper is designed to work directly with the LDS Conference Talk Clustering Tool:

```
python main.py --dir ./talks --clusters 8 --interactive
```

## Alternatives

If this script doesn't meet your needs, consider these GitHub projects:
- [johnmwood/LDS-Conference-Scraper](https://github.com/johnmwood/LDS-Conference-Scraper)
- [lukejoneslj/GeneralConferenceScraper](https://github.com/lukejoneslj/GeneralConferenceScraper)
- [simmeringratchet/LDSGeneralConferenceDownloader](https://github.com/simmeringratchet/LDSGeneralConferenceDownloader) (for audio files)
