import subprocess
import sys
import json
import os

try:
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    chrome_config = config['chrome_settings']
except (FileNotFoundError, KeyError) as e:
    print(f"Erro ao ler 'config.json' para as configurações do Chrome: {e}")
    sys.exit(1)

CHROME_EXE_PATH = chrome_config['executable_path']
PROFILE_DIR = chrome_config['profile_directory']

if not os.path.exists(CHROME_EXE_PATH):
    print(f"Erro: O caminho para o Chrome não foi encontrado em '{CHROME_EXE_PATH}'")
    print("Verifique o caminho 'executable_path' no seu config.json.")
    sys.exit(1)

if len(sys.argv) > 1:
    url_to_open = sys.argv[1]
else:
    sys.exit()

command = [
    CHROME_EXE_PATH,
    '--new-window',
    f'--profile-directory={PROFILE_DIR}',
    '--start-fullscreen',
    url_to_open
]

subprocess.Popen(command)