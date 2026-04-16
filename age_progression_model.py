import torch
import torch.nn as nn
import torchvision.transforms as transforms
from PIL import Image
import numpy as np
import cv2
import os
from typing import Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

# Import Fast-AgingGAN for realistic aging
try:
    from fast_aging_gan import get_fast_aging_gan
    FAST_AGING_GAN_AVAILABLE = True
    print("Fast-AgingGAN integration available")
except ImportError as e:
    FAST_AGING_GAN_AVAILABLE = False
    print(f"Fast-AgingGAN not available: {e}")
    print("Falling back to traditional image processing")

class AgeProgressionModel:
    """
    AI-based Age Progression Model using GAN architecture
    Implements realistic face aging using deep learning
    """
    
    def __init__(self, model_path: Optional[str] = None):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.fast_gan = None
        self.transform = transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
        ])
        
        # Age group mappings
        self.age_groups = {
            'child': (0, 12),
            'teenager': (13, 19),
            'young_adult': (20, 35),
            'middle_aged': (36, 50),
            'senior': (51, 70),
            'elderly': (71, 100)
        }
        
        # Initialize Fast-AgingGAN if available
        if FAST_AGING_GAN_AVAILABLE:
            try:
                self.fast_gan = get_fast_aging_gan()
                # Auto-load the model
                if not self.fast_gan.is_available():
                    self.fast_gan.load_model()
                print("Fast-AgingGAN initialized and loaded for realistic aging")
            except Exception as e:
                print(f"Failed to initialize Fast-AgingGAN: {e}")
                self.fast_gan = None
        
        # Initialize fallback model
        self._load_model(model_path)
    
    def _load_model(self, model_path: Optional[str] = None):
        """Load the age progression model"""
        try:
            # For demonstration, we'll use a simplified approach
            # In production, you would load a pre-trained GAN model
            # such as SAM (Style-based Age Manipulation) or similar
            
            # Create a simple encoder-decoder architecture for age progression
            self.model = AgeProgressionGAN()
            self.model.to(self.device)
            
            # Load pre-trained weights if available
            if model_path and os.path.exists(model_path):
                checkpoint = torch.load(model_path, map_location=self.device)
                self.model.load_state_dict(checkpoint)
                print(f"Loaded pre-trained model from {model_path}")
            else:
                print("Using initialized model (for demonstration)")
                
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model = None
    
    def preprocess_image(self, image: Image.Image) -> torch.Tensor:
        """Preprocess input image for the model"""
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Apply transforms
        tensor = self.transform(image).unsqueeze(0)
        return tensor.to(self.device)
    
    def postprocess_image(self, tensor: torch.Tensor) -> Image.Image:
        """Convert model output back to PIL Image"""
        # Denormalize
        tensor = tensor.squeeze(0).cpu()
        tensor = tensor * 0.5 + 0.5
        tensor = torch.clamp(tensor, 0, 1)
        
        # Convert to PIL
        transform = transforms.ToPILImage()
        return transform(tensor)
    
    def estimate_current_age(self, image: Image.Image) -> int:
        """
        Estimate current age from face image
        This is a simplified estimation - in production, use a proper age estimation model
        """
        # Simplified age estimation based on facial features
        # In production, use models like DeepFace's age estimation
        
        # Convert to numpy for analysis
        img_array = np.array(image)
        
        # Simple heuristic-based age estimation
        # This is just for demonstration - replace with proper model
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Calculate skin texture variance (simplified)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Estimate age based on skin texture (very rough approximation)
        if laplacian_var > 500:
            estimated_age = np.random.randint(35, 65)
        elif laplacian_var > 200:
            estimated_age = np.random.randint(20, 40)
        else:
            estimated_age = np.random.randint(5, 25)
        
        return estimated_age
    
    def get_age_condition(self, current_age: int, target_age: int) -> torch.Tensor:
        """Generate age conditioning vector for the model"""
        # Create age embedding
        age_diff = target_age - current_age
        
        # Normalize age difference to [-1, 1]
        normalized_diff = np.clip(age_diff / 50.0, -1, 1)
        
        # Create age condition tensor
        age_condition = torch.tensor([normalized_diff], dtype=torch.float32)
        age_condition = age_condition.unsqueeze(0).to(self.device)
        
        return age_condition
    
    def progress_age(self, image: Image.Image, years: int) -> Image.Image:
        """
        Progress face age by specified number of years
        
        Args:
            image: Input face image
            years: Number of years to age (positive for aging, negative for rejuvenation)
            
        Returns:
            Age-progressed image
        """
        # Try Fast-AgingGAN first for realistic results
        if self.fast_gan and self.fast_gan.is_available():
            try:
                print("Using Fast-AgingGAN for realistic age progression...")
                
                # Resize image to 512x512 for Fast-AgingGAN
                image_512 = image.resize((512, 512), Image.Resampling.LANCZOS)
                
                # Determine target age group
                if years > 0:
                    target_age_group = "old"
                    print(f"Aging by {years} years using Fast-AgingGAN...")
                else:
                    target_age_group = "young"
                    print(f"Rejuvenating by {abs(years)} years using Fast-AgingGAN...")
                
                # Use Fast-AgingGAN
                aged_image = self.fast_gan.progress_age(image_512, target_age_group)
                
                # Resize back to original size if needed
                if aged_image.size != image.size:
                    aged_image = aged_image.resize(image.size, Image.Resampling.LANCZOS)
                
                print("Fast-AgingGAN processing completed successfully!")
                return aged_image
                
            except Exception as e:
                print(f"Fast-AgingGAN failed: {e}")
                print("Falling back to enhanced image processing...")
        
        # Fallback to enhanced image processing
        print("Using enhanced image processing for age progression...")
        return self._fallback_age_progression(image, years)
    
    def _enhance_realism(self, image: Image.Image, years: int) -> Image.Image:
        """Apply post-processing to enhance realism"""
        img_array = np.array(image)
        
        # Apply subtle skin texture changes
        if years > 0:
            # Aging effects
            # Reduce skin smoothness
            kernel = np.ones((3,3), np.float32) / 9
            img_array = cv2.filter2D(img_array, -1, kernel)
            
            # Add subtle skin texture
            noise = np.random.normal(0, min(years/2, 10), img_array.shape).astype(np.int16)
            img_array = np.clip(img_array.astype(np.int16) + noise, 0, 255).astype(np.uint8)
            
            # Slight color shift for aging
            if years > 10:
                # Add slight yellowish tint
                img_array[:, :, 0] = np.clip(img_array[:, :, 0] - years//4, 0, 255)  # Reduce blue
                img_array[:, :, 1] = np.clip(img_array[:, :, 1] - years//8, 0, 255)  # Reduce green
                img_array[:, :, 2] = np.clip(img_array[:, :, 2] + years//6, 0, 255)  # Increase red
        
        return Image.fromarray(img_array)
    
    def _fallback_age_progression(self, image: Image.Image, years: int) -> Image.Image:
        """Enhanced fallback method with visible aging effects"""
        # Convert to numpy array for processing
        img_array = np.array(image)
        height, width = img_array.shape[:2]
        
        # Calculate age ratio for more pronounced effects
        age_ratio = min(abs(years) / 20.0, 2.0)  # More aggressive aging
        
        print(f"Age ratio: {age_ratio:.2f} for {years} years")
        
        if years > 0:  # Aging
            # More pronounced skin texture changes
            img_array = cv2.convertScaleAbs(img_array, alpha=1.0 - (age_ratio * 0.15), beta=0)
            
            # Add significant wrinkles and texture
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            # Create strong wrinkle patterns
            if age_ratio > 0.1:
                # Apply edge enhancement for prominent wrinkle simulation
                edges = cv2.Canny(gray, 30, 100)
                edges = cv2.GaussianBlur(edges, (3, 3), 0)  # Fixed: odd kernel size
                edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
                
                # Blend edges more prominently
                img_array = cv2.addWeighted(img_array, 1.0, edges_colored, age_ratio * 0.3, 0)
                
                # Add horizontal forehead wrinkles
                for i in range(int(age_ratio * 5)):
                    y = height//4 + i * 3
                    cv2.line(img_array, (width//4, y), (3*width//4, y), 
                            (50, 40, 30), 1)
                
                # Add crow's feet around eyes
                eye_y, eye_x = height//3, width//3
                for angle in range(0, 360, 45):
                    end_x = int(eye_x + 20 * np.cos(np.radians(angle)))
                    end_y = int(eye_y + 20 * np.sin(np.radians(angle)))
                    cv2.line(img_array, (eye_x, eye_y), (end_x, end_y), 
                            (60, 50, 40), 1)
                
                # Add smile lines
                smile_y = 2*height//3
                cv2.line(img_array, (width//3, smile_y), (width//2, smile_y + 20), 
                        (70, 60, 50), 2)
                cv2.line(img_array, (2*width//3, smile_y), (width//2, smile_y + 20), 
                        (70, 60, 50), 2)
            
            # Significant color changes for aging
            if age_ratio > 0.1:
                # Strong warm tone adjustment
                hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
                hsv[:, :, 0] = np.clip(hsv[:, :, 0] + age_ratio * 5, 0, 180)  # Hue shift
                hsv[:, :, 1] = np.clip(hsv[:, :, 1] - age_ratio * 15, 0, 255)  # Reduce saturation
                hsv[:, :, 2] = np.clip(hsv[:, :, 2] - age_ratio * 20, 0, 255)  # Darkening
                img_array = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
            
            # Add prominent age spots
            if age_ratio > 0.3:
                num_spots = int(25 * age_ratio)
                for _ in range(num_spots):
                    x = np.random.randint(width//6, 5*width//6)
                    y = np.random.randint(height//6, 5*height//6)
                    radius = np.random.randint(2, 6)
                    
                    # Create prominent age spot
                    color = (
                        np.random.randint(40, 80),   # R
                        np.random.randint(25, 55),   # G  
                        np.random.randint(15, 45)    # B
                    )
                    overlay = img_array.copy()
                    cv2.circle(overlay, (x, y), radius, color, -1)
                    cv2.addWeighted(overlay, 0.6, img_array, 0.4, 0, img_array)
            
            # Add gray hair effect
            if age_ratio > 0.5:
                # Create hair region mask (top portion of image)
                hair_mask = np.zeros(img_array.shape[:2], dtype=np.uint8)
                cv2.ellipse(hair_mask, (width//2, height//6), (width//3, height//8), 0, 0, 360, 255, -1)
                
                # Add gray/white to hair region
                gray_hair = np.ones_like(img_array) * 200
                # Apply mask manually since addWeighted doesn't support mask parameter
                masked_original = cv2.bitwise_and(img_array, img_array, mask=cv2.bitwise_not(hair_mask))
                masked_gray = cv2.bitwise_and(gray_hair, gray_hair, mask=hair_mask)
                img_array = cv2.add(masked_original, masked_gray)
                
        else:  # Rejuvenation
            # Stronger reverse aging effects
            img_array = cv2.convertScaleAbs(img_array, alpha=1.0 + (age_ratio * 0.1), beta=10)
            
            # Strong skin smoothing
            img_array = cv2.bilateralFilter(img_array, 15, 80, 80)
            
            # Brighten significantly for youthful look
            if age_ratio > 0.1:
                hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
                hsv[:, :, 1] = np.clip(hsv[:, :, 1] + age_ratio * 20, 0, 255)  # More saturation
                hsv[:, :, 2] = np.clip(hsv[:, :, 2] + age_ratio * 25, 0, 255)  # More brightness
                img_array = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
            
            # Remove wrinkles (strong smoothing)
            img_array = cv2.GaussianBlur(img_array, (5, 5), 0)  # Fixed: odd kernel size
            
            # Brighten eye area significantly
            mask = np.zeros(img_array.shape[:2], dtype=np.uint8)
            cv2.ellipse(mask, (width//2, height//3), (width//4, height//6), 0, 0, 360, 255, -1)
            img_array = cv2.add(img_array, np.ones_like(img_array) * 20, mask=mask)
        
        return Image.fromarray(img_array)


class AgeProgressionGAN(nn.Module):
    """
    Simplified GAN architecture for age progression
    In production, replace with a proper pre-trained model
    """
    
    def __init__(self):
        super().__init__()
        
        # Encoder
        self.encoder = nn.Sequential(
            nn.Conv2d(3, 64, 4, 2, 1),  # 128x128
            nn.LeakyReLU(0.2, inplace=True),
            nn.Conv2d(64, 128, 4, 2, 1),  # 64x64
            nn.BatchNorm2d(128),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Conv2d(128, 256, 4, 2, 1),  # 32x32
            nn.BatchNorm2d(256),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Conv2d(256, 512, 4, 2, 1),  # 16x16
            nn.BatchNorm2d(512),
            nn.LeakyReLU(0.2, inplace=True),
        )
        
        # Age conditioning layer
        self.age_fc = nn.Linear(1, 512)
        
        # Decoder
        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(1024, 256, 4, 2, 1),  # 32x32
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.ConvTranspose2d(256, 128, 4, 2, 1),  # 64x64
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.ConvTranspose2d(128, 64, 4, 2, 1),  # 128x128
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.ConvTranspose2d(64, 3, 4, 2, 1),  # 256x256
            nn.Tanh()
        )
    
    def forward(self, x, age_condition):
        # Encode
        encoded = self.encoder(x)
        
        # Apply age conditioning
        age_feat = self.age_fc(age_condition).unsqueeze(-1).unsqueeze(-1)
        age_feat = age_feat.expand(-1, -1, encoded.size(2), encoded.size(3))
        
        # Concatenate age features
        conditioned = torch.cat([encoded, age_feat], dim=1)
        
        # Decode
        output = self.decoder(conditioned)
        
        return output


# Global model instance
age_model = None

def get_age_model():
    """Get or initialize the age progression model"""
    global age_model
    if age_model is None:
        age_model = AgeProgressionModel()
    return age_model
