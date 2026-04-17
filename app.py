import os
import json
import time
import numpy as np
import cv2
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageOps
try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
except ImportError:
    DEEPFACE_AVAILABLE = False
    print("DeepFace not available - using fallback face detection")
try:
    import tensorflow as tf
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    print("TensorFlow not available - some features may be limited")
import random
from age_progression_model import get_age_model
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure TensorFlow to use GPU if available
if TENSORFLOW_AVAILABLE:
    gpus = tf.config.experimental.list_physical_devices('GPU')
    if gpus:
        try:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
        except RuntimeError as e:
            print(e)

app = Flask(__name__)

# Production configuration
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Configure upload folders for Render
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', '/tmp/uploads')
app.config['FOUND_FOLDER'] = os.path.join(app.config['UPLOAD_FOLDER'], 'found')
app.config['MISSING_FOLDER'] = os.path.join(app.config['UPLOAD_FOLDER'], 'missing')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB max upload

# Production settings
app.config['DEBUG'] = os.getenv('FLASK_ENV', 'development') == 'development'
app.config['TESTING'] = False

# Create necessary directories
for folder in [app.config['UPLOAD_FOLDER'], app.config['FOUND_FOLDER'], app.config['MISSING_FOLDER']]:
    os.makedirs(folder, exist_ok=True)

# Add datetime filter
def format_datetime(value, format='%Y-%m-%d %H:%M:%S'):
    """Format a date time to (Default): d Mon YYYY HH:MM P"""
    if value is None:
        return ""
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return value
    return value.strftime(format)

# Register the datetime filter after the function is defined
app.jinja_env.filters['datetimeformat'] = format_datetime

app.jinja_env.filters['datetimeformat'] = format_datetime

# Add context processor for 'now'
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
DATA_FILE = 'data/records.json'
os.makedirs('data', exist_ok=True)

# Initialize data file if it doesn't exist
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump([], f)

def save_record(record):
    """Save a new record to the JSON file"""
    records = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            records = json.load(f)
    
    # Add ID and timestamp
    record['id'] = len(records) + 1
    record['created_at'] = datetime.now().isoformat()
    records.append(record)
    
    with open(DATA_FILE, 'w') as f:
        json.dump(records, f, indent=2)
    
    return record

def get_all_records():
    """Get all records from the JSON file"""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def generate_embedding(image_path):
    """Simulate generating face embeddings"""
    # In a real app, this would use a model like ArcFace
    # For now, return a random vector
    return np.random.rand(512).tolist()

def cosine_similarity(a, b):
    """Calculate cosine similarity between two vectors"""
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# Add this function before your routes
def format_datetime(value, format='%Y-%m-%d %H:%M:%S'):
    """Format a date time to (Default): d Mon YYYY HH:MM P"""
    if value is None:
        return ""
    if isinstance(value, str):
        # If the value is a string, try to parse it to a datetime object
        try:
            value = datetime.fromisoformat(value.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return value
    return value.strftime(format)
@app.route('/')
def index():
    """Home page"""
    # Get 3 most recent records for the home page
    records = get_all_records()[-3:]
    return render_template('index.html', recent_records=reversed(records))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """Handle file uploads"""
    if request.method == 'POST':
        if 'photo' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['photo']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        if file:
            # Get report type (missing or found)
            report_type = request.form.get('type', 'missing')
            
            # Determine the target directory based on report type
            target_folder = app.config['MISSING_FOLDER'] if report_type == 'missing' else app.config['FOUND_FOLDER']
            
            # Create a secure filename with person's name and timestamp
            name = request.form.get('name', 'unknown').lower().replace(' ', '_')
            age = request.form.get('age', '0')
            gender = request.form.get('gender', 'unknown').lower()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Get file extension
            file_ext = os.path.splitext(file.filename)[1].lower()
            
            # Create new filename: name_age_gender_timestamp.ext
            new_filename = f"{name}_{age}_{gender}_{timestamp}{file_ext}"
            new_filepath = os.path.join(target_folder, new_filename)
            
            # Save the uploaded file to the appropriate folder
            file.save(new_filepath)
            
            # Generate embedding
            embedding = generate_embedding(new_filepath)
            
            # Save record
            record = {
                'name': request.form.get('name', 'Unknown'),
                'gender': request.form.get('gender', 'Unknown'),
                'age': int(request.form.get('age', 0)),
                'location': request.form.get('location', 'Unknown'),
                'contact': request.form.get('contact', ''),
                'photo_path': f"{report_type}/{new_filename}",  # Store relative path
                'embedding': embedding,
                'type': report_type,
                'created_at': datetime.now().isoformat()
            }
            
            save_record(record)
            flash('Record uploaded successfully!', 'success')
            return redirect(url_for('index'))
    
    return render_template('upload.html')

# No need to initialize face_cascade as we'll use DeepFace's built-in detectors

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Serve uploaded files from the appropriate folder"""
    # Check if the file exists in the upload folder first
    if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    
    # If not found, check in the missing or found folders
    if os.path.exists(os.path.join(app.config['MISSING_FOLDER'], filename)):
        return send_from_directory(app.config['MISSING_FOLDER'], filename)
    elif os.path.exists(os.path.join(app.config['FOUND_FOLDER'], filename)):
        return send_from_directory(app.config['FOUND_FOLDER'], filename)
    
    # If file not found anywhere, return 404
    return "File not found", 404

@app.route('/get_record_details', methods=['POST'])
def get_record_details():
    """Get the complete details for a record by image filename"""
    try:
        data = request.get_json()
        if not data or 'image_path' not in data:
            return jsonify({'success': False, 'error': 'Missing image path'}), 400

        # Get the filename and clean it up (remove any URL parameters or fragments)
        filename = data['image_path'].split('?')[0].split('#')[0]
        filename = os.path.basename(filename)  # Ensure we only have the filename
        
        print(f"Looking up record for filename: {filename}")
        
        records = get_all_records()
        print(f"Total records to search: {len(records)}")
        
        # Find the record with matching filename
        for record in records:
            # Get the photo path and normalize it
            record_path = record.get('photo_path', '')
            
            # Handle both cases: with or without 'found/' or 'missing/' prefix
            record_filename = os.path.basename(record_path)
            record_path_without_prefix = record_path.replace('found/', '').replace('missing/', '')
            
            # Debug output
            print(f"Checking record: {record_path} (filename: {record_filename}) == {filename}? {record_filename == filename or record_path == filename or record_path_without_prefix == filename}")
            
            if record_filename == filename or record_path == filename or record_path_without_prefix == filename:
                print(f"Found matching record: {record}")
                return jsonify({
                    'success': True,
                    'record': record
                })
        
        print(f"No record found for filename: {filename}")
        return jsonify({
            'success': False,
            'error': 'Record not found',
            'searched_filename': filename,
            'available_records': [os.path.basename(r.get('photo_path', '')) for r in records]
        }), 404
        
    except Exception as e:
        error_msg = f"Error getting record details: {str(e)}"
        print(error_msg)
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500

@app.route('/search', methods=['GET', 'POST'])
def search():
    """Search for matching faces between missing and found persons"""
    if request.method == 'POST':
        if 'photo' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
            
        file = request.files['photo']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
            
        try:
            # Get search type (look for missing or found persons)
            # When searching for missing persons, we look in the 'found' folder and vice versa
            search_type = request.form.get('search_type', 'found')  # Default to searching in 'found' folder
            
            # Determine the target directory to search in
            # If the search type is 'missing', it means we're looking for this person in the 'found' folder
            search_folder = app.config['FOUND_FOLDER'] if search_type == 'missing' else app.config['MISSING_FOLDER']
            
            print(f"Search type: {search_type}")
            print(f"Searching in folder: {search_folder}")
            print(f"This means we're looking for a {search_type} person in the {os.path.basename(search_folder)} folder")
            
            # Verify search folder exists and is accessible
            if not os.path.exists(search_folder):
                return jsonify({
                    'success': False,
                    'error': f'Search directory not found: {search_folder}'
                }), 500
                
            # List files in search directory for debugging
            current_dir = os.getcwd()
            abs_search_folder = os.path.abspath(search_folder)
            print("\n=== DEBUGGING SEARCH FOLDER ===")
            print(f"Current working directory: {current_dir}")
            print(f"Search folder (relative): {search_folder}")
            print(f"Search folder (absolute): {abs_search_folder}")
            print(f"Folder exists: {os.path.exists(abs_search_folder)}")
            
            if os.path.exists(abs_search_folder):
                print(f"Files in folder: {os.listdir(abs_search_folder)}")
            else:
                print("Search folder does not exist!")
                # Try to create the directory if it doesn't exist
                try:
                    os.makedirs(abs_search_folder, exist_ok=True)
                    print(f"Created directory: {abs_search_folder}")
                except Exception as e:
                    print(f"Error creating directory: {e}")
            print("==============================\n")
            
            # Save the uploaded file temporarily
            temp_filename = secure_filename(file.filename)
            temp_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
            file.save(temp_path)
            
            # Search for matches in the target folder
            matches = []
            image_count = 0
            
            # Get list of image files in search folder (use absolute path)
            try:
                image_files = [f for f in os.listdir(abs_search_folder) 
                             if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            except Exception as e:
                print(f"Error listing directory {abs_search_folder}: {e}")
                return jsonify({
                    'success': False,
                    'error': f'Could not read directory: {abs_search_folder}',
                    'details': str(e)
                }), 500
            
            print(f"Found {len(image_files)} images to compare with")
            
            for found_file in image_files:
                found_path = os.path.join(search_folder, found_file)
                image_count += 1
                
                try:
                    # Skip if comparing the same file
                    if os.path.basename(temp_path) == found_file:
                        print(f"Skipping self-comparison with {found_file}")
                        continue
                        
                    print(f"\nComparing {os.path.basename(temp_path)} with {found_file}...")
                    similarity = compare_faces(temp_path, found_path)
                    print(f"Similarity score: {similarity:.2f}%")
                    
                    # Lower the threshold to 25% to get more potential matches
                    print(f"Comparing with {found_file} - Similarity: {similarity:.2f}%")
                    if similarity >= 25:  # Lowered threshold to 25% for more matches
                        try:
                            # Extract person details from filename (format: name_age_gender_timestamp.ext)
                            name_parts = os.path.splitext(found_file)[0].split('_')
                            
                            # Handle name parts (could contain multiple underscores)
                            if len(name_parts) >= 4:  # At least name, age, gender, timestamp
                                name = ' '.join(part.capitalize() for part in name_parts[:-3])
                                age = name_parts[-3]
                                gender = name_parts[-2].capitalize()
                            else:
                                # Fallback if filename doesn't follow expected format
                                name = os.path.splitext(found_file)[0].replace('_', ' ').title()
                                age = 'Unknown'
                                gender = 'Unknown'
                            
                            print(f"Processed match: {name}, Age: {age}, Gender: {gender}")
                            
                            # Generate the correct URL for the image
                            # Use the filename directly since our uploaded_file route will find it in the right folder
                            image_url = url_for('uploaded_file', filename=found_file)
                            
                            # Create a unique ID for this match
                            match_id = f"{os.path.splitext(found_file)[0]}_{int(time.time())}"
                            
                            match_data = {
                                'id': match_id,  # Use a unique ID based on filename and timestamp
                                'image': image_url,
                                'similarity': round(similarity, 2),
                                'name': name,
                                'age': age,
                                'gender': gender,
                                'type': 'found' if search_type == 'missing' else 'missing',  # Opposite of search type
                                'last_seen': 'Recently',
                                'filename': found_file  # Store the filename for looking up details
                            }
                            
                            print(f"Match found: {match_data}")
                            matches.append(match_data)
                            
                        except Exception as e:
                            print(f"Error processing match for {found_file}: {str(e)}")
                            continue
                            
                    else:
                        print(f"No match: {found_file} (similarity: {similarity:.2f}%)")
                        
                except Exception as e:
                    print(f"Error comparing with {found_file}: {str(e)}")
                    continue
            
            # Sort matches by similarity (highest first)
            matches = sorted(matches, key=lambda x: x['similarity'], reverse=True)
            
            # Clean up temporary file
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception as e:
                    print(f"Error removing temp file: {e}")
            
            # Save the uploaded file to the uploads folder
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
            file.save(upload_path)  # Save the file to the uploads folder
            
            # Generate URL for the uploaded image
            uploaded_image_url = url_for('uploaded_file', filename=temp_filename, _external=True)
            
            # Prepare response with additional debug info
            response_data = {
                'success': True,
                'matches': matches,
                'uploaded_image': uploaded_image_url,
                'search_type': search_type,
                'total_scanned': image_count,
                'match_count': len(matches),
                'search_folder': search_folder,
                'debug_info': {
                    'search_folder_contents': os.listdir(search_folder) if os.path.exists(search_folder) else 'Folder not found',
                    'search_folder_path': os.path.abspath(search_folder),
                    'current_working_directory': os.getcwd(),
                    'file_exists': os.path.exists(os.path.join(search_folder, os.listdir(search_folder)[0])) if os.path.exists(search_folder) and len(os.listdir(search_folder)) > 0 else 'No files in folder'
                }
            }
            
            print(f"\nSearch complete. Scanned {image_count} images. Found {len(matches)} matches.")
            
            return jsonify(response_data)
            
        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return jsonify({'error': str(e)}), 500
            
    return render_template('search.html')

def extract_face_embeddings(image_path):
    """Extract face embeddings using DeepFace with OpenCV backend"""
    try:
        print(f"\nExtracting face embeddings from: {os.path.basename(image_path)}")
        
        # Use OpenCV backend which is the most reliable and doesn't require additional dependencies
        embedding_objs = DeepFace.represent(
            img_path=image_path,
            model_name='Facenet512',
            detector_backend='opencv',
            enforce_detection=True,
            align=True
        )
        
        if not embedding_objs:
            print("No faces detected in the image")
            return None, False
            
        # Get the first face found
        embedding = embedding_objs[0]['embedding']
        print("Successfully extracted face embeddings")
        return np.array(embedding), True
        
    except Exception as e:
        print(f"Error in face embedding extraction: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, False

def compare_faces(img1_path, img2_path, threshold=0.6):
    """
    Compare two face images using DeepFace's verify function
    Returns a similarity score between 0 and 100
    """
    try:
        print(f"\nComparing {os.path.basename(img1_path)} with {os.path.basename(img2_path)}")
        
        # Use DeepFace's verify function which handles face detection and comparison
        result = DeepFace.verify(
            img1_path=img1_path,
            img2_path=img2_path,
            model_name='Facenet512',
            detector_backend='opencv',
            distance_metric='cosine',
            enforce_detection=True,
            align=True
        )
        
        # Get the similarity score (1 - distance)
        similarity_score = 1 - result['distance']
        
        # Convert to percentage (0-100)
        similarity_percent = max(0, min(100, similarity_score * 100))
        
        # Apply threshold-based scaling for better discrimination
        if similarity_percent < threshold * 100:
            # Scale down low similarity scores more aggressively
            similarity_percent = similarity_percent * 0.7
        
        print(f"Face similarity: {similarity_percent:.2f}%")
        return similarity_percent
        
    except Exception as e:
        print(f"Error comparing faces: {str(e)}")
        import traceback
        traceback.print_exc()
        return 0.0
    

@app.route('/simulate', methods=['GET', 'POST'])
def simulate():
    """AI-powered age progression simulation using deep learning models"""
    result_image = None
    
    if request.method == 'POST' and 'photo' in request.files:
        file = request.files['photo']
        if file.filename != '':
            try:
                years = int(request.form.get('years', 10))
                filename = secure_filename(file.filename)
                ext = os.path.splitext(filename)[1].lower()
                timestamp = int(datetime.now().timestamp())
                processed_filename = f"aged_{timestamp}{ext}"
                processed_path = os.path.join(app.config['UPLOAD_FOLDER'], processed_filename)
                temp_path = os.path.join(app.config['UPLOAD_FOLDER'], f'temp_{timestamp}{ext}')
                file.save(temp_path)

                try:
                    # Load the image
                    input_image = Image.open(temp_path)
                    
                    # Get the age progression model
                    age_model = get_age_model()
                    
                    # Perform AI-based age progression
                    print(f"Performing age progression: {years} years...")
                    aged_image = age_model.progress_age(input_image, years)
                    
                    # Verify the result is valid
                    if aged_image is None:
                        raise Exception("Age progression returned None")
                    
                    # Save the processed image
                    aged_image.save(processed_path, 'JPEG' if ext.lower() in ['.jpg', '.jpeg'] else 'PNG', 
                                   quality=95, optimize=True, progressive=True)
                    
                    # Get the URL for the processed image
                    result_image = url_for('static', filename=f'uploads/{processed_filename}')
                    
                    # Prepare response data
                    response_data = {
                        'success': True,
                        'image_path': result_image,
                        'years': years,
                        'model_used': 'Fast-AgingGAN (Realistic GAN-based Age Progression)',
                        'processing_method': 'Advanced CycleGAN model with high-quality realistic aging effects'
                    }
                    
                    # Clean up temporary file
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                    
                    # Handle AJAX requests
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
                        return jsonify(response_data)
                    
                    flash(f'Age progression completed! Image aged by {years} years using realistic GAN model.', 'success')
                    
                except Exception as e:
                    print(f"Error in AI age progression: {str(e)}")
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                    return jsonify({
                        'success': False,
                        'error': f'Error in AI age progression: {str(e)}'
                    }), 400
                
            except Exception as e:
                print(f"Error: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 400
    
    # Handle AJAX error responses
    if request.method == 'POST' and (request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json):
        return jsonify({
            'success': False,
            'error': 'No file was uploaded or an error occurred'
        }), 400

    # Render the template for regular page loads
    return render_template('simulate.html', result_image=result_image)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    """Admin dashboard"""
    # Simple password protection
    if request.method == 'POST':
        if (request.form.get('username') == 'admin' and 
            request.form.get('password') == 'admin123'):
            session['admin_logged_in'] = True
        else:
            flash('Invalid credentials', 'error')
    
    if not session.get('admin_logged_in'):
        return render_template('admin.html')
    
    records = get_all_records()
    return render_template('admin.html', records=records)

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')

if __name__ == '__main__':
    # Production deployment configuration
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    debug = os.getenv('FLASK_ENV', 'development') == 'development'
    
    print(f"Starting Age Progression App on {host}:{port}")
    print(f"Debug mode: {debug}")
    print(f"Upload folder: {app.config['UPLOAD_FOLDER']}")
    
    app.run(host=host, port=port, debug=debug)
