#!/usr/bin/env python3
"""
Cache management utility for the content adaptation system
"""

import sys
import os
import requests
import argparse

def clear_cache(base_url="http://localhost:5000"):
    """Clear the content adaptation cache"""
    try:
        response = requests.post(f"{base_url}/clear-cache")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Cache cleared successfully!")
            print(f"   Removed {data['cache_size']} cached items")
        else:
            print(f"❌ Failed to clear cache: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the Flask app. Make sure it's running on http://localhost:5000")
    except Exception as e:
        print(f"❌ Error: {e}")

def check_cache_status(base_url="http://localhost:5000"):
    """Check current cache status"""
    try:
        response = requests.get(f"{base_url}/cache-status")
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Cache Status:")
            print(f"   Total cached items: {data['cache_size']}")
            if data['cache_size'] > 0:
                print(f"   Sample keys: {data['cached_items'][:5]}")
        else:
            print(f"❌ Failed to get cache status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the Flask app. Make sure it's running on http://localhost:5000")
    except Exception as e:
        print(f"❌ Error: {e}")

def clear_cache_locally():
    """Clear cache by directly accessing the app module"""
    try:
        # Add src to path
        sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
        from app import adapted_content_cache
        
        cache_size = len(adapted_content_cache)
        adapted_content_cache.clear()
        print(f"✅ Local cache cleared successfully!")
        print(f"   Removed {cache_size} cached items")
        
    except ImportError:
        print("❌ Could not import app module. Make sure you're in the right directory.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage content adaptation cache")
    parser.add_argument("action", choices=["clear", "status", "clear-local"], 
                       help="Action to perform")
    parser.add_argument("--url", default="http://localhost:5000", 
                       help="Base URL of the Flask app")
    
    args = parser.parse_args()
    
    print("🧹 Content Adaptation Cache Manager")
    print("=" * 40)
    
    if args.action == "clear":
        clear_cache(args.url)
    elif args.action == "status":
        check_cache_status(args.url)
    elif args.action == "clear-local":
        clear_cache_locally()
