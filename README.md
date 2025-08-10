# Newspaper4k MCP Server

An MCP (Model Context Protocol) server that provides web scraping capabilities using [newspaper4k](https://github.com/AndyTheFactory/newspaper4k). This server can scrape single webpages, entire websites, and search Google News.

## Features

- **Single Article Scraping**: Extract content, metadata, and NLP analysis from individual articles
- **Website Scraping**: Discover and scrape articles from entire news websites
- **Google News Search**: Search Google News by keywords, topics, or get top news
- **Multi-language Support**: Support for 20+ languages including English, Spanish, French, German, Chinese, Japanese, etc.
- **NLP Analysis**: Extract keywords and generate summaries (when enabled)
- **Comprehensive Metadata**: Extract authors, publish dates, images, links, and more

## Installation

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install fastmcp newspaper4k[gnews] pydantic
```

## Usage

### Running the Server

```bash
python mcp_newspaper4k/server.py
```

### Available Tools

#### 1. Scrape Single Article

Extract content from a single webpage:

```python
result = scrape_single_article(
    url="https://example.com/article",
    language="en",  # Optional: auto-detected if not specified
    include_nlp=True  # Optional: include keywords and summary
)
```

Returns JSON with:
- Article title, text, and authors
- Publish date and metadata
- Images, videos, and links
- Keywords and summary (if NLP enabled)

#### 2. Scrape Website

Discover and optionally download articles from a news website:

```python
result = scrape_website(
    url="https://example.com",
    max_articles=10,  # Maximum articles to process
    language="en",  # Optional
    include_nlp=False,  # Optional: NLP analysis for each article
    download_articles=True  # Whether to download full article content
)
```

Returns JSON with:
- Website metadata (domain, brand, description)
- Category and feed URLs
- Article URLs and optionally full article content

#### 3. Search Google News

Search Google News for articles:

```python
result = search_google_news(
    keyword="artificial intelligence",  # Search keyword
    # OR topic="TECHNOLOGY",  # News topic
    country="US",  # Country code
    period="7d",  # Time period: h, d, m, y
    max_results=10,
    language="en",
    include_nlp=False,
    download_articles=True
)
```

Available topics: `WORLD`, `BUSINESS`, `TECHNOLOGY`, `ENTERTAINMENT`, `SPORTS`, `SCIENCE`, `HEALTH`

#### 4. Get Supported Languages

Get list of supported languages:

```python
result = get_supported_languages()
```

#### 5. Get Popular URLs

Get list of news websites known to work well with newspaper4k:

```python
result = get_popular_urls()
```

## Example Usage

See `examples/newspaper4k_example.py` for a complete example demonstrating all features.

```python
# Scrape a single article
result = scrape_single_article(
    url="https://www.bbc.com/news/world-us-canada-68612345",
    include_nlp=True
)
data = json.loads(result)
print(f"Title: {data['title']}")
print(f"Summary: {data['summary']}")

# Search Google News
result = search_google_news(
    keyword="climate change",
    max_results=5,
    download_articles=True
)
data = json.loads(result)
print(f"Found {len(data['articles'])} articles")
```

## Configuration

The server uses newspaper4k's default configuration. You can customize behavior by modifying the `Configuration` object in the server code:

```python
from newspaper.configuration import Configuration

config = Configuration()
config.language = 'en'
config.number_threads = 10
config.request_timeout = 10
```

## Supported Languages

The server supports 20+ languages including:
- English (en)
- Spanish (es)
- French (fr)
- German (de)
- Chinese (zh)
- Japanese (ja)
- Korean (ko)
- Arabic (ar)
- And many more...

## Error Handling

The server includes comprehensive error handling:
- Network timeouts and connection errors
- Invalid URLs and missing content
- Language detection failures
- NLP analysis errors

All errors are logged and returned as exceptions with descriptive messages.

## Dependencies

- `fastmcp`: MCP server framework
- `newspaper4k[gnews]`: Web scraping library with Google News support
- `pydantic`: Data validation
- `gnews`: Google News API (included with newspaper4k[gnews])

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.