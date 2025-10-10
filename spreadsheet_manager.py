import os
import sys
import json
import subprocess
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime

def get_credentials(creds_path, token_path, scopes):
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, scopes)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                creds = None
        if not creds:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, scopes)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    return creds

def list_all_files_in_folder(service, folder_id):
    query = f"'{folder_id}' in parents and trashed=false"
    results = service.files().list(
        q=query, pageSize=100, orderBy='modifiedTime desc',
        fields="files(id, name, webViewLink)",
        includeItemsFromAllDrives=True, supportsAllDrives=True
    ).execute()
    return results.get('files', [])

def get_current_month_key(month_map):
    now = datetime.now()
    month_abbr = now.strftime('%b').lower()
    year_short = str(now.year % 100)
    return f"{month_map.get(month_abbr, '')} {year_short}"

def main():
    print("\n--- 📊 Gerenciador de Planilhas do Aether 📊 ---")
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        sm_config = config['spreadsheet_manager']
        gdrive_config = config['google_drive_api']
        loc_config = config['localization']

        SHEETS_GIDS = sm_config['sheet_gids']
        SPREADSHEET_FOLDER_ID = sm_config['folder_id']
        MONTH_MAP = loc_config['month_map_pt']
        
        SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
        TOKEN_PATH = os.path.join(SCRIPT_DIR, gdrive_config['token_file'])
        CREDS_PATH = os.path.join(SCRIPT_DIR, gdrive_config['credentials_file'])
        SCOPES = gdrive_config['scopes']

    except (FileNotFoundError, KeyError) as e:
        print(f"[ERRO CRÍTICO] # Falha ao ler o 'config.json': {e}")
        sys.exit(1)

    try:
        creds = get_credentials(CREDS_PATH, TOKEN_PATH, SCOPES)
        drive_service = build('drive', 'v3', credentials=creds)
        
        files = list_all_files_in_folder(drive_service, SPREADSHEET_FOLDER_ID)
        if not files:
            print("\nNenhum arquivo encontrado na pasta configurada.")
            return
            
        print("\nEncontrei os seguintes arquivos na sua pasta de trabalho:\n")
        for i, file in enumerate(files):
            print(f"  [{i+1}] - {file.get('name')}")
        
        choice_str = input("\nEscolha o NÚMERO do arquivo (ou Enter para cancelar): ").strip()
        if not choice_str:
            return

        choice_idx = int(choice_str) - 1
        if 0 <= choice_idx < len(files):
            chosen_file = files[choice_idx]
            file_name = chosen_file.get('name')
            file_url = chosen_file.get('webViewLink')
            
            gid = None
            if file_name in SHEETS_GIDS:
                if file_name == "MENTORIAS AGOSTO 2025":
                    gid = SHEETS_GIDS[file_name].get("Gabriel")
                else:
                    month_key = get_current_month_key(MONTH_MAP)
                    gid = SHEETS_GIDS[file_name].get(month_key)

            final_url = file_url
            if gid:
                base_url = file_url.split('/edit')[0]
                final_url = f"{base_url}/edit#gid={gid}"
            
            print("\nAbrindo no navegador...")
            subprocess.run(['py', 'launch_chrome.py', final_url], stdin=subprocess.DEVNULL)
        else:
            print("⚠️ Número de arquivo inválido.")
            
    except (ValueError, IndexError):
        print("⚠️ Digite um número válido ou apenas Enter para cancelar.")
    except HttpError as err:
        print(f"Ocorreu um erro na API do Google. Detalhe: {err}")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

if __name__ == '__main__':
    main()