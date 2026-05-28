#!/usr/bin/env python3
"""
Validação de Ambiente - Verifica se tudo está pronto para executar
"""

import sys
import importlib
import subprocess
import os
from pathlib import Path


def check_python_version():
    """Verifica versão do Python."""
    version = sys.version_info
    print(f"Python: {version.major}.{version.minor}.{version.micro}", end=" ")
    
    if version.major >= 3 and version.minor >= 11:
        print("✅")
        return True
    else:
        print("❌ (Requer 3.11+)")
        return False


def check_module(module_name, package_name=None):
    """Verifica se módulo Python está instalado."""
    if package_name is None:
        package_name = module_name
    
    try:
        importlib.import_module(module_name)
        print(f"{package_name}: ✅")
        return True
    except ImportError:
        print(f"{package_name}: ❌")
        return False


def check_mosquitto():
    """Verifica se Mosquitto está instalado."""
    try:
        result = subprocess.run(
            ["mosquitto", "--help"],
            capture_output=True,
            timeout=2
        )
        print("Mosquitto: ✅")
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print("Mosquitto: ❌")
        return False


def check_pdflatex():
    """Verifica se pdflatex está instalado (opcional)."""
    try:
        result = subprocess.run(
            ["pdflatex", "--version"],
            capture_output=True,
            timeout=2
        )
        print("pdflatex (LaTeX): ✅")
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print("pdflatex (LaTeX): ⚠️  (opcional)")
        return False


def check_files():
    """Verifica se arquivos principais existem."""
    files_to_check = [
        "ring_buffer.py",
        "inefficient_buffer.py",
        "producer.py",
        "consumer.py",
        "mqtt_client.py",
        "benchmark.py",
        "plot_graphs.py",
        "main.py",
        "requirements.txt",
        "dashboard/node-red.json",
        "relatorio/relatorio.tex"
    ]
    
    all_ok = True
    for file in files_to_check:
        if os.path.exists(file):
            print(f"  {file}: ✅")
        else:
            print(f"  {file}: ❌")
            all_ok = False
    
    return all_ok


def main():
    """Função principal."""
    
    print("\n" + "="*70)
    print("  VALIDAÇÃO DE AMBIENTE - Sistema de Telemetria")
    print("="*70 + "\n")
    
    print("📋 VERIFICAÇÕES:\n")
    
    print("1️⃣  Python:")
    python_ok = check_python_version()
    
    print("\n2️⃣  Módulos Python:")
    modules_ok = True
    modules_ok &= check_module("paho.mqtt", "paho-mqtt")
    modules_ok &= check_module("matplotlib")
    modules_ok &= check_module("pandas")
    modules_ok &= check_module("psutil")
    
    print("\n3️⃣  Ferramentas Externas:")
    mosquitto_ok = check_mosquitto()
    pdflatex_ok = check_pdflatex()
    
    print("\n4️⃣  Arquivos do Projeto:")
    files_ok = check_files()
    
    print("\n" + "="*70)
    print("  RESUMO")
    print("="*70 + "\n")
    
    status = {
        "Python 3.11+": python_ok,
        "Módulos Python": modules_ok,
        "Mosquitto": mosquitto_ok,
        "Arquivos": files_ok,
    }
    
    for item, ok in status.items():
        symbol = "✅" if ok else "❌"
        print(f"{symbol} {item}")
    
    print("\n" + "="*70)
    
    if python_ok and modules_ok and files_ok:
        if mosquitto_ok:
            print("✅ AMBIENTE PRONTO! Você pode executar o projeto.")
        else:
            print("⚠️  Ambiente quase pronto! Instale Mosquitto:")
            print("    Windows: https://mosquitto.org/download/")
            print("    Linux: sudo apt install mosquitto")
    else:
        print("❌ AMBIENTE INCOMPLETO. Corrija os problemas acima.")
        print("\nSolução rápida:")
        print("  pip install -r requirements.txt")
    
    print("="*70 + "\n")
    
    if mosquitto_ok:
        print("Próximo passo: python quick_test.py\n")
    else:
        print("Próximo passo:")
        print("  1. Instale Mosquitto")
        print("  2. Execute: mosquitto")
        print("  3. Em outro terminal: python quick_test.py\n")


if __name__ == "__main__":
    main()
