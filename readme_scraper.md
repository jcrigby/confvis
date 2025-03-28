# LDS Conference Talk Scraper

This tool scrapes LDS General Conference talks and saves them as text files for use with the clustering tool.

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

## Output

The script will:
1. Create a directory structure organized by year
2. Save each talk as a text file with filename: `YYYY_MM_Speaker_Title.txt`
3. Include metadata (title, speaker, calling, date) at the top of each file
4. Create a `talk_index.json` file with an index of all downloaded talks

## Notes

- Be respectful of the Church's website and don't overload their servers with requests
- This script includes a 1-second delay between requests to avoid overwhelming the server
- The website structure may change, requiring updates to the CSS selectors in the script
- Check the Church's terms of service and robots.txt for any crawling restrictions

## Integration with Clustering Tool

The output of this scraper is designed to work directly with the LDS Conference Talk Clustering Tool. Simply point the clustering tool at the output directory:

```
python main.py --dir ./talks --clusters 8 --interactive
```

## Alternatives

If this script doesn't meet your needs, consider these GitHub projects:
- [johnmwood/LDS-Conference-Scraper](https://github.com/johnmwood/LDS-Conference-Scraper)
- [lukejoneslj/GeneralConferenceScraper](https://github.com/lukejoneslj/GeneralConferenceScraper)
- [simmeringratchet/LDSGeneralConferenceDownloader](https://github.com/simmeringratchet/LDSGeneralConferenceDownloader) (for audio files)
