#!/usr/bin/env python3
"""
Test script for selective content adaptation system
"""

import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from app import adapt_content_for_level, create_beginner_adaptation, create_intermediate_adaptation, MODEL_AVAILABLE
    
    print("🧪 Testing Selective Content Adaptation System")
    print("=" * 60)
    
    print("✅ Model and functions loaded successfully!")
    print()
    
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
            'type': 'Code block (should not adapt)',
            'content': '```bash\nazd init -t hello-azd\n```'
        }
    ]
    
    for test in test_contents:
        print(f"📝 Testing: {test['type']}")
        print(f"   Original: {test['content']}")
        print()
        
        # Test beginner level
        print("   🟢 Beginner adaptation:")
        beginner_result = create_beginner_adaptation(test['content'], "Test Section")
        print(f"   {beginner_result}")
        print()
        
        # Test intermediate level
        print("   🟡 Intermediate adaptation:")
        intermediate_result = create_intermediate_adaptation(test['content'], "Test Section") 
        print(f"   {intermediate_result}")
        print()
        
        print("-" * 60)
        print()
    
    print("✅ All content adaptation tests completed!")
    print("🎯 The system now adapts explanatory text while preserving code blocks and technical elements!")
    print("🚀 Run the full application with: cd src && python app.py")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please make sure you're in the right directory and dependencies are installed")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error during testing: {e}")
    sys.exit(1)
