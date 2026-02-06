import time
import sys
import asyncio
from server import search_web, scrape_url

# Add /app to path just in case, though it should be CWD
sys.path.append("/app")


async def benchmark_tool(func, name, **kwargs):
    print(f"Benchmarking {name} with args: {kwargs}...")
    start = time.time()
    try:
        if asyncio.iscoroutinefunction(func):
            result = await func(**kwargs)
        else:
            result = func(**kwargs)

        duration = time.time() - start

        # Output snippet
        preview = str(result)[:100].replace("\n", " ")
        print(f"✅ {name}: {duration:.4f}s | Result: {preview}...")
        return duration
    except Exception as e:
        print(f"❌ {name}: Failed with {e}")
        return None


async def main():
    print("Starting MCP Service Benchmark (Internal)\n" + "=" * 40)

    # Warmup / Test 1: search_web (DuckDuckGo - "ddgs")
    # search_web is sync
    await benchmark_tool(
        search_web, "search_web (DuckDuckGo)", query="Python programming", max_results=3
    )

    # Test 2: scrape_url
    # scrape_url is now async
    await benchmark_tool(scrape_url, "scrape_url", url="https://example.com")

    # Test 3: Heavy URL
    await benchmark_tool(scrape_url, "scrape_url (Heavy)", url="https://www.python.org")

    print("=" * 40)
    print("Benchmark Complete")


if __name__ == "__main__":
    asyncio.run(main())
