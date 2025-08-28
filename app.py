from flask import Flask, request, jsonify, render_template, Response
from flask_cors import CORS
import numpy as np
import pandas as pd
import joblib
import os
import time
import string
import random
import json
import re

# Initialize the Flask application
app = Flask(__name__)
CORS(app)

# Load the common passwords dataset
passwords_df = pd.read_csv('common_passwords.csv')

# Load the KNN model (if applicable)
try:
    knn_model = joblib.load('knn_model.pkl')
except Exception as e:
    knn_model = None
    print("KNN model not found. Falling back to basic analysis.")

# Helper function to calculate similarity percentage
def calculate_similarity_percentage(input_password, common_passwords):
    from Levenshtein import distance as levenshtein_distance
    distances = []
    for common_password in common_passwords:
        dist = levenshtein_distance(input_password, common_password)
        max_len = max(len(input_password), len(common_password))
        similarity = 100 - ((dist / max_len) * 100)
        distances.append(similarity)
    max_similarity = max(distances) if distances else 0
    similarity_percentage = round(max_similarity, 2)
    return similarity_percentage

# Helper function for password strength analysis
def analyze_password_strength(password):
    # Initialize score
    score = 0
    feedback = []

    # Length check
    if len(password) >= 8:
        score += 20
        feedback.append("Strength: Good length.")
    else:
        feedback.append("Weakness: Password is too short.")

    # Uppercase check
    if any(char.isupper() for char in password):
        score += 15
        feedback.append("Strength: Contains uppercase letters.")
    else:
        feedback.append("Weakness: Add uppercase letters.")

    # Lowercase check
    if any(char.islower() for char in password):
        score += 15
        feedback.append("Strength: Contains lowercase letters.")
    else:
        feedback.append("Weakness: Add lowercase letters.")

    # Digit check
    if any(char.isdigit() for char in password):
        score += 15
        feedback.append("Strength: Contains numbers.")
    else:
        feedback.append("Weakness: Add numbers.")

    # Special character check
    if any(char in string.punctuation for char in password):
        score += 15
        feedback.append("Strength: Contains special characters.")
    else:
        feedback.append("Weakness: Add special characters.")

    # Repetition check
    if len(set(password)) == len(password):
        score += 10
        feedback.append("Strength: No character repetition.")
    else:
        feedback.append("Weakness: Avoid repeating characters.")

    # Sequential characters check
    sequences = [string.ascii_lowercase, string.ascii_uppercase, string.digits]
    sequential = False
    for seq in sequences:
        for i in range(len(seq) - 2):
            seq_fragment = seq[i:i+3]
            if seq_fragment in password or seq_fragment[::-1] in password:
                sequential = True
                break
    if not sequential:
        score += 10
        feedback.append("Strength: No sequential characters.")
    else:
        feedback.append("Weakness: Avoid sequential characters.")

    return score, feedback

# Helper function for social engineering analysis
def analyze_social_engineering(password, personal_info):
    analysis_report = []
    unmatched_characters = list(password)

    password_lower = password.lower()

    # Extract email username
    email = personal_info.get('email address', '').lower().strip()
    email_username = email.split('@')[0] if '@' in email else email

    # Prepare personal info components for checking
    personal_components = {
        'name': personal_info.get('name', '').lower().strip(),
        'email username': email_username,
        'date of birth': personal_info.get('date of birth', '').lower().strip(),
        'location': personal_info.get('location', '').lower().strip(),
        'phone number': personal_info.get('phone number', '').lower().strip(),
    }

    # Analyze each piece of personal information
    for key, value in personal_components.items():
        if value:
            found = False
            # First check if the entire personal info is in the password
            if value in password_lower:
                analysis_report.append(f"Weakness: Password contains your {key}.")
                # Remove matched part from unmatched_characters
                pattern = re.compile(re.escape(value), re.IGNORECASE)
                unmatched_characters = list(pattern.sub('', ''.join(unmatched_characters)))
                found = True
            else:
                # Check for substrings of length 3 or more
                substrings = [value[i:j] for i in range(len(value)) for j in range(i+3, len(value)+1)]
                substrings = list(set(substrings))  # Remove duplicates
                substrings.sort(key=len, reverse=True)  # Check longer substrings first
                substrings_matched = []
                for substr in substrings:
                    if substr in password_lower:
                        analysis_report.append(f"Weakness: Password contains part of your {key} ('{substr}').")
                        # Remove matched part from unmatched_characters
                        pattern = re.compile(re.escape(substr), re.IGNORECASE)
                        unmatched_characters = list(pattern.sub('', ''.join(unmatched_characters)))
                        substrings_matched.append(substr)
                if not found and not substrings_matched:
                    analysis_report.append(f"Strength: Password does not contain your {key}.")
        else:
            analysis_report.append(f"Strength: No {key} provided for analysis.")

    # Calculate unmatched percentage
    unmatched_percentage = (len(unmatched_characters) / len(password)) * 100 if password else 0
    unmatched_percentage = round(unmatched_percentage, 2)

    return unmatched_percentage, analysis_report

# Combined analysis route
@app.route('/analyze_password', methods=['POST'])
def analyze_password():
    data = request.get_json()
    password = data.get('password', '')
    name = data.get('name', '')
    dob = data.get('dob', '')
    location = data.get('location', '')
    phone = data.get('phone', '')
    email = data.get('email', '')

    personal_info = {
        'name': name,
        'date of birth': dob,
        'location': location,
        'phone number': phone,
        'email address': email
    }

    # Initialize response
    response = {}

    # Check if password is empty
    if not password:
        response['error'] = 'Password is required.'
        return jsonify(response), 400

    # Calculate similarity percentage
    common_passwords = passwords_df['password'].tolist()
    similarity_percentage = calculate_similarity_percentage(password, common_passwords)

    # Analyze password strength
    final_score, feedback = analyze_password_strength(password)

    # Check if similarity is 100%
    if similarity_percentage == 100.0:
        final_score = 0  # Set score to 0
        feedback.insert(0, "Weakness: Password is one of the most common passwords.")

    # Analyze social engineering aspects
    unmatched_percentage, analysis_report = analyze_social_engineering(password, personal_info)

    # Combine feedback and analysis report
    combined_feedback = feedback + analysis_report

    # Prepare response
    response['similarity_percentage'] = similarity_percentage
    response['final_score'] = final_score
    response['unmatched_percentage'] = unmatched_percentage
    response['feedback'] = combined_feedback

    return jsonify(response)

# Password generator route
@app.route('/generate_password', methods=['GET'])
def generate_password():
    length = 30
    characters = string.ascii_letters + string.digits + string.punctuation
    generated_password = ''.join(random.choice(characters) for _ in range(length))
    return jsonify({'generated_password': generated_password})

# Enhanced password cracking simulation with detailed character discovery
def brute_force_crack(input_password, time_limit=120, personal_info=None):
    start_time = time.time()
    charset = string.ascii_letters + string.digits + string.punctuation

    password_length = len(input_password)
    found_password = ['_'] * password_length

    # Prepare personal info components
    personal_components = []
    substitutions = {
        'a': ['@', '4'],
        'e': ['3'],
        'i': ['1', '!'],
        'o': ['0'],
        's': ['5', '$'],
        'l': ['1'],
        't': ['7'],
        'b': ['8'],
        'g': ['9'],
        'z': ['2']
    }

    if personal_info:
        # Combine all personal info into one string
        for key in ['name', 'date of birth', 'location', 'phone number', 'email username']:
            value = personal_info.get(key, '')
            if value:
                personal_components.append(value.lower())

    # Simulate character-by-character cracking
    for i in range(password_length):
        current_char = input_password[i]
        char_found = False

        # First, check if the character matches personal info
        for info in personal_components:
            if i < len(info) and current_char.lower() == info[i]:
                found_password[i] = current_char
                yield f"Found character '{current_char}' at position {i+1} via personal info"
                char_found = True
                break

        if not char_found:
            # Check for substitutions in personal info
            for info in personal_components:
                if i < len(info):
                    original_char = info[i]
                    substituted_chars = substitutions.get(original_char.lower(), [])
                    if current_char in substituted_chars:
                        found_password[i] = current_char
                        yield f"Found character '{current_char}' at position {i+1} via substitution of '{original_char}'"
                        char_found = True
                        break

        if not char_found:
            # Brute-force the character
            for char in charset:
                if time.time() - start_time > time_limit:
                    yield "Time limit exceeded. Password could not be found."
                    return
                if char == current_char:
                    found_password[i] = char
                    yield f"Found character '{char}' at position {i+1} via brute-force"
                    char_found = True
                    break

        # Update cracked password progress
        yield f"Cracked so far: {''.join(found_password)}"

    # Final check
    cracked_password = ''.join(found_password)
    if cracked_password == input_password:
        yield f"Password cracked successfully: {cracked_password}"
    else:
        yield "Failed to crack the password within the given time limit."

# Password cracking route
@app.route('/crack_password_stream/<string:input_password>', methods=['GET'])
def crack_password_stream(input_password):
    time_limit = request.args.get('time_limit', default=120, type=int)
    use_personal_info = request.args.get('use_personal_info', default='false') == 'true'

    personal_info = {}
    if use_personal_info:
        personal_info['name'] = request.args.get('full_name', '')
        personal_info['date of birth'] = request.args.get('dob', '')
        personal_info['location'] = request.args.get('location', '')
        personal_info['phone number'] = request.args.get('phone', '')
        email = request.args.get('email', '')
        email_username = email.split('@')[0] if '@' in email else email
        personal_info['email username'] = email_username

    def generate_cracking_stream():
        # Start the enhanced brute-force cracking simulation
        for message in brute_force_crack(input_password, time_limit=time_limit, personal_info=personal_info):
            yield f"data: {message}\n\n"

    return Response(generate_cracking_stream(), content_type='text/event-stream')

# Route to render the main HTML page
@app.route('/')
def index():
    return render_template('PasscheckUI.html')

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
