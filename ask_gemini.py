import google.generativeai as genai
import sys
import json

def get_ai_response(query, api_key, model_name):
    try:
        genai.configure(api_key=api_key)

        model = genai.GenerativeModel(model_name=model_name)
        response = model.generate_content(query)
        
        print(response.text)

    except Exception as e:
        print(f"ERRO_IA: {e}")

def main():
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load()
        
        api_key = config['api_keys']['gemini_api_key']
        model_name = config['gemini_settings']['model_name']

    except (FileNotFoundError, KeyError) as e:
        print(f"ERRO_IA: Falha ao ler o 'config.json': {e}")
        sys.exit(1)

    if len(sys.argv) > 1:
        user_query = " ".join(sys.argv[1:])
        get_ai_response(user_query, api_key, model_name)

if __name__ == "__main__":
    main()