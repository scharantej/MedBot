
# Import the necessary modules.
from flask import Flask, render_template, request, redirect, url_for, send_file
import PyPDF2
import pandas as pd

# Create a Flask app.
app = Flask(__name__)

# Define the route for the upload page.
@app.route('/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Get the uploaded file.
        file = request.files['file']

        # Validate the file.
        if not file.filename.endswith('.pdf'):
            return 'Invalid file type.'

        # Save the file.
        file.save('report.pdf')

        # Redirect to the processing page.
        return redirect(url_for('process'))

    # Render the upload page.
    return render_template('upload.html')

# Define the route for the processing page.
@app.route('/process', methods=['GET', 'POST'])
def process():
    # Open the PDF file.
    pdf_file = open('report.pdf', 'rb')

    # Read the PDF file.
    pdf_reader = PyPDF2.PdfFileReader(pdf_file)

    # Get the text from the PDF file.
    text = pdf_reader.getPage(0).extractText()

    # Close the PDF file.
    pdf_file.close()

    # Extract the relevant data from the text.
    data = extract_data(text)

    # Generate a Google Sheet with the processed data.
    sheet = generate_sheet(data)

    # Save the Google Sheet.
    sheet.save('data.xlsx')

    # Redirect to the data page.
    return redirect(url_for('data'))

# Define the route for the data page.
@app.route('/data', methods=['GET'])
def data():
    # Return the Google Sheet.
    return send_file('data.xlsx', as_attachment=True)

# Extract the relevant data from the text.
def extract_data(text):
    # Find the start and end of the data section.
    start = text.find('Policy Number:')
    end = text.find('Total Charges:')

    # Get the data section.
    data = text[start:end]

    # Split the data section into lines.
    lines = data.split('\n')

    # Create a dictionary to store the data.
    data = {}

    # Loop through the lines.
    for line in lines:
        # Split the line into key and value.
        key, value = line.split(':')

        # Add the key and value to the dictionary.
        data[key] = value

    # Return the dictionary.
    return data

# Generate a Google Sheet with the processed data.
def generate_sheet(data):
    # Create a DataFrame from the data.
    df = pd.DataFrame.from_dict(data, orient='index')

    # Create a Google Sheet.
    sheet = gspread.create('Medical Insurance Claims')

    # Set the worksheet title.
    sheet.worksheet('Sheet1').title = 'Claims Data'

    # Update the worksheet with the data.
    sheet.worksheet('Sheet1').update([df.columns.tolist()] + df.values.tolist())

    # Return the Google Sheet.
    return sheet

# Run the app.
if __name__ == '__main__':
    app.run()
