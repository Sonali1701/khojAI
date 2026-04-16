#!/usr/bin/env python3
"""
Fast-AgingGAN Integration for Realistic Age Progression
Uses pre-trained GAN model for high-quality age transformation
"""

import os
import sys
import torch
import torch.nn as nn
from PIL import Image
import torchvision.transforms as transforms
import numpy as np
from typing import Optional

# Add Fast-AgingGAN to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'Fast-AgingGAN'))

try:
    from models import Generator
except ImportError:
    print("Error: Could not import Fast-AgingGAN models")
    print("Please ensure Fast-AgingGAN is properly cloned")
    sys.exit(1)

class FastAgingGAN:
    """
    Realistic Age Progression using Fast-AgingGAN
    Provides high-quality, GAN-based age transformation
    """
    
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.transform = None
        self.model_loaded = False
        
        print(f"FastAgingGAN initialized on device: {self.device}")
        
    def load_model(self):
        """Load the pre-trained Fast-AgingGAN model"""
        try:
            print("Loading Fast-AgingGAN model...")
            
            # Initialize the generator
            self.model = Generator(ngf=32, n_residual_blocks=9)
            
            # Load pre-trained weights
            model_path = os.path.join(os.path.dirname(__file__), 'Fast-AgingGAN', 'pretrained_model', 'state_dict.pth')
            
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model weights not found at {model_path}")
            
            checkpoint = torch.load(model_path, map_location=self.device)
            self.model.load_state_dict(checkpoint)
            self.model.to(self.device)
            self.model.eval()
            
            # Setup transforms
            self.transform = transforms.Compose([
                transforms.Resize((512, 512)),
                transforms.ToTensor(),
                transforms.Normalize(mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5))
            ])
            
            self.model_loaded = True
            print("Fast-AgingGAN model loaded successfully!")
            
        except Exception as e:
            print(f"Error loading Fast-AgingGAN model: {e}")
            self.model_loaded = False
            raise
    
    def preprocess_image(self, image: Image.Image) -> torch.Tensor:
        """Preprocess image for GAN input"""
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Apply transforms
        tensor = self.transform(image).unsqueeze(0)
        return tensor.to(self.device)
    
    def postprocess_image(self, tensor: torch.Tensor) -> Image.Image:
        """Convert GAN output back to PIL Image"""
        # Denormalize from [-1, 1] to [0, 1]
        tensor = tensor.squeeze(0).cpu()
        tensor = (tensor + 1.0) / 2.0
        tensor = torch.clamp(tensor, 0, 1)
        
        # Convert to PIL
        transform = transforms.ToPILImage()
        return transform(tensor)
    
    def progress_age(self, image: Image.Image, target_age_group: str = "old") -> Image.Image:
        """
        Progress age using Fast-AgingGAN
        
        Args:
            image: Input face image
            target_age_group: "old" for aging, "young" for rejuvenation
            
        Returns:
            Age-progressed image
        """
        if not self.model_loaded:
            self.load_model()
        
        try:
            # Preprocess image
            input_tensor = self.preprocess_image(image)
            
            print(f"Processing image with Fast-AgingGAN for {target_age_group} age group...")
            
            # Generate aged face
            with torch.no_grad():
                aged_tensor = self.model(input_tensor)
            
            # Postprocess result
            result_image = self.postprocess_image(aged_tensor)
            
            print("Fast-AgingGAN processing completed successfully!")
            return result_image
            
        except Exception as e:
            print(f"Error in Fast-AgingGAN processing: {e}")
            raise
    
    def is_available(self) -> bool:
        """Check if the model is available and loaded"""
        return self.model_loaded and self.model is not None
    
    def get_model_info(self) -> dict:
        """Get model information"""
        return {
            'model_name': 'Fast-AgingGAN',
            'model_type': 'CycleGAN-based Age Progression',
            'device': str(self.device),
            'input_size': '512x512',
            'output_size': '512x512',
            'loaded': self.model_loaded,
            'description': 'High-quality GAN-based age transformation with realistic results'
        }


# Global model instance
fast_aging_gan = None

def get_fast_aging_gan():
    """Get or initialize the Fast-AgingGAN model"""
    global fast_aging_gan
    if fast_aging_gan is None:
        fast_aging_gan = FastAgingGAN()
    return fast_aging_gan

def test_fast_aging_gan():
    """Test the Fast-AgingGAN model"""
    try:
        print("Testing Fast-AgingGAN...")
        
        # Create test image
        test_image = Image.new('RGB', (512, 512), color='lightblue')
        
        # Get model
        gan = get_fast_aging_gan()
        
        # Test aging
        aged_image = gan.progress_age(test_image, "old")
        
        print("Fast-AgingGAN test completed successfully!")
        print(f"Model info: {gan.get_model_info()}")
        
        return True
        
    except Exception as e:
        print(f"Fast-AgingGAN test failed: {e}")
        return False

if __name__ == "__main__":
    test_fast_aging_gan()
