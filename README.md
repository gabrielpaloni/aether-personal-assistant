# Aether - Command Line Personal Assistant

Aether is a customizable personal assistant built in Python with a cyberpunk aesthetic. It is designed to automate tasks, manage information, and integrate with modern APIs such as Google Drive and Google Gemini.

## Features

* **Unified Dashboard:** Displays a custom banner, a random quote, and your pending to-do list on the main screen.
* **Task Manager:** Direct commands to add, remove, and mark tasks as completed (`todo add`, `todo done`, `todo list`).
* **Google Drive Integration:** Interactive modules to list files in specific folders (`drive`, `spreadsheets`).
* **AI Brain:** Any unrecognized command is automatically sent to Google's AI (Gemini) for a conversational response.
* **Hybrid Voice Mode:** Primarily text-based, but includes a continuous listening mode via the `listen` command, activated by the keyword "Jarvis".
* **Shortcuts:** Quick commands to launch applications and websites instantly.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```



2.  **Create secret key files in the root directory:

   * `credentials.json`: Google Cloud API credentials.

   * `gemini_api_key.txt`: Your API key [Google AI Studio](https://aistudio.google.com/app/apikey).

   * `picovoice_access_key.txt`: Your access key [PicoVoice Console](https://console.picovoice.ai/).



3.  **Configure Scripts:**

   * In `run_drive_selector.py`, set your `FOLDER_ID`.

   * In `spreadsheet_manager.py`, set your `SPREADSHEET_FOLDER_ID`.

   * In `launch_chrome.py`, configure your `CHROME_EXE_PATH` and `PROFILE_DIR`.
