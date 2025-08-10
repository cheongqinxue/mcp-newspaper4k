#!/usr/bin/env python3
"""Example usage of the newspaper4k MCP server through MCP protocol."""

import json
import asyncio
import sys
from pathlib import Path
import subprocess
import time
import signal
import os

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))


async def wait_for_server_ready(process, timeout=30):
    """Wait for the server to be ready by checking stderr output."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        # Check if process is still running
        if process.poll() is not None:
            raise RuntimeError("Server process terminated unexpectedly")
        
        # Check stderr for initialization messages
        stderr_line = process.stderr.readline()
        if stderr_line:
            print(f"Server: {stderr_line.strip()}")
            # Look for FastMCP startup message
            if "Starting MCP server" in stderr_line or "FastMCP" in stderr_line:
                print("Server appears to be starting up...")
        
        # Small delay to avoid busy waiting
        await asyncio.sleep(0.1)
    
    raise TimeoutError("Server did not start within timeout period")


async def test_mcp_server():
    """Test the newspaper4k MCP server through the MCP protocol."""
    
    print("=== Testing Newspaper4k MCP Server ===\n")
    
    # Start the MCP server as a subprocess
    server_path = Path(__file__).parent.parent / "mcp_newspaper4k" / "server.py"
    
    print(f"Starting MCP server from: {server_path}")
    
    # Start the server process
    process = subprocess.Popen(
        [sys.executable, str(server_path)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1  # Line buffered
    )
    
    try:
        # Wait for server to be ready
        print("Waiting for server to initialize...")
        # await wait_for_server_ready(process)
        await asyncio.sleep(10)
        
        # Connect directly to the existing process
        print("Connecting to server...")
        
        # Create a simple MCP client that connects to the existing process
        async def run_tests():
            # Read the initialization message from stdout
            init_line = process.stdout.readline()
            print(f"Init: {init_line.strip()}")
            
            # Send initialization request
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "newspaper4k-test-client",
                        "version": "1.0.0"
                    }
                }
            }
            
            process.stdin.write(json.dumps(init_request) + "\n")
            process.stdin.flush()
            
            # Read initialization response
            init_response = process.stdout.readline()
            print(f"Init response: {init_response.strip()}")
            
            # Send initialized notification
            initialized_notification = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
                "params": {}
            }
            
            process.stdin.write(json.dumps(initialized_notification) + "\n")
            process.stdin.flush()
            
            # Now test the tools
            test_cases = [
                ("get_supported_languages", {}, "1. Testing get_supported_languages..."),
                ("get_popular_urls", {}, "2. Testing get_popular_urls..."),
                ("scrape_single_article", {
                    "url": "https://www.bbc.com/news/world-us-canada-68612345",
                    "include_nlp": False
                }, "3. Testing scrape_single_article..."),
                ("search_google_news", {
                    "keyword": "artificial intelligence",
                    "max_results": 3,
                    "download_articles": False
                }, "4. Testing search_google_news..."),
                ("scrape_website", {
                    "url": "https://techcrunch.com",
                    "max_articles": 3,
                    "download_articles": False
                }, "5. Testing scrape_website...")
            ]
            
            for i, (tool_name, params, message) in enumerate(test_cases, 1):
                print(message)
                try:
                    # Send tool call request
                    tool_request = {
                        "jsonrpc": "2.0",
                        "id": i + 1,
                        "method": "tools/call",
                        "params": {
                            "name": tool_name,
                            "arguments": params
                        }
                    }
                    
                    process.stdin.write(json.dumps(tool_request) + "\n")
                    process.stdin.flush()
                    
                    # Read response
                    response = process.stdout.readline()
                    response_data = json.loads(response)
                    
                    if "result" in response_data:
                        result = response_data["result"]
                        if "content" in result and result["content"]:
                            content = result["content"][0]["text"]
                            data = json.loads(content)
                            
                            if tool_name == "get_supported_languages":
                                print(f"✓ Supported languages: {data['language_count']}")
                                print(f"  Sample: {data['supported_languages'][:5]}")
                            elif tool_name == "get_popular_urls":
                                print(f"✓ Popular URLs: {data['url_count']}")
                                print(f"  Sample: {data['popular_urls'][:3]}")
                            elif tool_name == "scrape_single_article":
                                print(f"✓ Article scraped successfully!")
                                print(f"  Title: {data['title']}")
                                print(f"  Text length: {len(data['text'])} characters")
                            elif tool_name == "search_google_news":
                                print(f"✓ Google News search successful!")
                                print(f"  Found: {data['total_articles_found']} articles")
                                print(f"  Sample URLs: {data['article_urls'][:2]}")
                            elif tool_name == "scrape_website":
                                print(f"✓ Website scraping successful!")
                                print(f"  Website: {data['brand']}")
                                print(f"  Found: {data['total_articles_found']} articles")
                                print(f"  Sample URLs: {data['article_urls'][:2]}")
                        else:
                            print(f"✓ Tool call successful but no content returned")
                    else:
                        print(f"✗ Error: {response_data.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    print(f"✗ Error: {e}")
                print()
        
        await run_tests()
                
    except Exception as e:
        print(f"Error connecting to MCP server: {e}")
    finally:
        # Clean up the server process
        try:
            process.terminate()
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        print("MCP server stopped.")


def main():
    """Run the MCP server test."""
    try:
        asyncio.run(test_mcp_server())
        print("=== MCP Server Test Completed ===")
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
    except Exception as e:
        print(f"Test failed: {e}")


if __name__ == "__main__":
    main() 