#!/usr/bin/env python3
"""MCP server for web scraping using newspaper4k."""

import json
import logging
import tempfile
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import Field
from typing import Annotated
from urllib.parse import urlparse

from fastmcp import FastMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastMCP server instance
mcp = FastMCP(
    name="Newspaper4k Web Scraper",
    instructions="""
    This server provides web scraping capabilities using newspaper4k.
    It can scrape single webpages, entire websites, and search Google News.
    Results are returned in JSON format with extracted content and metadata.
    """
)

# Import newspaper4k modules
try:
    import newspaper
    from newspaper import Article, Source
    from newspaper.google_news import GoogleNewsSource
    from newspaper.configuration import Configuration
except ImportError as e:
    logger.error(f"Failed to import newspaper4k: {e}")
    logger.error("Please install newspaper4k: pip install newspaper4k[gnews]")
    raise


@mcp.tool()
def scrape_single_article(
    url: Annotated[str, Field(description="URL of the article to scrape")],
    language: Annotated[Optional[str], Field(description="Language code (e.g., 'en', 'es', 'fr'). If not specified, will auto-detect.")] = None,
    include_nlp: Annotated[bool, Field(description="Whether to include NLP analysis (keywords, summary)")] = True
) -> str:
    """Scrape a single article from a URL using newspaper4k.
    
    Args:
        url: URL of the article to scrape
        language: Language code (e.g., 'en', 'es', 'fr'). If not specified, will auto-detect.
        include_nlp: Whether to include NLP analysis (keywords, summary)
        
    Returns:
        JSON string containing the scraped article data
    """
    logger.info(f"Scraping single article: {url}")
    
    try:
        # Create article object
        article = Article(url, language=language)
        
        # Download and parse the article
        article.download()
        article.parse()
        
        # Perform NLP analysis if requested
        if include_nlp:
            try:
                article.nlp()
            except Exception as e:
                logger.warning(f"NLP analysis failed: {e}")
        
        # Prepare result
        result = {
            "url": url,
            "title": article.title,
            "text": article.text,
            "authors": article.authors,
            "publish_date": article.publish_date.isoformat() if article.publish_date else None,
            "top_image": article.top_image,
            "images": article.images,
            "movies": article.movies,
            "meta_description": article.meta_description,
            "meta_keywords": article.meta_keywords,
            "meta_lang": article.meta_lang,
            "canonical_link": article.canonical_link,
            "meta_favicon": article.meta_favicon,
            "meta_img": article.meta_img,
            "meta_data": article.meta_data,
            "tags": article.tags,
            "tweets": article.tweets,
            "links": article.links,
            "scraped_at": datetime.now().isoformat()
        }
        
        # Add NLP data if available
        if include_nlp and hasattr(article, 'keywords') and article.keywords:
            result["keywords"] = article.keywords
        if include_nlp and hasattr(article, 'summary') and article.summary:
            result["summary"] = article.summary
        
        logger.info(f"Successfully scraped article: {article.title}")
        return json.dumps(result, indent=2, default=str)
        
    except Exception as e:
        logger.error(f"Error scraping article {url}: {str(e)}")
        raise


@mcp.tool()
def scrape_website(
    url: Annotated[str, Field(description="URL of the website to scrape")],
    max_articles: Annotated[int, Field(description="Maximum number of articles to scrape")] = 10,
    language: Annotated[Optional[str], Field(description="Language code (e.g., 'en', 'es', 'fr')")] = None,
    include_nlp: Annotated[bool, Field(description="Whether to include NLP analysis for articles")] = False,
    download_articles: Annotated[bool, Field(description="Whether to download and parse individual articles")] = True
) -> str:
    """Scrape a website to get article URLs and optionally download articles.
    
    Args:
        url: URL of the website to scrape
        max_articles: Maximum number of articles to scrape
        language: Language code (e.g., 'en', 'es', 'fr')
        include_nlp: Whether to include NLP analysis for articles
        download_articles: Whether to download and parse individual articles
        
    Returns:
        JSON string containing the scraped website data
    """
    logger.info(f"Scraping website: {url}")
    
    try:
        # Build the source
        config = Configuration()
        if language:
            config.language = language
        
        source = Source(url, config=config)
        source.build()
        
        # Get basic source information
        result = {
            "url": url,
            "domain": source.domain,
            "brand": source.brand,
            "description": source.description,
            "category_urls": source.category_urls(),
            "feed_urls": source.feed_urls(),
            "article_urls": [article.url for article in source.articles[:max_articles]],
            "total_articles_found": len(source.articles),
            "scraped_at": datetime.now().isoformat()
        }
        
        # Download articles if requested
        if download_articles:
            logger.info(f"Downloading {min(max_articles, len(source.articles))} articles...")
            articles_data = []
            
            for i, article in enumerate(source.articles[:max_articles]):
                try:
                    article.download()
                    article.parse()
                    
                    if include_nlp:
                        try:
                            article.nlp()
                        except Exception as e:
                            logger.warning(f"NLP analysis failed for article {i}: {e}")
                    
                    article_data = {
                        "url": article.url,
                        "title": article.title,
                        "text": article.text,
                        "authors": article.authors,
                        "publish_date": article.publish_date.isoformat() if article.publish_date else None,
                        "top_image": article.top_image,
                        "meta_description": article.meta_description,
                        "meta_lang": article.meta_lang
                    }
                    
                    if include_nlp and hasattr(article, 'keywords') and article.keywords:
                        article_data["keywords"] = article.keywords
                    if include_nlp and hasattr(article, 'summary') and article.summary:
                        article_data["summary"] = article.summary
                    
                    articles_data.append(article_data)
                    logger.info(f"Downloaded article {i+1}/{min(max_articles, len(source.articles))}: {article.title}")
                    
                except Exception as e:
                    logger.warning(f"Failed to download article {i}: {e}")
                    articles_data.append({
                        "url": article.url,
                        "error": str(e)
                    })
            
            result["articles"] = articles_data
        
        logger.info(f"Successfully scraped website: {source.brand}")
        return json.dumps(result, indent=2, default=str)
        
    except Exception as e:
        logger.error(f"Error scraping website {url}: {str(e)}")
        raise


@mcp.tool()
def search_google_news(
    keyword: Annotated[Optional[str], Field(description="Search keyword")] = None,
    topic: Annotated[Optional[str], Field(description="News topic (e.g., 'WORLD', 'BUSINESS', 'TECHNOLOGY')")] = None,
    country: Annotated[Optional[str], Field(description="Country code (e.g., 'US', 'GB', 'CA')")] = "US",
    period: Annotated[Optional[str], Field(description="Time period ('h', 'd', 'm', 'y')")] = "7d",
    max_results: Annotated[int, Field(description="Maximum number of results")] = 10,
    language: Annotated[Optional[str], Field(description="Language code (e.g., 'en', 'es', 'fr')")] = "en",
    include_nlp: Annotated[bool, Field(description="Whether to include NLP analysis for articles")] = False,
    download_articles: Annotated[bool, Field(description="Whether to download and parse individual articles")] = True
) -> str:
    """Search Google News for articles using newspaper4k's GoogleNewsSource.
    
    Args:
        keyword: Search keyword
        topic: News topic (e.g., 'WORLD', 'BUSINESS', 'TECHNOLOGY')
        country: Country code (e.g., 'US', 'GB', 'CA')
        period: Time period ('h', 'd', 'm', 'y')
        max_results: Maximum number of results
        language: Language code (e.g., 'en', 'es', 'fr')
        include_nlp: Whether to include NLP analysis for articles
        download_articles: Whether to download and parse individual articles
        
    Returns:
        JSON string containing the Google News search results
    """
    logger.info(f"Searching Google News - keyword: {keyword}, topic: {topic}, country: {country}")
    
    try:
        # Check if gnews is available
        try:
            import gnews
        except ImportError:
            raise ImportError(
                "Google News functionality requires the gnews package. "
                "Install it with: pip install newspaper4k[gnews]"
            )
        
        # Create Google News source
        config = Configuration()
        if language:
            config.language = language
        
        source = GoogleNewsSource(
            country=country,
            period=period,
            max_results=max_results,
            config=config
        )
        
        # Build the source
        if keyword:
            source.build(keyword=keyword)
        elif topic:
            source.build(topic=topic)
        else:
            source.build(top_news=True)
        
        # Get basic results
        result = {
            "search_type": "keyword" if keyword else "topic" if topic else "top_news",
            "keyword": keyword,
            "topic": topic,
            "country": country,
            "period": period,
            "language": language,
            "article_urls": source.article_urls(),
            "total_articles_found": len(source.articles),
            "scraped_at": datetime.now().isoformat()
        }
        
        # Download articles if requested
        if download_articles:
            logger.info(f"Downloading {len(source.articles)} articles...")
            articles_data = []
            
            for i, article in enumerate(source.articles):
                try:
                    article.download()
                    article.parse()
                    
                    if include_nlp:
                        try:
                            article.nlp()
                        except Exception as e:
                            logger.warning(f"NLP analysis failed for article {i}: {e}")
                    
                    article_data = {
                        "url": article.url,
                        "title": article.title,
                        "text": article.text,
                        "authors": article.authors,
                        "publish_date": article.publish_date.isoformat() if article.publish_date else None,
                        "top_image": article.top_image,
                        "meta_description": article.meta_description,
                        "meta_lang": article.meta_lang
                    }
                    
                    if include_nlp and hasattr(article, 'keywords') and article.keywords:
                        article_data["keywords"] = article.keywords
                    if include_nlp and hasattr(article, 'summary') and article.summary:
                        article_data["summary"] = article.summary
                    
                    articles_data.append(article_data)
                    logger.info(f"Downloaded article {i+1}/{len(source.articles)}: {article.title}")
                    
                except Exception as e:
                    logger.warning(f"Failed to download article {i}: {e}")
                    articles_data.append({
                        "url": article.url,
                        "error": str(e)
                    })
            
            result["articles"] = articles_data
        
        logger.info(f"Successfully searched Google News - found {len(source.articles)} articles")
        return json.dumps(result, indent=2, default=str)
        
    except Exception as e:
        logger.error(f"Error searching Google News: {str(e)}")
        raise


@mcp.tool()
def get_supported_languages() -> str:
    """Get list of supported languages in newspaper4k.
    
    Returns:
        JSON string containing supported languages
    """
    try:
        from newspaper.languages import valid_languages
        
        languages = list(valid_languages.keys())
        result = {
            "supported_languages": languages,
            "language_count": len(languages),
            "note": "These are the language codes supported by newspaper4k for article parsing"
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting supported languages: {str(e)}")
        raise


@mcp.tool()
def get_popular_urls() -> str:
    """Get list of popular news URLs that work well with newspaper4k.
    
    Returns:
        JSON string containing popular news URLs
    """
    try:
        popular_urls = newspaper.popular_urls()
        
        result = {
            "popular_urls": popular_urls,
            "url_count": len(popular_urls),
            "note": "These URLs are known to work well with newspaper4k"
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting popular URLs: {str(e)}")
        raise


if __name__ == "__main__":
    import signal
    import sys
    
    def signal_handler(signum, frame):
        """Handle shutdown signals."""
        logger.info("Shutting down server...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("MCP Newspaper4k Server starting...")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Newspaper4k version: {newspaper.__version__}")
    
    # Run the server
    mcp.run()
