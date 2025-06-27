#!/usr/bin/env python3
"""
Simple test script to verify content adaptation is working
"""

import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from app import create_beginner_adaptation, create_intermediate_adaptation, adapt_content_for_level
    
    print("🧪 Testing Simple Content Adaptation")
    print("=" * 50)
    
    # Test simple content
    test_content = "Install the Azure Developer CLI on your system using the package manager."
    
    print(f"Original: {test_content}")
    print()
    
    # Test beginner adaptation
    print("🟢 Beginner:")
    beginner_result = adapt_content_for_level(test_content, 0, "Installation")
    print(beginner_result)
    print()
    
    # Test intermediate adaptation
    print("🟡 Intermediate:")
    intermediate_result = adapt_content_for_level(test_content, 1, "Installation")
    print(intermediate_result)
    print()
    
    # Test advanced (should return original)
    print("🔴 Advanced:")
    advanced_result = adapt_content_for_level(test_content, 2, "Installation")
    print(advanced_result)
    print()
    
    print("✅ Adaptation test completed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
