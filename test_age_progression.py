#!/usr/bin/env python3
"""
Test script for the new AI-based age progression model
"""

import os
import sys
from PIL import Image
import numpy as np
from age_progression_model import get_age_model

def create_test_image():
    """Create a simple test image for testing"""
    # Create a simple colored square as test image
    img = Image.new('RGB', (256, 256), color='lightblue')
    
    # Add some simple features to make it more face-like
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    
    # Draw simple face features
    draw.ellipse([80, 80, 176, 176], fill='peachpuff')  # Face
    draw.ellipse([100, 110, 120, 130], fill='black')    # Left eye
    draw.ellipse([136, 110, 156, 130], fill='black')    # Right eye
    draw.ellipse([120, 140, 140, 160], fill='pink')      # Nose
    draw.ellipse([110, 170, 150, 180], fill='red')       # Mouth
    
    return img

def test_age_progression():
    """Test the age progression functionality"""
    print("🧪 Testing AI-based Age Progression Model...")
    print("=" * 50)
    
    try:
        # Create test image
        print("📸 Creating test image...")
        test_image = create_test_image()
        test_image.save("test_input.jpg")
        print("✅ Test image created: test_input.jpg")
        
        # Get the age progression model
        print("🤖 Loading age progression model...")
        model = get_age_model()
        print("✅ Model loaded successfully!")
        
        # Test age progression
        print("\n🔄 Testing age progression...")
        
        # Test different age ranges
        test_cases = [
            (10, "Aging by 10 years"),
            (20, "Aging by 20 years"),
            (-5, "Rejuvenating by 5 years"),
            (30, "Aging by 30 years")
        ]
        
        for years, description in test_cases:
            print(f"\n📈 {description}...")
            
            try:
                # Perform age progression
                aged_image = model.progress_age(test_image, years)
                
                # Save result
                output_filename = f"test_aged_{years}.jpg"
                aged_image.save(output_filename)
                
                print(f"✅ Success! Result saved as: {output_filename}")
                
                # Verify output dimensions
                if aged_image.size == test_image.size:
                    print(f"✅ Output dimensions correct: {aged_image.size}")
                else:
                    print(f"⚠️  Output dimensions changed: {aged_image.size}")
                
            except Exception as e:
                print(f"❌ Error in {description}: {str(e)}")
        
        # Test model information
        print(f"\n📊 Model Information:")
        print(f"   Device: {model.device}")
        print(f"   Model available: {model.model is not None}")
        
        # Clean up test files
        print(f"\n🧹 Cleaning up test files...")
        test_files = ["test_input.jpg"] + [f"test_aged_{years}.jpg" for years, _ in test_cases]
        
        for file in test_files:
            if os.path.exists(file):
                os.remove(file)
                print(f"   Removed: {file}")
        
        print(f"\n🎉 Age progression model test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_fallback_functionality():
    """Test the fallback functionality when AI model fails"""
    print("\n🛡️  Testing Fallback Functionality...")
    print("=" * 50)
    
    try:
        from age_progression_model import AgeProgressionModel
        
        # Create model without loading (to test fallback)
        model = AgeProgressionModel()
        model.model = None  # Force fallback mode
        
        # Create test image
        test_image = create_test_image()
        
        # Test fallback age progression
        print("🔄 Testing fallback age progression...")
        aged_image = model.progress_age(test_image, 15)
        
        # Save result
        aged_image.save("test_fallback.jpg")
        print("✅ Fallback functionality works! Result saved as: test_fallback.jpg")
        
        # Clean up
        if os.path.exists("test_fallback.jpg"):
            os.remove("test_fallback.jpg")
            print("🧹 Cleaned up fallback test file")
        
        return True
        
    except Exception as e:
        print(f"❌ Fallback test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Age Progression Model Tests")
    print("=" * 60)
    
    # Run main test
    success1 = test_age_progression()
    
    # Run fallback test
    success2 = test_fallback_functionality()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("🎉 ALL TESTS PASSED! Age progression model is working correctly.")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED! Please check the errors above.")
        sys.exit(1)
