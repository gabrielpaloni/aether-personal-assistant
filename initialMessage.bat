@echo off
:: Garante que estamos na pasta certa
cd /d "%~dp0"

:: Inicia o agente principal em Python
py main_agent.py

:: Verifica o código de saída (ERRORLEVEL) do script Python
:: Se o código for 99, executa o comando para fechar o CMD
if %ERRORLEVEL% == 99 (
    exit
)