# Gemini Prompt Consistency Tester

This Flask-based web application allows you to test the consistency of outputs from Google's **Gemini** large language models. You can upload system and user messages, specify model parameters (number of runs, model name, temperature, seed), and visualize how consistent the model's responses are across multiple runs.

The application highlights inconsistencies directly within the raw output, helping you identify areas where the model's behavior might vary.

---

## ✨ Features

- **Customizable Testing**: Upload your own system and user prompt files (`.txt`).
- **Multiple Runs**: Specify how many times you want the model to execute the prompt.
- **Model Selection**: Choose from various Gemini models (e.g., `gemini-pro`, `gemini-1.5-pro-latest`, etc.).
- **Parameter Control**:
  - Adjust **temperature** for creativity.
  - Set a **seed** for reproducibility (when supported by the model).
- **Consistency Analysis**:
  - Calculates overall output consistency percentage.
  - Identifies the most frequent output.
  - Highlights inconsistencies (🔴 red text) within each run compared to the most frequent output.
  - Highlights consistent parts in 🟢 green.
- **User-Friendly UI**: A clean, split-panel interface for efficient testing and result viewing.

---

## 🛠 Technologies Used

- **Backend**: Python (Flask)
- **AI Model**: Google Gemini API (`google-generativeai` library)
- **Frontend**: HTML, CSS, JavaScript (minimal)
- **Diffing**: `difflib` for comparing text outputs
- **Environment Variables**: `python-dotenv`

---

## 🚀 Setup and Installation

Follow these steps to get the application running on your local machine.

### 1. Prerequisites

- Python 3.8+
- A Google Cloud Project with the Gemini API enabled
- A Gemini API Key

### 2. Clone the Repository / Download the Files

```bash
git clone <your-repo-url>
cd <your-repo-folder>
```

### 3. Create a Virtual Environment (Recommended)

```bash
python -m venv venv

# On macOS/Linux
source venv/bin/activate

# On Windows
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install Flask google-generativeai python-dotenv markdown2
```

### 5. Configure Your Gemini API Key

- Obtain a Gemini API key from Google AI Studio or Google Cloud Console.
- Create a file named `.env` in the root directory of your project:

```
GEMINI_API_KEY="YOUR_API_KEY_HERE"
```

> ✅ **Note**: The UI also has an input field for the API key for quick testing. For production use, the `.env` file method is safer and more secure.

### 6. Create Uploads Directory

```bash
mkdir uploads
```

### 7. Prepare Prompt Files

Create two `.txt` files:

- `system_message.txt`: Contains your system instructions for the Gemini model.
- `user_message.txt`: Contains the user prompt or query.

Upload these files via the UI when running the app.

### 8. Run the Application

```bash
python app.py
```

The app will be available at [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

---

## 🧪 How to Use

1. **Enter Gemini API Key**  
   Input your API key in the field provided (stored locally in browser for convenience).

2. **Upload Prompt Files**  
   Upload `system_message.txt` and `user_message.txt`.

3. **Configure Test Runs**  
   - **Number of Runs**: Number of times to run the prompt.
   - **Model**: Select a Gemini model.
   - **Temperature**: Controls output randomness.
   - **Seed** (optional): Enter an integer for reproducibility.

4. **Run Tests**  
   Click `Run Tests` to begin.

5. **View Results**  
   - Right panel shows **Overall Consistency Summary**.
   - Expandable sections show:
     - Raw output from each run.
     - Red highlights = inconsistent parts.
     - Green highlights = consistent parts.
     - Most frequent output for reference.

   Errors (if any) will be shown in place of the output.

---

## 📁 File Structure

```
.
├── app.py                  # Main Flask application logic
├── templates/
│   └── index.html          # HTML template for the web interface
├── uploads/                # Directory for uploaded prompt files
├── .env                    # Stores your Gemini API key (excluded in .gitignore)
└── README.md               # Project documentation
```

---

## 📄 License

This project is for educational and testing purposes. No official affiliation with Google or the Gemini team.

---

## 🙌 Contributions

Feel free to open issues or submit PRs to improve features, performance, or UI!
