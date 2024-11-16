import json
import os
import requests
from flask import Flask, request, jsonify, render_template
import subprocess

app = Flask(__name__)

# Replace this with your actual OpenAI API key
openai_api_key = ''

#openai_api_key = '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'

def openai_api_call(prompt, api_key):
    url = "https://api.openai.com/v1/chat/completions"  # OpenAI endpoint for chat completions
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-3.5-turbo",  # You can also use "gpt-3.5-turbo"
        "messages": [
            {"role": "system", "content": "You are a Trained Network Automation Engine Expert. Do not provide any text/summary before or after response. Only Provide code for mininet with ryu controller setup using Langchain. Not Ryu application and Provide code and debug issues related to all network engineering tasks. Do not provide any text/description only provide code."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 2500
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()

        # Print the full response for debugging
        print(f"Full response for prompt '{prompt}': {response.json()}")

        # Extract the response text from the JSON
        response_json = response.json()
        if 'choices' in response_json and len(response_json['choices']) > 0:
            code = response_json['choices'][0]['message']['content'].strip()
            # Remove any Markdown code block markers
            return code.replace('```', '').strip()
        else:
            return "Error: No response choices found in the response"
    except requests.exceptions.RequestException as e:
        error_message = f"Error generating response from OpenAI: {e}"
        print(error_message)
        return error_message

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-code', methods=['POST'])
def generate_code():
    prompt = request.json['prompt']
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

    result = subprocess.run(['python3', code_file_path], capture_output=True, text=True)
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
        
    except requests.exceptions.RequestException as e:
    	error_message = f"Error generating response from OpenAI: {e}"
    	print(error_message)
    	print(f"Response content: {e.response.content if e.response else 'No response'}")
    	return error_message

if __name__ == '__main__':
    app.run(debug=True)

