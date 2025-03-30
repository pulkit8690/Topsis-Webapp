import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import pandas as pd
import plotly.express as px
import plotly.io as pio

from utils.file_handler import allowed_file, load_input_data, validate_numeric_values
from utils.email_utils import send_email
from utils.topsis_calc import validate_weights_impacts, calculate_custom_score
from utils.data_autofill import autofill_criteria_values

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'supersecretkey')

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ===================== ROUTES ===================== #

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit():
    mode = request.form.get('mode')

    if mode == 'upload':
        # ---------- Manual Upload Mode ----------
        file = request.files.get('file')
        if not file or file.filename == '':
            flash('No file selected.')
            return redirect(url_for('index'))

        if not allowed_file(file.filename):
            flash('Invalid file type. Please upload a CSV or XLSX file.')
            return redirect(url_for('index'))

        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        data = load_input_data(file_path)
        if data is None:
            flash('Invalid or unreadable file.')
            return redirect(url_for('index'))

        if not validate_numeric_values(data):
            flash('All columns except the first must be numeric.')
            return redirect(url_for('index'))

        session['mode'] = 'upload'
        session['uploaded_file'] = filename
        columns = data.columns[1:]
        return render_template('weights_impacts.html', columns=columns)

    elif mode == 'autofill':
        # ---------- AI Autofill Mode ----------
        alternatives = request.form.get('alternatives').split(',')
        criteria = request.form.get('criteria').split(',')

        if not alternatives or not criteria:
            flash('Please enter valid alternatives and criteria.')
            return redirect(url_for('index'))

        openai_key = os.getenv("OPENAI_API_KEY")
        serpapi_key = os.getenv("SERPAPI_KEY")

        df = autofill_criteria_values(
            alternatives=[alt.strip() for alt in alternatives],
            criteria=[crit.strip() for crit in criteria],
            openai_api_key=openai_key,
            serpapi_key=serpapi_key
        )

        file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'autofilled_data.csv')
        df.to_csv(file_path, index=False)
        if df.isnull().values.any():
            flash('Some criteria values could not be auto-filled. Please check and re-upload if needed.')

        session['mode'] = 'autofill'
        session['uploaded_file'] = 'autofilled_data.csv'
        columns = df.columns[1:]
        return render_template('weights_impacts.html', columns=columns)

    else:
        flash('Invalid mode selected.')
        return redirect(url_for('index'))


@app.route('/process', methods=['POST'])
def process():
    weights = request.form.getlist('weights')
    impacts = request.form.getlist('impacts')
    email = request.form.get('email')

    filename = session.get('uploaded_file')
    mode = session.get('mode')

    if not filename:
        flash('No file found in session. Please upload or autofill again.')
        return redirect(url_for('index'))

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    data = load_input_data(file_path)
    if data is None:
        flash('File could not be loaded. Try again.')
        return redirect(url_for('index'))

    # Validate numeric values (in case autofill includes text)
    if not validate_numeric_values(data):
        flash('All columns except the first must contain numeric values.')
        return redirect(url_for('index'))

    # Validate weights and impacts
    if not weights or not impacts:
        flash('Please provide weights and impacts.')
        return redirect(url_for('index'))

    if len(weights) != len(data.columns) - 1 or len(impacts) != len(data.columns) - 1:
        flash('Weights/Impacts count must match the number of criteria.')
        return redirect(url_for('index'))

    weights_str = ','.join(weights)
    impacts_str = ','.join(impacts)

    if not validate_weights_impacts(weights_str, impacts_str, len(data.columns)):
        flash('Invalid format for weights or impacts.')
        return redirect(url_for('index'))

    # Perform TOPSIS
    scores = calculate_custom_score(data, weights_str, impacts_str)
    data['Custom Score'] = scores
    data['Rank'] = data['Custom Score'].rank(ascending=False)

    # Save result CSV
    result_path = os.path.join(app.config['UPLOAD_FOLDER'], 'result_with_rank.csv')
    data.to_csv(result_path, index=False)

    # Visualization
    fig = px.bar(data, x=data.columns[0], y='Custom Score', title='TOPSIS Scores', text='Rank')
    graph_html = pio.to_html(fig, full_html=False)

    # Send Email
    send_email(data, email)

    return render_template('result.html', graph_html=graph_html, csv_download_link='/download')


@app.route('/download')
def download():
    result_csv_path = os.path.join(app.config['UPLOAD_FOLDER'], 'result_with_rank.csv')
    return send_file(result_csv_path, as_attachment=True)


# ===================== MAIN ===================== #

if __name__ == '__main__':
    app.run(debug=True)
