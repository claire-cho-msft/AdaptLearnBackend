#!/usr/bin/env python3
"""
Test script for the Hugging Face content adaptation system
"""

import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from app import adapt_content_for_level, MODEL_AVAILABLE
    
    print("🧪 Testing Hugging Face Content Adaptation System")
    print("=" * 50)
    
    if not MODEL_AVAILABLE:
        print("❌ Model not available. Please install requirements first:")
        print("   pip install transformers torch")
        sys.exit(1)
    
    print("✅ Model loaded successfully!")
    print()
    
    # Test content
    test_content = """Run the `azd up` command to package, provision and deploy the app resources to Azure."""
    
    print("Original content:")
    print(f"  {test_content}")
    print()
    
    # Test beginner level
    print("🟢 Beginner level adaptation:")
    beginner_content = adapt_content_for_level(test_content, 0, "Test Section")
    print(f"  {beginner_content}")
    print()
    
    # Test intermediate level  
    print("🟡 Intermediate level adaptation:")
    intermediate_content = adapt_content_for_level(test_content, 1, "Test Section")
    print(f"  {intermediate_content}")
    print()
    
    # Test advanced level
    print("🔴 Advanced level (should be unchanged):")
    advanced_content = adapt_content_for_level(test_content, 2, "Test Section")
    print(f"  {advanced_content}")
    print()
    
    print("✅ All tests completed successfully!")
    print("🚀 You can now run the full application with: cd src && python app.py")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please install requirements first: pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error during testing: {e}")
    sys.exit(1)
