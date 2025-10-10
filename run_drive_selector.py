import os
import sys
import traceback
import subprocess
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

def main():
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        drive_config = config['google_drive_api']
        file_paths = config['file_paths']
    except (FileNotFoundError, KeyError) as e:
        print(f"[ERRO CRÍTICO] # Falha ao ler o 'config.json': {e}")
        sys.exit(1)

    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    FOLDER_ID = drive_config['folder_id']
    FILE_TYPE_MENU = drive_config['file_type_menu']
    TOKEN_PATH = os.path.join(SCRIPT_DIR, drive_config['token_file'])
    CREDS_PATH = os.path.join(SCRIPT_DIR, drive_config['credentials_file'])
    SCOPES = drive_config['scopes']
    ERROR_LOG_PATH = os.path.join(SCRIPT_DIR, file_paths['error_log'])
    
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('drive', 'v3', credentials=creds)

        print("\n[⚡Aether⚡] # Qual tipo de arquivo você deseja buscar?")
        print(" ")
        for key, value in FILE_TYPE_MENU.items():
            print(f"  [{key}] - {value[0]}")
        
        print()
        type_choice = input("Escolha uma opção (ou Enter para cancelar): ").strip()

        if not type_choice or type_choice not in FILE_TYPE_MENU:
            if type_choice: print("\n[⚡Aether⚡] # Opção inválida.")
            return

        selected_type_name, mime_type = FILE_TYPE_MENU[type_choice]

        base_query = f"'{FOLDER_ID}' in parents and trashed=false"
        full_query = base_query
        
        if mime_type != "all":
            if 'image/' in mime_type: full_query += f" and mimeType contains '{mime_type}'"
            else: full_query += f" and mimeType='{mime_type}'"

        results = service.files().list(q=full_query, pageSize=100, orderBy='modifiedTime desc', fields="files(name, webViewLink)").execute()
        items = results.get('files', [])

        if not items:
            print(f"\n[⚡Aether⚡] # Nenhum arquivo do tipo '{selected_type_name}' encontrado na pasta.")
            return

        print(f"\n[⚡Aether⚡] # Encontrei os seguintes arquivos:")
        print (" ")
        for i, item in enumerate(items):
            print(f"  [{i+1}] - {item.get('name')}")
        
        print()
        file_choice_str = input("Escolha o ARQUIVO que deseja abrir (ou Enter para cancelar): ")

        if not file_choice_str: return
        
        try:
            file_choice_num = int(file_choice_str)
            if 1 <= file_choice_num <= len(items):
                selected_item = items[file_choice_num - 1]
                url_to_open = selected_item.get('webViewLink')
                print("\n[⚡Aether⚡] # Entendido. Abrindo o arquivo escolhido...")
                subprocess.run(['py', 'launch_chrome.py', url_to_open], stdin=subprocess.DEVNULL)
            else: print("\n[⚡Aether⚡] # Opção inválida.")
        except ValueError: print("\n[⚡Aether⚡] # Entrada inválida. Por favor, digite um número.")

    except Exception as e:
        ERROR_LOG_PATH = os.path.join(SCRIPT_DIR, 'error_log.txt')
        with open(ERROR_LOG_PATH, 'w', encoding='utf-8') as f:
            f.write(traceback.format_exc())
        print("\n[⚡Aether⚡] # Ocorreu um erro. Verifique o error_log.txt para detalhes.")

if __name__ == '__main__':
    main()