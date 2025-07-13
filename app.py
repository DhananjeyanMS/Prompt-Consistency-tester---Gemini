import os
import re
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
import google.generativeai as genai
from dotenv import load_dotenv
import difflib # For highlighting differences

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24) # A secret key for flashing messages
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16 MB limit for uploads

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# --- Gemini API Configuration ---
def configure_gemini_api(api_key):
    try:
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        print(f"Error configuring Gemini API: {e}")
        return False

# --- Helper Functions ---

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'txt'}

def read_file_content(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return None

# Removed the normalize_output function entirely as it's no longer used for comparison

def highlight_against_most_frequent(current_output, most_frequent_output):
    """
    Compares current_output to most_frequent_output character by character,
    and returns HTML where exact differing parts of current_output are highlighted.
    Green for common parts, Red for differing parts.
    """
    if not most_frequent_output:
        # If there's no most frequent output, treat the entire output as stable.
        return f'<span class="stable-green">{current_output}</span>'

    matcher = difflib.SequenceMatcher(None, current_output, most_frequent_output)
    
    highlighted_parts = []
    last_idx_current = 0 # To track position in current_output

    for opcode, a1, a2, b1, b2 in matcher.get_opcodes():
        # Append any unhandled (equal) parts between the last segment and the current one
        if a1 > last_idx_current:
            highlighted_parts.append(f'<span class="stable-green">{current_output[last_idx_current:a1]}</span>')

        if opcode == 'equal':
            highlighted_parts.append(f'<span class="stable-green">{current_output[a1:a2]}</span>')
        elif opcode == 'replace':
            # This segment in current_output differs from most_frequent_output
            highlighted_parts.append(f'<span class="inconsistent-red">{current_output[a1:a2]}</span>')
        elif opcode == 'delete':
            # This segment is in current_output but not in most_frequent_output
            highlighted_parts.append(f'<span class="inconsistent-red">{current_output[a1:a2]}</span>')
        elif opcode == 'insert':
            # This segment is in most_frequent_output but NOT in current_output.
            # Since we are only highlighting *within* current_output, we don't
            # add this content. Its absence is the inconsistency.
            pass
        
        last_idx_current = a2 # Update the last processed index in current_output

    # Append any remaining stable parts at the end
    if last_idx_current < len(current_output):
        highlighted_parts.append(f'<span class="stable-green">{current_output[last_idx_current:]}</span>')

    return ''.join(highlighted_parts)

# --- Flask Routes ---

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # API Key Handling
        gemini_api_key = request.form.get('gemini_api_key')
        if not gemini_api_key:
            flash('Gemini API Key is required!', 'error')
            return redirect(url_for('index'))
        
        if not configure_gemini_api(gemini_api_key):
            flash('Invalid Gemini API Key or configuration error!', 'error')
            return redirect(url_for('index'))

        # File Uploads
        system_message_file = request.files.get('system_message_file')
        user_message_file = request.files.get('user_message_file')

        if not system_message_file or not user_message_file:
            flash('Both system and user message files are required.', 'error')
            return redirect(url_for('index'))

        if not allowed_file(system_message_file.filename) or not allowed_file(user_message_file.filename):
            flash('Only .txt files are allowed for messages.', 'error')
            return redirect(url_for('index'))

        system_filename = secure_filename(system_message_file.filename)
        user_filename = secure_filename(user_message_file.filename)

        system_filepath = os.path.join(app.config['UPLOAD_FOLDER'], system_filename)
        user_filepath = os.path.join(app.config['UPLOAD_FOLDER'], user_filename)

        system_message_file.save(system_filepath)
        user_message_file.save(user_filepath)

        system_message_content = read_file_content(system_filepath)
        user_message_content = read_file_content(user_filepath)

        if system_message_content is None or user_message_content is None:
            flash('Failed to read content from uploaded files.', 'error')
            return redirect(url_for('index'))

        # Get other parameters
        num_runs = int(request.form.get('num_runs', 1))
        model_name = request.form.get('model_name', 'gemini-pro')
        temperature = float(request.form.get('temperature', 0.7))
        seed = request.form.get('seed')
        
        # Convert seed to int if provided, otherwise None
        generation_config = {"temperature": temperature}
        if seed:
            try:
                generation_config["seed"] = int(seed)
            except ValueError:
                flash("Invalid seed value. Please enter an integer.", "error")
                return redirect(url_for('index'))


        # --- Core Logic Placeholder ---
        try:
            results = run_gemini_tests(
                system_message_content,
                user_message_content,
                num_runs,
                model_name,
                generation_config
            )
            return render_template('index.html', results=results,
                                   system_message=system_message_content,
                                   user_message=user_message_content)
        except Exception as e:
            flash(f"An error occurred during testing: {e}", 'error')
            return redirect(url_for('index'))

    return render_template('index.html')

# --- Main Logic Function ---
def run_gemini_tests(system_message, user_message, num_runs, model_name, generation_config):
    outputs = []
    
    try:
        model = genai.GenerativeModel(model_name)
    except Exception as e:
        raise Exception(f"Could not initialize Gemini model '{model_name}': {e}")


    for i in range(num_runs):
        try:
            full_prompt = f"System Instruction:\n{system_message}\n\nUser Query:\n{user_message}"
            chat_session = model.start_chat(history=[])
            response = chat_session.send_message(full_prompt, generation_config=generation_config)

            output_text = response.text
            # We are no longer storing 'normalized_output' in the individual output dict
            outputs.append({
                'run_number': i + 1,
                'raw_output': output_text,
                'status': 'Success'
            })
        except Exception as e:
            outputs.append({
                'run_number': i + 1,
                'raw_output': f"Error: {e}",
                'status': 'Failed'
            })
            print(f"Error during Gemini API call for run {i+1}: {e}")

    # --- Consistency Analysis ---
    if not outputs:
        return {
            'overall_consistency_percentage': 0,
            'identical_count': 0,
            'total_runs': num_runs, # This uses the original requested number of runs
            'individual_results': outputs,
            'summary_message': 'No outputs generated.'
        }

    # IMPORTANT: Use 'raw_output' directly for comparison
    successful_outputs_for_comparison = [o['raw_output'] for o in outputs if o['status'] == 'Success']

    if not successful_outputs_for_comparison:
        return {
            'overall_consistency_percentage': 0,
            'identical_count': 0,
            'total_runs': num_runs,
            'individual_results': outputs,
            'summary_message': 'No successful outputs to compare.'
        }
        
    # Count occurrences of each unique raw output
    output_counts = {}
    for output in successful_outputs_for_comparison:
        output_counts[output] = output_counts.get(output, 0) + 1

    # Find the most frequent raw output and its count
    if output_counts:
        most_frequent_output = max(output_counts, key=output_counts.get)
        most_frequent_count = output_counts[most_frequent_output]
    else:
        most_frequent_output = ""
        most_frequent_count = 0

    overall_consistency_percentage = (most_frequent_count / len(successful_outputs_for_comparison)) * 100 if successful_outputs_for_comparison else 0

    # Add consistency status and highlighted content to each individual result
    for output_data in outputs:
        if output_data['status'] == 'Success':
            output_data['is_consistent_with_most_frequent'] = (output_data['raw_output'] == most_frequent_output)
            if not output_data['is_consistent_with_most_frequent']:
                output_data['highlighted_output'] = highlight_against_most_frequent(
                    output_data['raw_output'], most_frequent_output
                )
            else:
                # If consistent, the whole output is stable-green
                output_data['highlighted_output'] = f'<span class="stable-green">{output_data["raw_output"]}</span>'
        else:
            # FIX: Corrected typo here and simplified logic
            output_data['is_consistent_with_most_frequent'] = False 
            output_data['highlighted_output'] = output_data['raw_output'] # Just show raw error for failed

    return {
        'overall_consistency_percentage': round(overall_consistency_percentage, 2),
        'identical_count': most_frequent_count,
        'total_runs': num_runs, # Ensure this always refers to the requested 'num_runs'
        'individual_results': outputs,
        'most_frequent_output': most_frequent_output # This will now be the raw, most frequent output
    }


if __name__ == '__main__':
    app.run(debug=True) # Set debug=False in production
