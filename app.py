from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os
from model import predict_skin_disease  # Import the prediction function from your model
from flask_wtf import FlaskForm
from wtforms import SubmitField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from chat import chat_bp  # Assuming chat.py contains your chat blueprint

# Setup the Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Use a more secure secret key in production
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit file upload size to 16MB

# Allowed image file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Check if the upload folder exists, create it if not
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Form for file upload
class UploadForm(FlaskForm):
    file = FileField('Upload Skin Image', validators=[
        FileRequired(),
        FileAllowed(ALLOWED_EXTENSIONS, 'Only image files are allowed!')
    ])
    submit = SubmitField('Submit')

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route for the main page
# Route for the main page
@app.route('/', methods=['GET', 'POST'])
def index():
    form = UploadForm()
    res = None
    spread_intensity = None  # Renamed from confidence

    if form.validate_on_submit():
        file = form.file.data
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Predict using your model (ensure predict_skin_disease function returns result and confidence)
        try:
            res, confidence = predict_skin_disease(filepath)
            spread_intensity = confidence  # Assign confidence to new name
        except Exception as e:
            res = f"Error during prediction: {str(e)}"
            spread_intensity = None

    return render_template('index.html', form=form, res=res, spread_intensity=spread_intensity)


# Register the chat blueprint (assuming you have it correctly defined in chat.py)
app.register_blueprint(chat_bp, url_prefix='/chat')

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
