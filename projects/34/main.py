# pip install git+https://github.com/Google-Health/cxr-foundation.git#subdirectory=python

# # Load image as grayscale (Stillwaterising, CC0, via Wikimedia Commons)
# import requests
# from PIL import Image
# from io import BytesIO
# image_url = "https://upload.wikimedia.org/wikipedia/commons/c/c8/Chest_Xray_PA_3-8-2010.png"
# img = Image.open(requests.get(image_url, headers={'User-Agent': 'Demo'}, stream=True).raw).convert('L')

# # Run inference
# from clientside.clients import make_hugging_face_client
# cxr_client = make_hugging_face_client('cxr_model')
# print(cxr_client.get_image_embeddings_from_images([img]))

from flask import Flask, request, render_template, jsonify
import os
import requests
from werkzeug.utils import secure_filename
import skimage.io
import torch
import torchvision
import torchxrayvision as xrv
import numpy as np
from PIL import Image
import io
import json
# from dotenv import load_dotenv

# Load environment variables
# load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Arabic translations for medical conditions
ARABIC_TERMS = {
    'Atelectasis': 'انخماص الرئة',
    'Cardiomegaly': 'تضخم القلب',
    'Consolidation': 'تصلب رئوي',
    'Edema': 'وذمة',
    'Effusion': 'انصباب',
    'Emphysema': 'انتفاخ الرئة',
    'Enlarged Cardiomediastinum': 'تضخم المنصف القلبي',
    'Fibrosis': 'تليف',
    'Fracture': 'كسر',
    'Hernia': 'فتق',
    'Infiltration': 'ارتشاح',
    'Lung Lesion': 'آفة رئوية',
    'Lung Opacity': 'عتامة رئوية',
    'Mass': 'كتلة',
    'Nodule': 'عقيدة',
    'Pleural_Thickening': 'تسمك الجنبة',
    'Pneumonia': 'التهاب رئوي',
    'Pneumothorax': 'استرواح الصدر'
}

MODELS = {
    'all': {
        'name': 'جميع مجموعات البيانات',
        'weights': 'densenet121-res224-all'
    },
    'chexpert': {
        'name': 'تشيكسبرت (ستانفورد)',
        'weights': 'densenet121-res224-chex'
    },
    'mimic_nb': {
        'name': 'ميميك (معهد ماساتشوستس للتكنولوجيا) NB',
        'weights': 'densenet121-res224-mimic_nb'
    },
    'mimic_ch': {
        'name': 'ميميك (معهد ماساتشوستس للتكنولوجيا) CH',
        'weights': 'densenet121-res224-mimic_ch'
    }
}

def get_openai_consultation(analysis_results):
    # Format the analysis results for OpenAI
    prompt = """
    أنت طبيب خبير في تحليل صور الأشعة السينية. لديك نتائج تحليل من عدة نماذج للذكاء الاصطناعي. 
    بناءً على هذه النتائج، يرجى:
    1. تحديد الحالات المحتملة التي تظهر في الصورة
    2. تقديم توصيات للطبيب المعالج
    3. اقتراح الخطوات التالية للتشخيص أو العلاج

    نتائج التحليل:
    """
    
    # Add formatted results from each model
    for model_key, model_data in analysis_results.items():
        if 'predictions' in model_data:
            prompt += f"\n\nنموذج {model_data['name']}:\n"
            for condition, probability in model_data['predictions'].items():
                percentage = probability * 100
                if percentage > 10:  # Only include significant findings
                    arabic_condition = ARABIC_TERMS.get(condition, condition)
                    prompt += f"- {arabic_condition}: {percentage:.1f}%\n"

    try:
        key_openai = ""
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers={
                'Authorization': f"Bearer {key_openai}",
                'Content-Type': 'application/json'
            },
            json={
                'model': 'gpt-4',
                'messages': [
                    {'role': 'system', 'content': 'You are a medical expert specializing in X-ray analysis. Respond in Arabic.'},
                    {'role': 'user', 'content': prompt}
                ],
                'temperature': 0.7
            }
        )
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return "عذراً، حدث خطأ في الاتصال بنظام التحليل الطبي."
    except Exception as e:
        return f"عذراً، حدث خطأ: {str(e)}"

def get_llm_consultation(analysis_results):
    # Format the analysis results for the LLM
    prompt = """
    أنت طبيب خبير في تحليل صور الأشعة السينية. لديك نتائج تحليل من عدة نماذج للذكاء الاصطناعي. 
    بناءً على هذه النتائج، يرجى:
    1. تحديد الحالات المحتملة التي تظهر في الصورة
    2. تقديم توصيات للطبيب المعالج
    3. اقتراح الخطوات التالية للتشخيص أو العلاج

    نتائج التحليل:
    """
    
    # Add formatted results from each model
    for model_key, model_data in analysis_results.items():
        if 'predictions' in model_data:
            prompt += f"\n\nنموذج {model_data['name']}:\n"
            for condition, probability in model_data['predictions'].items():
                percentage = probability * 100
                if percentage > 10:  # Only include significant findings
                    arabic_condition = ARABIC_TERMS.get(condition, condition)
                    prompt += f"- {arabic_condition}: {percentage:.1f}%\n"

    # Make request to Ollama
    try:
        response = requests.post('http://localhost:11434/api/generate', 
                               json={
                                   'model': 'qwen2.5-coder',
                                   'prompt': prompt,
                                   'stream': False
                               })
        
        if response.status_code == 200:
            return response.json()['response']
        else:
            return "عذراً، حدث خطأ في الاتصال بنظام التحليل الطبي."
    except Exception as e:
        return f"عذراً، حدث خطأ: {str(e)}"

def analyze_xray(img_path):
    # Load and preprocess the image once
    img = skimage.io.imread(img_path)
    img = xrv.datasets.normalize(img, 255)

    # Check that images are 2D arrays
    if len(img.shape) > 2:
        img = img[:, :, 0]
    if len(img.shape) < 2:
        return {"error": "أبعاد الصورة غير صالحة"}

    # Add color channel
    img = img[None, :, :]
    transform = torchvision.transforms.Compose([xrv.datasets.XRayCenterCrop()])
    img = transform(img)
    
    results = {}
    
    # Process with each model
    for model_key, model_info in MODELS.items():
        try:
            # Load the model
            model = xrv.models.DenseNet(weights=model_info['weights'])
            model.eval()

            # Get predictions
            with torch.no_grad():
                img_tensor = torch.from_numpy(img).unsqueeze(0)
                preds = model(img_tensor).cpu()
                
                predictions = {}
                for k, v in zip(xrv.datasets.default_pathologies, preds[0].detach().numpy()):
                    arabic_k = ARABIC_TERMS.get(k, k)
                    predictions[arabic_k] = float(v)

                results[model_key] = {
                    'name': model_info['name'],
                    'predictions': predictions
                }
        except Exception as e:
            results[model_key] = {
                'name': model_info['name'],
                'error': str(e)
            }
    
    return results

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' in request.files:
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'لم يتم اختيار ملف'})
        
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            try:
                results = analyze_xray(filepath)
                os.remove(filepath)  # Clean up
                return jsonify(results)
            except Exception as e:
                os.remove(filepath)  # Clean up
                return jsonify({'error': str(e)})
    
    elif 'url' in request.form:
        url = request.form['url']
        try:
            response = requests.get(url)
            if response.status_code != 200:
                return jsonify({'error': 'فشل في تحميل الصورة من الرابط'})
            
            # Save the image temporarily
            filename = 'temp_xray.png'
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            results = analyze_xray(filepath)
            os.remove(filepath)  # Clean up
            return jsonify(results)
        except Exception as e:
            return jsonify({'error': str(e)})
    
    return jsonify({'error': 'لم يتم تقديم ملف أو رابط'})

@app.route('/consult', methods=['POST'])
def consult():
    try:
        data = request.json
        analysis_results = data['results']
        model_type = data.get('model', 'openai')  # Default to OpenAI if not specified
        
        if model_type == 'openai':
            consultation = get_openai_consultation(analysis_results)
        else:  # ollama
            consultation = get_llm_consultation(analysis_results)
            
        return jsonify({'consultation': consultation})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)