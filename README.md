# Aether - Assistente Pessoal de Linha de Comando



Aether é um assistente pessoal customizável construído em Python com uma estética cyberpunk. Ele é projetado para automatizar tarefas, gerenciar informações e se integrar com APIs modernas como Google Drive e Gemini.



\## Funcionalidades

\* \*\*Painel Unificado:\*\* Exibe um banner, uma frase aleatória e a lista de tarefas pendentes na tela principal.

\* \*\*Gerenciador de Tarefas:\*\* Comandos diretos para adicionar, remover e marcar tarefas como feitas (`todo add`, `todo done`, `todo list`).

\* \*\*Integração com Google Drive:\*\* Módulos interativos para listar arquivos em pastas específicas (`drive`, `planilhas`).

\* \*\*Cérebro de IA:\*\* Qualquer comando não reconhecido é enviado para a IA do Google (Gemini) para uma resposta conversacional.

\* \*\*Modo de Voz Híbrido:\*\* Funciona primariamente por texto, mas pode entrar em um modo de escuta contínua com o comando `escutar`, sendo ativado pela palavra-chave "jarvis".

\* \*\*Atalhos:\*\* Comandos para abrir rapidamente aplicativos e sites.



\## Configuração



1\.  \*\*Instale as dependências:\*\*

&nbsp;   ```

&nbsp;   pip install -r requirements.txt

&nbsp;   ```



2\.  \*\*Crie os arquivos de chaves secretas\*\* na pasta principal:

&nbsp;   \* `credentials.json`: Credencial da API do Google (siga o guia do Google Cloud).

&nbsp;   \* `gemini\_api\_key.txt`: Sua chave de API do \[Google AI Studio](https://aistudio.google.com/app/apikey).

&nbsp;   \* `picovoice\_access\_key.txt`: Sua chave de acesso do \[PicoVoice Console](https://console.picovoice.ai/).



3\.  \*\*Configure os Scripts:\*\*

&nbsp;   \* Em `run\_drive\_selector.py`, configure a `FOLDER\_ID`.

&nbsp;   \* Em `spreadsheet\_manager.py`, configure a `SPREADSHEET\_FOLDER\_ID`.

&nbsp;   \* Em `launch\_chrome.py`, configure `CHROME\_EXE\_PATH` e `PROFILE\_DIR`.

