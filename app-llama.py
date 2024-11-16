import json
import os
import subprocess
from flask import Flask, request, jsonify, render_template
from llamaapi import LlamaAPI  # Import the correct LlamaAPI class

app = Flask(__name__)

# Initialize the LlamaAPI with your API token
llama = LlamaAPI("")

# Llama API call function
def llama_api_call(prompt):
    try:
        # Assuming the method to call Llama API is 'generate'
        response = llama.run(
            model="llama3.1-8b",  # Specify the model
            prompt=prompt,
            max_tokens=2500,  # Maximum tokens to generate
            messages=[
                {"role": "system", "content": "You are a Trained Network Automation Engine Expert. Do not provide any text/summary before or after response. Only Provide code for mininet with ryu controller setup using Langchain. Not Ryu application and Provide code and debug issues related to all network engineering tasks. Do not provide any text/description only provide code."},
                {"role": "user", "content": prompt}
            ]
        )

        # Debugging: Print full response for troubleshooting
        print(f"Full response for prompt '{prompt}': {response}")

        # Parse response to get the generated code
        if response and 'choices' in response and len(response['choices']) > 0:
            code = response['choices'][0]['message']['content'].strip()
            return code.replace('```', '').strip()  # Clean up Markdown-style code blocks
        else:
            return "Error: No response choices found in the response"
    
    except Exception as e:
        error_message = f"Error generating response from Llama API: {e}"
        print(error_message)
        return error_message

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-code', methods=['POST'])
def generate_code():
    prompt = request.json['prompt']  # Get the prompt from the request
    generated_code = llama_api_call(prompt)  # Generate code using Llama API
    code_file_path = 'generated_code.py'  # Save generated code in a file
    
    # Write the generated code to a file
    with open(code_file_path, 'w') as f:
        f.write(generated_code)
    
    # Return the generated code and file path in the response
    return jsonify({'code': generated_code, 'file_path': code_file_path})

@app.route('/execute-code', methods=['POST'])
def execute_code():
    code_file_path = 'generated_code.py'  # Define the file path of the code to execute
    
    # Check if the code file exists
    if not os.path.exists(code_file_path):
        return jsonify({'message': 'Code file does not exist.'}), 404

    # Execute the code using subprocess and capture output
    result = subprocess.run(['python3', code_file_path], capture_output=True, text=True)
    
    # Check the result of execution and return appropriate message
    if result.returncode == 0:
        message = 'Code executed successfully.'
    else:
        message = f'Error executing code: {result.stderr}'
    
    return jsonify({'message': message})

@app.route('/run-saved-tests', methods=['POST'])
def run_saved_tests():
    try:
        # Load saved responses from a file (assuming responses.json)
        with open('responses.json') as f:
            responses = json.load(f)

        # Function to write and execute code
        def test_code(code, filename):
            with open(filename, 'w') as f:
                f.write(code)
            os.system(f"python {filename}")

        results = []
        # Loop through the saved test cases
        for model, outputs in responses.items():
            for prompt, code in outputs.items():
                filename = f"{model}_{prompt.replace(' ', '_')}.py"
                try:
                    # Write and test each code output
                    test_code(code, filename)
                    results.append(f"{model} passed for prompt: {prompt}")
                except Exception as e:
                    results.append(f"{model} failed for prompt: {prompt} with error: {e}")
        
        return jsonify({'results': results})
    
    except Exception as e:
        return jsonify({'message': f"Error running saved tests: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)

