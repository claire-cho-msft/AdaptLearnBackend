#!/usr/bin/env python3
"""
Test script for improved content adaptation system
"""

import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from app import create_beginner_adaptation, create_intermediate_adaptation
    
    print("🧪 Testing Improved Content Adaptation System")
    print("=" * 60)
    
    # Test different types of content
    test_contents = [
        {
            'type': 'Installation instruction',
            'content': 'Install the Azure Developer CLI on your system using the package manager.'
        },
        {
            'type': 'Command explanation', 
            'content': 'Run the azd up command to package, provision and deploy the app resources to Azure.'
        },
        {
            'type': 'Deployment concept',
            'content': 'The deployment process involves provisioning cloud resources and deploying your application code to those resources.'
        },
        {
            'type': 'Generic content',
            'content': 'This tool helps developers quickly deploy applications to the cloud using modern DevOps practices.'
        }
    ]
    
    for i, test in enumerate(test_contents, 1):
        print(f"📝 Test {i}: {test['type']}")
        print(f"   Original: {test['content']}")
        print()
        
        # Test beginner level
        print("   🟢 BEGINNER adaptation:")
        beginner_result = create_beginner_adaptation(test['content'], "Test Section")
        print(f"   {beginner_result}")
        print()
        
        # Test intermediate level
        print("   🟡 INTERMEDIATE adaptation:")
        intermediate_result = create_intermediate_adaptation(test['content'], "Test Section") 
        print(f"   {intermediate_result}")
        print()
        
        print("-" * 60)
        print()
    
    print("✅ Improved content adaptation tests completed!")
    print("🎯 Key improvements:")
    print("   • More concise and respectful tone")
    print("   • Practical, actionable information")
    print("   • Professional but accessible language")
    print("   • Clear differentiation between skill levels")
    print("🚀 Run the full application with: cd src && python app.py")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please make sure you're in the right directory and dependencies are installed")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error during testing: {e}")
    sys.exit(1)
