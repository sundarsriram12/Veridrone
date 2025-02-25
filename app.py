from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
import os
import csv
from datetime import datetime
from werkzeug.utils import secure_filename
from classifier import img_classify

app = Flask(__name__)
app.secret_key = 'your_secret_key'
UPLOAD_FOLDER = 'uploads'
CSV_FILE = 'image_data.csv'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Image Name', 'Uploaded Date', 'Classify Status', 'Number of Persons', 'Missing Hardhat', 'Missing PPE'])

# Dummy credentials for login
VALID_USERS = {'admin': 'pass123'}

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in VALID_USERS and VALID_USERS[username] == password:
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid Credentials!')
    return render_template('login.html')

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

#send email with attachment
def send_email_with_attachment(sender_email, sender_password, recipient_email, subject, body, attachment_path):
    # Set up the MIME
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = subject

    # Attach the message body
    message.attach(MIMEText(body, 'plain'))

    # Attach the image
    if attachment_path and os.path.isfile(attachment_path):
        with open(attachment_path, 'rb') as attachment_file:
            mime_base = MIMEBase('application', 'octet-stream')
            mime_base.set_payload(attachment_file.read())
            encoders.encode_base64(mime_base)
            mime_base.add_header(
                'Content-Disposition',
                f'attachment; filename={os.path.basename(attachment_path)}'
            )
            message.attach(mime_base)

    try:
        # Connect to Gmail's SMTP server
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, sender_password)
            server.send_message(message)
            print("Email with attachment sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")



@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'image' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['image']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            with open(CSV_FILE, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([filename, datetime.now(), 'No', '0', 'No', 'No'])
            flash('Image successfully uploaded')
            return redirect(url_for('upload'))
    return render_template('upload.html')

@app.route('/classify')
def classify():
    new_images = []
    classified_images = []
    with open(CSV_FILE, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['Classify Status'] == 'No':
                new_images.append(row)
            else:
                classified_images.append(row)
    return render_template('classify.html', new_images=new_images, classified_images=classified_images)

# Route to handle image classification
@app.route('/classify_image/<image_name>', methods=['POST'])
def classify_image(image_name):
    # Simulated classification results
    print(f"image_name={image_name}")
    number_of_persons = 2  # Example
    missing_hardhat = 'Yes'
    missing_ppe = 'No'
    classified_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Update CSV file
    updated_rows = []
    with open(CSV_FILE, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['Image Name'] == image_name:
                print("image available in csv")
                number_of_persons, missing_hardhat, missing_ppe, filename = img_classify.predict(image_name)
                row['Classify Status'] = 'Yes'
                row['Number of Persons'] = number_of_persons
                row['Missing Hardhat'] = missing_hardhat
                row['Missing PPE'] = missing_ppe
                row['Classified Image'] = filename
            updated_rows.append(row)
    
    # Write back the updated rows
    with open(CSV_FILE, 'w', newline='') as file:
        fieldnames = ['Image Name', 'Uploaded Date', 'Classify Status', 'Number of Persons', 'Missing Hardhat', 'Missing PPE', 'Classified Image']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(updated_rows)
    
    return redirect(url_for('classify'))

# Route to handle send email
@app.route('/send_email/<image_name>', methods=['GET'])
def send_email(image_name):
    # Simulated classification results
    print(f"send_email image_name={image_name}")
    number_of_persons = 2  # Example
    missing_hardhat = 'Yes'
    missing_ppe = 'No'
    classified_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Update CSV file
    updated_rows = []
    with open(CSV_FILE, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['Image Name'] == image_name:
                print(f"image available in csv={row['Classified Image']}")
                send_email_with_attachment(
                    sender_email='veridrone6@gmail.com',
                    sender_password='mexe ynte cqpg ynil',  # Use App Password if 2FA is enabled
                    recipient_email='skavitha2076@gmail.com',
                    subject='Veridrone Alert',
                    body='Veridrone alert is detected. Person(s) are not following safety rules.',
                    attachment_path=f"{row['Classified Image']}"
                )
    return redirect(url_for('classify'))


@app.route('/reports')
def reports():
    # You can integrate charts here using libraries like Chart.js or Plotly
    return render_template('reports.html')

@app.route('/report-data')
def report_data():
    new_images = []
    classified_images = []
    with open(CSV_FILE, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['Classify Status'] == 'No':
                new_images.append(row)
            else:
                classified_images.append(row)

    # Data to send as JSON
    data = {
        'classified': len(classified_images),
        'unclassified': len(new_images),
        'person_counts': 5,
        'missing_hardhat': 10,
        'hardhat_present': 5,
        'missing_ppe': 5,
        'ppe_present': 5,
        'hardhat_violations': 10,
        'ppe_violations': 5,
        'image_names': [row['Image Name'] for row in classified_images]  # Assuming 'Image Name' exists
    }

    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
