from rich.layout import Layout
from rich.panel import Panel
from rich.align import Align
from rich.table import Table
from rich.live import Live
from rich.console import Console, Group
import os
import random
import subprocess
import time
import sys
from datetime import datetime, timedelta
import json

""" Imports de voz e teclado """
import speech_recognition as sr
import pyttsx3
import pvporcupine
import pyaudio
import struct
import keyboard

""" Lib rich """

""" Import para limpar buffer do teclado """
try:
    import msvcrt
except ImportError:
    msvcrt = None

""" CARREGAMENTO DAS CONFIGURAÇÕES """
try:
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
except FileNotFoundError:
    print("[ERRO CRÍTICO] # Arquivo 'config.json' não encontrado. Certifique-se de que ele existe.")
    sys.exit(1)
except json.JSONDecodeError:
    print("[ERRO CRÍTICO] # Arquivo 'config.json' está mal formatado.")
    sys.exit(1)

# Configurações do Agente
AGENT_NAME = config['agent_settings']['name']
PROMPT = config['agent_settings']['prompt_prefix']
WAKE_WORD = config['agent_settings']['wake_word']

# Configurações de Voz e API
VOICE_SPEED_ADJUSTMENT = config['voice_settings']['speed_adjustment']
PICOVOICE_ACCESS_KEY = config['api_keys']['picovoice_access_key']
PREFERRED_VOICE = config['voice_settings']['preferred_voice']

# Nomes de arquivos
TODOLIST_FILENAME = config['file_paths']['todolist']

# Caminhos de aplicativos e links
APP_PATHS = config['app_shortcuts']


""" INICIALIZAÇÃO DA VOZ """
try:
    engine = pyttsx3.init()
    rate = engine.getProperty('rate')
    engine.setProperty('rate', rate + VOICE_SPEED_ADJUSTMENT)
    voices = engine.getProperty('voices')
    for voice in voices:
        if PREFERRED_VOICE in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break
except Exception as e:
    engine = None
    print(
        f"[AVISO] Não foi possível inicializar o motor de voz (pyttsx3): {e}")

    """ INICIALIZAÇÃO DA VOZ """
try:
    engine = pyttsx3.init()
    rate = engine.getProperty('rate')
    engine.setProperty('rate', rate + VOICE_SPEED_ADJUSTMENT)
    voices = engine.getProperty('voices')
    for voice in voices:
        if 'brazil' in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break
except Exception as e:
    engine = None
    print(
        f"[AVISO] Não foi possível inicializar o motor de voz (pyttsx3): {e}")
try:
    with open('picovoice_access_key.txt', 'r') as f:
        PICOVOICE_ACCESS_KEY = f.read().strip()
except FileNotFoundError:
    print(f"[ERRO CRÍTICO] # Arquivo 'picovoice_access_key.txt' não encontrado.")
    sys.exit(1)

ASCII_BANNER = """░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
░░░░░░░░░░░░░░░░░░░░░░██████░░███████░███░░░░███░░░░░██░░░░██░██░███░░░░██░██████░░░██████░░░░░░░░░███████░██░░░░░░░██████░░██░░░░░██░██░░░░░░░░░░░░░░░░░░░░░░
░░░░░░░░░░░░░░░░░░░░░░██░░░██░██░░░░░░████░░████░░░░░██░░░░██░██░████░░░██░██░░░██░██░░░░██░░░░░░░░██░░░░░░██░░░░░░██░░░░██░██░░░░░██░██░░░░░░░░░░░░░░░░░░░░░░
░░░░░░░░░░░░░░░░░░░░░░██████░░█████░░░██░████░██░░░░░██░░░░██░██░██░██░░██░██░░░██░██░░░░██░░░░░░░░█████░░░██░░░░░░██░░░░██░██░░█░░██░██░░░░░░░░░░░░░░░░░░░░░░
░░░░░░░░░░░░░░░░░░░░░░██░░░██░██░░░░░░██░░██░░██░░░░░░██░░██░░██░██░░██░██░██░░░██░██░░░░██░░░░░░░░██░░░░░░██░░░░░░██░░░░██░██░███░██░░░░░░░░░░░░░░░░░░░░░░░░░
░░░░░░░░░░░░░░░░░░░░░░██████░░███████░██░░░░░░██░░░░░░░████░░░██░██░░░████░██████░░░██████░░█░░░░░░██░░░░░░███████░░██████░░░███░███░░██░░░░░░░░░░░░░░░░░░░░░░
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
"""

""" TODAS DEFs """


def flush_input_buffer():
    if msvcrt:
        while msvcrt.kbhit():
            msvcrt.getch()

def speak(text, also_print=True):
    if also_print:
            print(f"\n[⚡{AGENT_NAME}⚡] # {text}")
    if engine:
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"[ERRO DE FALA] # {e}")

def respond(text, mode='text'):
    print(f"\n[⚡{AGENT_NAME}⚡] # {text}")
    if mode == 'voice':
        speak(text, also_print=False)

def listen_for_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print(f"\n[⚡{AGENT_NAME}⚡] # Sim? Estou ouvindo...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
    try:
        command = recognizer.recognize_google(audio, language='pt-BR')
        print(f"   (Você disse): {command}")
        return command
    except (sr.UnknownValueError, sr.WaitTimeoutError):
        return "ERRO_STT: Nao entendi"
    except sr.RequestError:
        return "ERRO_STT: Sem conexao"

def get_random_line(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            return random.choice(lines).strip()
        except:
            return "⚡ Flow Core Active ⚡"

def clear_screen():
        os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
        clear_screen()
        print(ASCII_BANNER)
        print(get_random_line('phrases.txt'))
        print()
        tasks = load_tasks()
        pending_tasks = [t for t in tasks if t['status'] != 'Realizada']
        if pending_tasks:
            console = Console()
            console.print(generate_tasks_table())
            print()

def show_help(mode='text'):
        respond("Aqui estão os comandos que eu conheço:", mode=mode)
        print("""
    ================================= AJUDA =================================

        planilhas             - Acessa o menu de planilhas de trabalho
        todo list             - Mostra todas as tarefas.
        todo add <tarefa>     - Adiciona uma nova tarefa à lista.
        todo done <numero>    - Marca uma tarefa PENDENTE como realizada.
        todo del <numero>     - Remove uma tarefa PENDENTE da lista.
        todo clear            - Remove TODAS as tarefas já realizadas.
        steam                 - Abre a Steam
        faculdade             - Github do Vinícius
        class plan            - Abre meus planos de aula
        app cna               - Abre o App CNA
        cna box               - Abre o BOX
        atualizar             - Atualiza a exibição do painel de tarefas.
        drive                 - Abre o menu de busca no Drive
        escutar               - Ativa o modo de escuta por voz
        mysql                 - Abre o cliente MySQL
        clear                 - Limpa a tela e exibe o painel de tarefas.
        desligar              - Desliga o computador
        sair                  - Sair do agente
        
    =========================================================================
        """)

def run_spreadsheet_manager():
        subprocess.run(['py', 'spreadsheet_manager.py'])

def run_drive_selector():
        respond("Iniciando módulo de busca no Drive.", mode='text')
        print("-" * 60)
        subprocess.run(['py', 'run_drive_selector.py'])
        print("-" * 60)
        respond("Módulo de busca finalizado.", mode='text')

def run_ai_query(query, mode):
        result = subprocess.run(
            ['py', 'ask_gemini.py', query], capture_output=True, text=True, errors='ignore')
        response_text = result.stdout.strip()
        if response_text.startswith("ERRO_IA:"):
            respond("Desculpe, ocorreu um erro ao contatar a IA.", mode=mode)
        elif response_text:
            respond(response_text, mode=mode)
        else:
            respond("A IA não forneceu uma resposta.", mode=mode)

def run_mysql():
        print()
        user = input(f"[⚡{AGENT_NAME}⚡] # Digite o usuário do MySQL: ")
        port = input(f"[⚡{AGENT_NAME}⚡] # Digite a porta (Enter para 3306): ")
        if not port:
            port = "3306"
        program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
        mysql_path = config['mysql_settings']['executable_path']

        if not os.path.exists(mysql_path):
            print(
                f"\n[ERRO] # Não consegui encontrar o executável do MySQL no caminho esperado.")
            print(f"   Verifique se o MySQL está instalado em: {mysql_path}")
            return

        print(f"\n[⚡{AGENT_NAME}⚡] # Abrindo cliente MySQL...")
        try:
            subprocess.call([mysql_path, f"-u{user}", "-p", f"-P{port}"])
            print(f"\n[⚡{AGENT_NAME}⚡] # Cliente MySQL fechado.")
        except Exception as e:
            print(f"\n[ERRO] # Falha ao executar o comando MySQL: {e}")

def refresh_tasks_display():
        console = Console()
        print()
        console.print(generate_tasks_table())
        print(f"Use o comando 'clear' para limpar a tela ou 'ajuda' para ver os comandos.")

def process_command(command_full, mode='text'):
        command_full_lower = command_full.lower()
        needs_redraw = False
        message = ""

        if command_full_lower in APP_PATHS:
            print(f"\n[⚡{AGENT_NAME}⚡] # Abrindo '{command_full_lower}'...")
            path = APP_PATHS[command_full_lower]
            if path.startswith("http"):
                subprocess.run(['py', 'launch_chrome.py', path],
                               stdin=subprocess.DEVNULL)
            else:
                os.startfile(path)
            return "continue", False

        parts = command_full.split()
        command = parts[0].lower()
        args = parts[1:]

        if command in ["sair", "tchau", "desconectar"]:
            respond(get_random_line('farewells.txt'), mode=mode)
            time.sleep(2)
            return "exit"

        elif command == "ajuda":
            show_help(mode=mode)

        elif command in ["clear", "atualizar"]:
            print_header()
            return "continue"

        elif command in ["desligar", "desligar computador"]:
            respond("Confirmado. Desligando o sistema em 5 segundos.", mode=mode)
            time.sleep(5)
            os.system("shutdown /s /f /t 0")
            return "exit"

        elif command == "drive" or command == "alpoo":
            run_drive_selector()
            return "continue"

        elif command == "planilhas":
            run_spreadsheet_manager()
            return "continue"

        elif command == "mysql":
            run_mysql()
            return "continue"

        elif command == "todo":
            if not args:
                message = "Comando 'todo' incompleto. Use 'add', 'done', 'del', 'list', ou 'clear'."
            else:
                sub_command = args[0].lower()
                if sub_command == "add":
                    description = " ".join(args[1:])
                    message = add_task(description)
                elif sub_command in ["done", "feito"]:
                    if len(args) < 2:
                        message = "Por favor, especifique o número da tarefa (ex: todo done 1)."
                    else:
                        message = mark_task_done(args[1])
                elif sub_command in ["del", "remover"]:
                    if len(args) < 2:
                        message = "Por favor, especifique o número da tarefa (ex: todo del 1)."
                    else:
                        message = remove_task(args[1])
                elif sub_command == "clear":
                    message = clear_completed_tasks()
                    needs_redraw = True
                elif sub_command in ["list", "all"]:
                    show_all_tasks()
                else:
                    message = f"Sub-comando '{sub_command}' desconhecido para 'todo'."

            if message:
                respond(message, mode=mode)
        else:
            run_ai_query(command_full, mode=mode)

        if needs_redraw:
            print_header()

        return "continue"

def start_listening_mode():
        porcupine = None
        pa = None
        audio_stream = None
        try:
            porcupine = pvporcupine.create(
                access_key=PICOVOICE_ACCESS_KEY, keywords=[WAKE_WORD])
            pa = pyaudio.PyAudio()
            audio_stream = pa.open(rate=porcupine.sample_rate, channels=1,
                                   format=pyaudio.paInt16, input=True, frames_per_buffer=porcupine.frame_length)
            respond(
                f"Modo de escuta ativado. Diga '{WAKE_WORD}' para me chamar, ou pressione Enter para voltar.", mode='voice')

            while True:
                print(
                    f"[STATUS] Ouvindo por '{WAKE_WORD}'...", end='\r', flush=True)
                pcm = audio_stream.read(
                    porcupine.frame_length, exception_on_overflow=False)
                pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
                keyword_index = porcupine.process(pcm)

                if keyword_index >= 0:
                    print(" " * 60, end='\r')
                    print(
                        f"--- Palavra de ativação '{WAKE_WORD}' detectada! ---")
                    command_voice = listen_for_command()

                    if "ERRO_STT" in command_voice:
                        respond(command_voice.replace(
                            "ERRO_STT: ", ""), mode='voice')
                    elif process_command(command_voice, mode='voice') == "exit":
                        sys.exit(99)

                if keyboard.is_pressed('enter'):
                    print(" " * 60, end='\r')
                    respond("Modo de texto ativado.", mode='voice')
                    break
        finally:
            if audio_stream:
                audio_stream.close()
            if pa:
                pa.terminate()
            if porcupine:
                porcupine.delete()

def get_last_modified_date(filepath):
        try:
            timestamp = os.path.getmtime(filepath)
            mod_date = datetime.fromtimestamp(timestamp)
            return mod_date.strftime("%d/%m/%Y")
        except FileNotFoundError:
            return "desconhecida"

def initial_interaction():
        last_update_date = get_last_modified_date(__file__)

        while True:
            prompt_text = f"[⚡{AGENT_NAME}⚡] # Quer que eu mostre os comandos da última atualização ({last_update_date})? (sim/nao): "
            answer = input(prompt_text).lower().strip()
            print()

            if answer in ['sim', 's']:
                show_help('text')
                print(
                    f"\n[⚡{AGENT_NAME}⚡] # Só lembrando que ainda estou em desenvolvimento.")

                while True:
                    more_help = input(
                        f"[⚡{AGENT_NAME}⚡] # Tem alguma sugestão? (sim/nao): ").lower().strip()
                    print()

                    if more_help in ['sim', 's']:
                        suggestion = input(
                            f"[⚡{AGENT_NAME}⚡] # Digite sua sugestão ou pedido: ")
                        suggestions_file = config['file_paths']['suggestions']
                        with open(suggestions_file, 'a', encoding='utf-8') as f:
                            f.write(suggestion + '\n')
                        respond(
                            "Obrigado! Sua sugestão foi registrada.", mode='text')
                        break

                    elif more_help in ['nao', 'n']:
                        respond(
                            "Perfeito! Tenha uma ótima experiência com meu sistema!", mode='text')
                        break

                    else:
                        respond(
                            "Entrada inválida. Por favor, digite 'sim' ou 'nao'.", mode='text')
                break

            elif answer in ['nao', 'n']:
                respond("Perfeito! Caso precise, digite 'ajuda'.", mode='text')
                break

            else:
                respond(
                    "Entrada inválida. Por favor, digite 'sim' ou 'nao'.", mode='text')
        print()

def load_tasks():
        if not os.path.exists(TODOLIST_FILENAME):
            return []

        try:
            if os.path.getsize(TODOLIST_FILENAME) > 0:
                with open(TODOLIST_FILENAME, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except (json.JSONDecodeError, FileNotFoundError):
            return []

def save_tasks(tasks):
        with open(TODOLIST_FILENAME, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, indent=4, ensure_ascii=False)

def get_time_remaining(due_at_str):
        if not due_at_str:
            return "[dim]Sem prazo[/dim]"
        due_at = datetime.fromisoformat(due_at_str)
        now = datetime.now()

        if now > due_at:
            return "[bold red]ATRASADA[/bold red]"
        delta = due_at - now
        days, hours, rem = delta.days, delta.seconds // 3600, delta.seconds % 3600
        minutes, _ = divmod(rem, 60)

        return f"[yellow]{days}d {hours:02d}h {minutes:02d}m[/yellow]"

def show_all_tasks():
        console = Console()
        table = Table(title="--- 📝 Histórico Completo de Tarefas 📝 ---",
                      expand=True, border_style="dim cyan")
        table.add_column("Tarefa", style="magenta")
        table.add_column("Status", justify="center")
        tasks = load_tasks()

        tasks = load_tasks()
        if not tasks:
            table.add_row("Nenhuma tarefa no histórico!", "-")
        else:
            for i, task in enumerate(tasks):
                status = task['status']
                description = task['description']
                if status == "Realizada":
                    table.add_row(
                        f"[strike dim]{description}[/strike dim]", "[blue]Realizada[/blue]")
                else:
                    table.add_row(description, "[yellow]Pendente[/yellow]")

                if i < len(tasks) - 1:
                    table.add_section()

        console.print(table)

def add_task(description):
        if not description:
            return "Nenhuma tarefa adicionada. Tente: todo add <descrição>"
        tasks = load_tasks()
        due_date = None

        while True:
            answer = input(
                f"[⚡{AGENT_NAME}⚡] # Deseja adicionar um prazo para esta tarefa? (sim/nao): ").lower().strip()
            if answer in ['sim', 's']:
                try:
                    days_str = input(f"    - Digite os dias (Enter para 0): ")
                    hours_str = input(
                        f"    - Digite as horas (Enter para 0): ")
                    minutes_str = input(
                        f"    - Digite os minutos (Enter para 0): ")

                    days = int(days_str) if days_str else 0
                    hours = int(hours_str) if hours_str else 0
                    minutes = int(minutes_str) if minutes_str else 0

                    if days == 0 and hours == 0 and minutes == 0:
                        print(f"[AVISO] # Nenhum prazo foi adicionado.")
                        due_date = None
                    else:
                        time_delta = timedelta(
                            days=days, hours=hours, minutes=minutes)
                        due_date = datetime.now() + time_delta
                    break

                except ValueError:
                    print(
                        "\n[ERRO] # Por favor, digite apenas números para o prazo. Tente novamente.")

            elif answer in ['nao', 'n']:
                print(f"[INFO] # Tarefa adicionada sem prazo.")
                break
            else:
                print(
                    "\n[ERRO] # Resposta inválida. Por favor, digite 'sim' ou 'nao'.")

        new_task = {
            "description": description,
            "status": "Pendente",
            "created_at": datetime.now().isoformat(),
            "due_at": due_date.isoformat() if due_date else None
        }

        tasks.append(new_task)
        save_tasks(tasks)
        confirmation_message = f"Tarefa '{description}' adicionada com sucesso"

        if due_date:
            formatted_due_date = due_date.strftime('%d/%m/%Y às %H:%M')
            confirmation_message += f", com prazo para {formatted_due_date}."
        else:
            confirmation_message += ", sem prazo definido."

        print()
        return confirmation_message

def mark_task_done(task_number):
        tasks = load_tasks()
        pending_tasks = [t for t in tasks if t['status'] != 'Realizada']

        try:
            index = int(task_number) - 1
            if 0 <= index < len(pending_tasks):
                task_to_mark = pending_tasks[index]

                for original_task in tasks:
                    if original_task['created_at'] == task_to_mark['created_at']:
                        original_task['status'] = 'Realizada'
                        break

                save_tasks(tasks)
                return f"Tarefa '{task_to_mark['description']}' marcada como realizada!"
            else:
                return "Número de tarefa inválido. Verifique o número na lista de pendentes."
        except ValueError:
            return "Entrada inválida. Use um número (ex: todo done 1)."

def remove_task(task_number):
        tasks = load_tasks()
        pending_tasks = [t for t in tasks if t['status'] != 'Realizada']

        try:
            index = int(task_number) - 1
            if 0 <= index < len(pending_tasks):
                task_to_remove = pending_tasks[index]

                updated_tasks = [
                    t for t in tasks if t['created_at'] != task_to_remove['created_at']]

                save_tasks(updated_tasks)
                return f"Tarefa '{task_to_remove['description']}' removida com sucesso."
            else:
                return "Número de tarefa inválido. Verifique o número na lista de pendentes."
        except ValueError:
            return "Entrada inválida. Use um número (ex: todo del 1)."

def clear_completed_tasks():
        tasks = load_tasks()
        pending_tasks = [t for t in tasks if t['status'] != 'Realizada']

        num_cleared = len(tasks) - len(pending_tasks)

        if num_cleared == 0:
            return "Nenhuma tarefa realizada para limpar."

        save_tasks(pending_tasks)
        return f"{num_cleared} tarefa(s) realizada(s) foi(ram) removida(s) do histórico."

def generate_tasks_table():
        table = Table(title="---------------------------------------------- 📝 Painel de Tarefas 📝 ----------------------------------------------",
                      expand=True, border_style="dim cyan")
        table.add_column("#", justify="center", style="cyan", no_wrap=True)
        table.add_column("Tarefa", style="magenta", justify="center")
        table.add_column("Status", justify="center")
        table.add_column("Prazo", justify="center")

        tasks = load_tasks()

        if not tasks:
            table.add_row("-", "Nenhuma tarefa na lista!", "-", "-")
        else:
            pending_tasks = [t for t in tasks if t['status'] != 'Realizada']
            done_tasks = [t for t in tasks if t['status'] == 'Realizada']

            if not pending_tasks:
                table.add_row("-", "Nenhuma tarefa pendente!", "🎉", "-")

            for i, task in enumerate(pending_tasks):
                description = task['description']
                time_info = get_time_remaining(task.get('due_at'))

                if "ATRASADA" in time_info:
                    table.add_row(str(i + 1), description,
                                  "[bold red]ATRASADA[/bold red]", "---")
                else:
                    table.add_row(str(i + 1), description,
                                  "[yellow]Pendente[/yellow]", time_info)
                if i < len(tasks) - 1:
                    table.add_section()

            if pending_tasks and done_tasks:
                table.add_section()
            for task in done_tasks:
                description = f"[dim strike]{task['description']}[/dim strike]"
                status = "[blue]Realizada[/blue]"
                table.add_row("-", description, status, "[dim]Concluído[/dim]")

        return table

""" LÓGICA PRINCIPAL """
if __name__ == "__main__":
    os.system('') 
    os.system('color 0A')
    print_header()
    respond("Olá, sou Aether, seu assistente no CyberUniverse. Bem-vindo!")
    
    initial_interaction()

    while True:
        try:
            command_text = input(PROMPT).strip()
            if not command_text:
                continue

            print()
            command_lower = command_text.lower()

            if command_lower == "escutar":
                start_listening_mode()
                flush_input_buffer()
            else:
                if process_command(command_text, mode='text') == "exit":
                    break

        except (KeyboardInterrupt, SystemExit):
            print("\n\n[⚡AETHER⚡] # Desligando...")
            break
        except Exception as e:
            respond(f"Ocorreu um erro inesperado.")
            print(f"(Detalhe do erro): {e}")
