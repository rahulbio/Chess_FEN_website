import os
from flask import Flask, render_template, request, redirect, url_for, flash
import cv2
import numpy as np
from utils.image_processing import preprocess_image, display_with_predicted_fen
from tensorflow.keras.models import load_model
from werkzeug.utils import secure_filename
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Set the upload folder for user-uploaded images
UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load model at startup
MODEL_PATH = 'model.h5'  # Update this to your actual model path
try:
    model = load_model(r"E:\Interview_Prep\Chess_Website\chess_model.h5")
    logger.info("Model loaded successfully")
except Exception as e:
    logger.error(f"Error loading model: {str(e)}")
    model = None

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        logger.debug("Processing POST request")
        
        # Check if the post request has the file part
        if 'file' not in request.files:
            logger.warning("No file part in request")
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['file']
        
        # If user does not select file, browser also submit an empty part without filename
        if file.filename == '':
            logger.warning("No selected file")
            flash('No selected file')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            try:
                logger.debug(f"Processing file: {file.filename}")
                
                # Secure the filename
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                # Save the file
                logger.debug(f"Saving file to: {filepath}")
                file.save(filepath)
                
                # Check if file was saved successfully
                if not os.path.exists(filepath):
                    logger.error(f"File was not saved successfully: {filepath}")
                    flash('Error saving file')
                    return redirect(request.url)
                
                # Check if model is loaded
                if model is None:
                    logger.error("Model not loaded")
                    flash('Model not loaded properly')
                    return redirect(request.url)
                
                # Process image
                logger.debug("Processing image with model")
                predicted_fen = display_with_predicted_fen(filepath, model)
                
                logger.info(f"Successfully processed image. FEN: {predicted_fen}")
                return render_template('result.html', 
                                    predicted_fen=predicted_fen,
                                    image_path=os.path.join('uploads', filename))
                                    
            except Exception as e:
                logger.error(f"Error processing image: {str(e)}", exc_info=True)
                flash(f'Error processing image: {str(e)}')
                return redirect(request.url)
        else:
            logger.warning(f"Invalid file type: {file.filename}")
            flash('Invalid file type. Please upload a PNG, JPG, or JPEG file.')
            return redirect(request.url)
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)