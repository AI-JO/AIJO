# X-ray Analysis Web Application

This is a Flask web application that analyzes chest X-ray images using the torchxrayvision model. The application can process images either through file upload or URL input.

## Setup and Installation

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python main.py
   ```

4. Open your browser and navigate to `http://localhost:5000`

## Features

- Upload X-ray images through file upload or URL
- Drag and drop support for file uploads
- Real-time analysis of chest X-rays
- Display of multiple medical condition probabilities
- Modern and responsive user interface

## Note

The application uses the DenseNet121 model from torchxrayvision to analyze chest X-rays. The model can detect various medical conditions and provides probability scores for each condition.
