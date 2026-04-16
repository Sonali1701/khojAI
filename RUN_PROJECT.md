# How to Run KhojAI Project

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git (optional, for cloning)

## 📋 Step-by-Step Instructions

### 1. **Install Dependencies**
```bash
# Navigate to project directory
cd C:\Users\vs510\PycharmProjects\KhojAI

# Install all required packages
pip install -r requirements.txt
```

### 2. **Run the Application**
```bash
# Start the Flask application
python app.py
```

### 3. **Access the Application**
Open your web browser and go to:
```
http://localhost:5000
```

## 🌐 Available Routes

| Route | Description |
|-------|-------------|
| `/` | Home page - Recent records and overview |
| `/upload` | Upload missing/found person reports |
| `/search` | Face matching between missing and found persons |
| `/simulate` | **AI Age Progression** - Upload photo to see aged appearance |
| `/admin` | Admin dashboard (username: admin, password: admin123) |
| `/about` | About the project |

## 🎯 Key Features to Try

### 1. **AI Age Progression** (NEW!)
- Go to `/simulate`
- Upload a face photo
- Enter number of years to age (e.g., 10, 20, 30)
- See AI-generated age progression

### 2. **Face Recognition**
- Upload missing person reports at `/upload`
- Upload found person reports
- Use `/search` to find matches

### 3. **Admin Dashboard**
- Access at `/admin`
- Login: username=`admin`, password=`admin123`
- View all records and manage data

## 🔧 Troubleshooting

### Common Issues

#### 1. **ModuleNotFoundError**
```bash
# Solution: Install missing dependencies
pip install -r requirements.txt
```

#### 2. **Port Already in Use**
```bash
# Solution: Kill existing process or change port
# On Windows:
netstat -ano | findstr :5000
taskkill /PID <PID_NUMBER> /F

# Or run on different port:
python app.py  # Then modify app.py to use different port
```

#### 3. **TensorFlow/CUDA Errors**
```bash
# The app will work on CPU, but for GPU acceleration:
# Install CUDA toolkit (optional)
pip install tensorflow-gpu  # If you have NVIDIA GPU
```

#### 4. **Permission Errors**
```bash
# Run as administrator or check folder permissions
# Make sure uploads/ folders exist and are writable
```

## 📁 Project Structure
```
KhojAI/
├── app.py                    # Main Flask application
├── requirements.txt           # Python dependencies
├── age_progression_model.py  # AI age progression model
├── data/
│   └── records.json         # Database of person records
├── static/
│   ├── uploads/             # Uploaded images
│   ├── found/               # Found person photos
│   └── missing/             # Missing person photos
├── templates/               # HTML templates
└── docs/                   # Documentation
```

## 🧪 Testing the Age Progression

### Quick Test
```bash
# Test the AI model directly
python -c "
from age_progression_model import get_age_model
from PIL import Image
model = get_age_model()
img = Image.new('RGB', (256, 256), 'blue')
result = model.progress_age(img, 10)
print('✅ Age progression working!')
"
```

### Test via Web Interface
1. Start the application: `python app.py`
2. Open browser to `http://localhost:5000/simulate`
3. Upload any face photo
4. Enter years to age (try 10, 20, 30)
5. Click "Simulate Age Progression"

## 📱 Mobile Access

### Access from Other Devices
1. Find your computer's IP address:
   ```bash
   ipconfig  # On Windows
   ```
2. Allow Flask to accept external connections:
   ```python
   # In app.py, change the last line to:
   app.run(host='0.0.0.0', port=5000, debug=True)
   ```
3. Access from mobile: `http://YOUR_IP:5000`

## 🔒 Security Notes

### Production Deployment
- Change the secret key in `app.py`
- Use proper database instead of JSON
- Implement proper authentication
- Use HTTPS in production

### Current Limitations
- Simple admin authentication (admin/admin123)
- JSON-based storage (not for production)
- No user registration system

## 🚀 Advanced Options

### Running with Different Python Versions
```bash
# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt
python app.py
```

### Development Mode
```bash
# Run with debug mode for development
python app.py  # Already runs in debug mode by default
```

### GPU Acceleration (Optional)
```bash
# If you have NVIDIA GPU and CUDA installed
pip install tensorflow-gpu
# The app will automatically use GPU if available
```

## 📞 Getting Help

### If Something Goes Wrong
1. Check the console output for error messages
2. Ensure all dependencies are installed
3. Verify Python version (3.8+)
4. Check that required folders exist

### Common Error Messages
- `"ModuleNotFoundError"` → Install requirements
- `"Permission denied"` → Run as admin or check permissions
- `"Address already in use"` → Kill existing process or change port

## 🎉 Success Indicators

### You know it's working when:
1. ✅ No error messages when running `python app.py`
2. ✅ Server starts on `http://127.0.0.1:5000`
3. ✅ Home page loads in browser
4. ✅ Age progression processes images without errors
5. ✅ Upload functionality works

---

**🚀 Ready to go! Start with `python app.py` and visit `http://localhost:5000`**
