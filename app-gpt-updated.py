import json
import os
import requests
from flask import Flask, request, jsonify, render_template
import subprocess

app = Flask(__name__)

# Replace this with your actual OpenAI API key
openai_api_key = ''

def openai_api_call(prompt, api_key):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Define the base role instructions (system prompt)
    base_role_instructions = """
    You are a network automation expert. Every time you receive a prompt, adhere to the following base setup for Mininet topology:
    
    1. Use remote controllers like (`c1` and `c2`), where `c1` is at IP `127.0.0.1` on port `6633` and `c2` is at IP `127.0.0.1` on port `6634`.
    2. Create switches (`s1` to `s6`) using OpenFlow protocol 1.3.
    3. Connect the following hosts with the mentioned IP addresses:
       - `h1` (IP `10.0.1.1/24`) and `h2` (IP `10.0.1.2/24`) connected to `s1`.
       - `h3` (IP `10.0.2.1/24`) and `h4` (IP `10.0.2.2/24`) connected to `s3`.
       - `h5` (IP `10.0.3.1/24`), `h6` (IP `10.0.3.2/24`), `h7` (IP `10.0.4.1/24`), and `h8` (IP `10.0.4.2/24`) connected to `s6`.
    4. Ensure the regions are managed by controllers `c1` and `c2`.
    5. Start the network.
    6. Run Mininet CLI
    7. Please provide only clean python code ready for execution without any comments or explanation..
    8. Do not provide python tag in the first line of output code.
    You may receive additional instructions or modifications from the user.
    """

    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": base_role_instructions},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 2500
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()

        response_json = response.json()
        if 'choices' in response_json and len(response_json['choices']) > 0:
            code = response_json['choices'][0]['message']['content'].strip()
            return code.replace('```', '').strip()
        else:
            return "Error: No response choices found."
    except requests.exceptions.RequestException as e:
        return f"Error generating response from OpenAI: {e}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-code', methods=['POST'])
def generate_code():
    prompt = request.json['prompt']  # Get the specific network topology request from the user
    generated_code = openai_api_call(prompt, openai_api_key)
    code_file_path = 'generated_code.py'
    
    with open(code_file_path, 'w') as f:
        f.write(generated_code)
    
    return jsonify({'code': generated_code, 'file_path': code_file_path})

@app.route('/execute-code', methods=['POST'])
def execute_code():
    code_file_path = 'generated_code.py'
    
    if not os.path.exists(code_file_path):
        return jsonify({'message': 'Code file does not exist.'}), 404

    result = subprocess.run(['sudo python3', code_file_path], capture_output=True, text=True)
    if result.returncode == 0:
        message = 'Code executed successfully.'
    else:
        message = f'Error executing code: {result.stderr}'
    
    return jsonify({'message': message})

@app.route('/run-saved-tests', methods=['POST'])
def run_saved_tests():
    try:
        with open('responses.json') as f:
            responses = json.load(f)

        def test_code(code, filename):
            with open(filename, 'w') as f:
                f.write(code)
            os.system(f"python {filename}")

        results = []
        for model, outputs in responses.items():
            for prompt, code in outputs.items():
                filename = f"{model}_{prompt.replace(' ', '_')}.py"
                try:
                    test_code(code, filename)
                    results.append(f"{model} passed for prompt: {prompt}")
                except Exception as e:
                    results.append(f"{model} failed for prompt: {prompt} with error: {e}")
        
        return jsonify({'results': results})
    
    except Exception as e:
        return jsonify({'message': f"Error running saved tests: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)

