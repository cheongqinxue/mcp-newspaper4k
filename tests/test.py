#!/usr/bin/env python3
"""Simple test script for the newspaper4k MCP server."""

import sys
sys.path.append("..")
import json
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    
    try:
        import newspaper
        print("✓ newspaper4k imported successfully")
        print(f"  Version: {newspaper.__version__}")
    except ImportError as e:
        print(f"✗ Failed to import newspaper4k: {e}")
        return False
    
    try:
        from newspaper import Article, Source
        print("✓ Article and Source classes imported")
    except ImportError as e:
        print(f"✗ Failed to import Article/Source: {e}")
        return False
    
    try:
        from newspaper.google_news import GoogleNewsSource
        print("✓ GoogleNewsSource imported")
    except ImportError as e:
        print(f"✗ Failed to import GoogleNewsSource: {e}")
        print("  Note: This requires newspaper4k[gnews]")
        return False
    
    try:
        from fastmcp import FastMCP
        print("✓ FastMCP imported")
    except ImportError as e:
        print(f"✗ Failed to import FastMCP: {e}")
        return False
    
    return True


def test_basic_functionality():
    """Test basic newspaper4k functionality."""
    print("\nTesting basic functionality...")
    
    try:
        import newspaper
        from newspaper import Article
        
        # Test creating an article object
        article = Article("https://example.com")
        print("✓ Article object created successfully")
        
        # Test getting supported languages
        from newspaper.languages import valid_languages
        languages = list(valid_languages())
        print(f"✓ Found {len(languages)} supported languages")
        
        # Test getting popular URLs
        popular_urls = newspaper.popular_urls()
        print(f"✓ Found {len(popular_urls)} popular URLs")
        
        return True
        
    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        return False


def test_server_import():
    """Test importing the server module."""
    print("\nTesting server import...")
    
    try:
        # Add the current directory to the path
        sys.path.insert(0, str(Path(__file__).parent.parent))
        
        from mcp_newspaper4k.server import (
            scrape_single_article,
            scrape_website,
            search_google_news,
            get_supported_languages,
            get_popular_urls
        )
        print("✓ Server functions imported successfully")
        return True
        
    except Exception as e:
        print(f"✗ Server import failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=== Newspaper4k MCP Server Test ===\n")
    
    tests = [
        ("Imports", test_imports),
        ("Basic Functionality", test_basic_functionality),
        ("Server Import", test_server_import),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"Running {test_name} test...")
        if test_func():
            passed += 1
            print(f"✓ {test_name} test passed\n")
        else:
            print(f"✗ {test_name} test failed\n")
    
    print(f"=== Test Results ===")
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! The server should work correctly.")
    else:
        print("⚠️  Some tests failed. Please check the installation.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 