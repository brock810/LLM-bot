from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import openai
import re

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_code():
    try:
        data = request.get_json()

        if 'prompt' not in data or not data['prompt']:
            return jsonify({'error': 'Invalid request. Missing or empty "prompt" parameter.'}), 400
        
        prompt = data['prompt']
        temperature = float(data.get('temperature', 1.0)) 

        max_tokens = 3000 
        if len(prompt) > 100:
            max_tokens = 5000 
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )

        if 'choices' in response and response['choices']:
            completion_text = response['choices'][0]['message']['content']
            
            formatted_response = format_response(completion_text)
            
            return jsonify({'completion': formatted_response})
        else:
            return jsonify({'error': 'Unexpected response from OpenAI API.'}), 500
        
    except ValueError as e:
        return jsonify({'error': f'Invalid parameter value: {str(e)}'}), 400

    except openai.OpenAIError as e:
        return jsonify({'error': f'OpenAI API error: {str(e)}'}), 500

    except Exception as e:
        app.logger.error(f"Error in generate_code(): {str(e)}")
        return jsonify({'error': 'Internal Server Error'}), 500

def format_response(completion_text):
    """Format the completion text into structured code snippets with language annotations."""
    formatted_response = []

    current_block = []
    current_language = None

    lines = completion_text.split('\n')
    for line in lines:
        if line.strip().startswith('```'):
            if current_block:
                if current_language: 
                    formatted_response.append(f"```{current_language}\n" + '\n'.join(current_block) + "\n```")
                else:
                    formatted_response.append('\n'.join(current_block)) 
                current_block = []

            match = re.match(r'^```(\w+)', line.strip())
            if match:
                current_language = match.group(1)
            else:
                current_language = ''  
        else:
            current_block.append(line)

    if current_block:
        if current_language:  
            formatted_response.append(f"```{current_language}\n" + '\n'.join(current_block) + "\n```")
        else:
            formatted_response.append('\n'.join(current_block))  

    return '\n\n'.join(formatted_response)


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8080)
