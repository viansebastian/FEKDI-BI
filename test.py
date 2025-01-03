# FLASK API SCRIPT 

'''
Key Features: 
1. Return Image of Petri Net 
2. Return global metric results 
3. Return all alignments and metric
'''
import os
import io
import tempfile
from flask import Flask, request, jsonify #,send_file
from flask_cors import CORS
from core_func import draw_petri_csv, draw_petri_xes, token_based_replay_csv, token_based_replay_xes, diagnostics_alignments_csv, diagnostics_alignments_xes

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "HEAD", "POST", "OPTIONS", "PUT", "PATCH", "DELETE"],
        "allow_headers": ["Authorization", "Content-Type"]
    }
})

@app.route("/")
def home():
    return "Hello World", 200

@app.errorhandler(404)
def page_not_found(e):
    return jsonify({"status": 404, "message": "Not Found"}), 404

@app.route('/check-graphviz')
def check_graphviz():
    import subprocess
    try:
        output = subprocess.check_output(['dot', '-V'], stderr=subprocess.STDOUT)
        return output.decode('utf-8')
    except subprocess.CalledProcessError as e:
        return str(e)

# API endpoint to draw Petri net from CSV
@app.route('/draw-petri-csv', methods=['POST'])
def draw_petri_csv_api():
    
    if 'file' not in request.files or not request.files['file']:
        return jsonify({'error': 'No file part in the request'}), 400
    
    file = request.files['file']
    sep = request.form['sep']
    case_id = request.form['case_id']
    activity_key = request.form['activity_key']
    timestamp_key = request.form['timestamp_key']
    
    # Save file temporarily
    temp_csv_file = tempfile.NamedTemporaryFile(delete=False)
    file.save(temp_csv_file.name)
    temp_csv_file.close()
    
    pnml_content, image, _, _, _ = draw_petri_csv(temp_csv_file.name, sep, case_id, activity_key, timestamp_key)
    
    # Remove temporary file
    os.remove(temp_csv_file.name)
    
    img_stream = io.BytesIO()
    image.save(img_stream, format='PNG')
    img_stream.seek(0)
    
    return jsonify({
        'pnml': pnml_content,
        'petri_img' : img_stream.getvalue().hex()
    })

# API endpoint to draw Petri net from XES
@app.route('/diagnostics-alignments-xes', methods=['POST'])
def diagnostics_alignments_xes_api():
    
    if 'file' not in request.files or 'pnml_file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    
    file = request.files['file']
    pnml_file = request.files['pnml_file']
    
    if file.filename == '' or pnml_file.filename == '':
        return jsonify({'error': 'No file selected for uploading'}), 400
    
    # Save file temporarily
    temp_xes_file = tempfile.NamedTemporaryFile(delete=False)
    file.save(temp_xes_file.name)
    temp_xes_file.close()
    
    # Log file content for debugging
    with open(temp_xes_file.name, 'r') as f:
        file_content = f.read()
        print("XES File Content:", file_content)
    
    # Check if the file is empty
    if not file_content:
        return jsonify({'error': 'Uploaded file is empty or corrupted'}), 400
    
    temp_pnml_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pnml')
    pnml_file.save(temp_pnml_file.name)
    temp_pnml_file.close()
    pnml_path = temp_pnml_file.name
    
    try:
        a = diagnostics_alignments_xes(temp_xes_file.name, pnml_path)
    except Exception as e:
        # Log the exception
        print("Exception occurred:", e)
        return jsonify({'error': 'An error occurred during processing', 'details': str(e)}), 500
    
    # Remove temporary files
    os.remove(temp_xes_file.name)
    os.remove(temp_pnml_file.name)
    
    return jsonify({'result': a})

# @app.route('/draw-petri-xes', methods=['POST'])
# def draw_petri_xes_api():
    
#     if 'file' not in request.files:
#         return jsonify({'error': 'No file part in the request'}), 400
    
#     file = request.files['file']

#     # Save file temporarily
#     temp_xes_file = tempfile.NamedTemporaryFile(delete=False)
#     file.save(temp_xes_file.name)
#     temp_xes_file.close()
    
#     pnml_content, image, _, _, _ = draw_petri_xes(temp_xes_file.name)
    
#     # Remove temporary file
#     os.remove(temp_xes_file.name)
    
#     img_stream = io.BytesIO()
#     image.save(img_stream, format='PNG')
#     img_stream.seek(0)
    
#     return jsonify({
#         'pnml': pnml_content,
#         'petri_image' : img_stream.getvalue().hex()
#     })

# API endpoint for token-based replay from CSV
@app.route('/token-replay-csv', methods=['POST'])
def token_replay_csv_api():
    
    if 'file' not in request.files or not request.files['file']:
        return jsonify({'error': 'No file part in the request'}), 400
    
    file = request.files['file']
    sep = request.form['sep']
    case_id = request.form['case_id']
    activity_key = request.form['activity_key']
    timestamp_key = request.form['timestamp_key']
    pnml_file = request.files['pnml_file']
    
    # Save file temporarily
    temp_csv_file = tempfile.NamedTemporaryFile(delete=False)
    file.save(temp_csv_file.name)
    temp_csv_file.close()
    
    temp_pnml_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pnml')
    pnml_file.save(temp_pnml_file.name)
    temp_pnml_file.close()
    pnml_path = temp_pnml_file.name
    
    a = token_based_replay_csv(temp_csv_file.name, sep, case_id, activity_key, timestamp_key, pnml_path)
    
    # Remove temporary file
    os.remove(temp_csv_file.name)
    os.remove(temp_pnml_file.name)
    
    return jsonify({'result': a})

# API endpoint for token-based replay from XES
@app.route('/token-replay-xes', methods=['POST'])
def token_replay_xes_api():
    
    if 'file' not in request.files or not request.files['file']:
        return jsonify({'error': 'No file part in the request'}), 400
    
    file = request.files['file']
    pnml_file = request.files['pnml_file']
    
    # Save file temporarily
    temp_xes_file = tempfile.NamedTemporaryFile(delete=False)
    file.save(temp_xes_file.name)
    temp_xes_file.close()
    
    temp_pnml_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pnml')
    pnml_file.save(temp_pnml_file.name)
    temp_pnml_file.close()
    pnml_path = temp_pnml_file.name
    
    a = token_based_replay_xes(temp_xes_file.name, pnml_path)
    
    # Remove temporary file
    os.remove(temp_xes_file.name)
    os.remove(temp_pnml_file.name)
    
    return jsonify({'result': a})

# API endpoint for diagnostics alignments from CSV
@app.route('/diagnostics-alignments-csv', methods=['POST'])
def diagnostics_alignments_csv_api():
    
    if 'file' not in request.files or not request.files['file']:
        return jsonify({'error': 'No file part in the request'}), 400
    
    file = request.files['file']
    sep = request.form['sep']
    case_id = request.form['case_id']
    activity_key = request.form['activity_key']
    timestamp_key = request.form['timestamp_key']
    pnml_file = request.files['pnml_file']
    
    # Save file temporarily
    temp_csv_file = tempfile.NamedTemporaryFile(delete=False)
    file.save(temp_csv_file.name)
    temp_csv_file.close()

    temp_pnml_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pnml')
    pnml_file.save(temp_pnml_file.name)
    temp_pnml_file.close()
    pnml_path = temp_pnml_file.name
    
    a = diagnostics_alignments_csv(temp_csv_file.name, sep, case_id, activity_key, timestamp_key, pnml_path)
    
    # Remove temporary file
    os.remove(temp_csv_file.name)
    os.remove(temp_pnml_file.name)
    
    return jsonify({'result' : a})

@app.route('/diagnostics-alignments-xes', methods=['POST'])
def diagnostics_alignments_xes_api():
    
    if 'file' not in request.files or not request.files['file']:
        return jsonify({'error': 'No file part in the request'}), 400
    
    file = request.files['file']
    pnml_file = request.files['pnml_file']
    
    # Save file temporarily
    temp_xes_file = tempfile.NamedTemporaryFile(delete=False)
    file.save(temp_xes_file.name)
    temp_xes_file.close()
    
    temp_pnml_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pnml')
    pnml_file.save(temp_pnml_file.name)
    temp_pnml_file.close()
    pnml_path = temp_pnml_file.name
    
    a = diagnostics_alignments_xes(temp_xes_file.name, pnml_path)
    
    # Remove temporary file
    os.remove(temp_xes_file.name)
    os.remove(temp_pnml_file.name)
    
    return jsonify({'result' : a})


# if __name__ == '__main__': 
#     app.run(debug= True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))