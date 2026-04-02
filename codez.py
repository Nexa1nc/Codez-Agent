import os
import requests
import subprocess
import json
import psutil
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

# Inizializzazione della console
console = Console()

def logo():
    """Pulisce lo schermo e stampa il logo ASCII."""
    os.system('cls' if os.name == 'nt' else 'clear')
    ascii_art = r"""
 [bold cyan]
  /$$$$$$                  /$$                     
 /$$__  $$                | $$                     
| $$  \__/  /$$$$$$   /$$$$$$$  /$$$$$$  /$$$$$$$$ 
| $$       /$$__  $$ /$$__  $$ /$$__  $$|____ /$$/ 
| $$      | $$  \ $$| $$  | $$| $$$$$$$$   /$$$$/  
| $$    $$| $$  \ $$| $$  | $$| $$_____/  /$$__/   
|  $$$$$$/|  $$$$$$/|  $$$$$$$|  $$$$$$$ /$$$$$$$$ 
 \______/  \______/  \_______/ \_______/|________/ 
 [/bold cyan]
    """
    console.print(Panel(ascii_art, border_style="cyan", title="CODEZ AGENT v0.2.0"))

def system_doctor():
    """Monitora le risorse del sistema (Principio Budget 0)."""
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    
    if ram < 70:
        status = "[bold green]OTTIMO[/bold green]"
        color = "green"
    elif ram < 90:
        status = "[bold yellow]ATTENZIONE[/bold yellow]"
        color = "yellow"
    else:
        status = "[bold red]CRITICO (RAM QUASI PIENA)[/bold red]"
        color = "red"
    
    info = f"💻 [bold]CPU:[/bold] {cpu}%\n🧠 [bold]RAM:[/bold] {ram}%\n📊 [bold]Stato:[/bold] {status}"
    console.print(Panel(info, title="🏥 System Doctor", border_style=color))

def configura_sessione():
    """Scansione automatica modelli (Principio Accessibilità)."""
    console.print("\n[italic]Digita 'ollama' o la tua API Key[/italic]")
    key = input("Chiave: ").strip()
    
    if key.lower() == "ollama":
        prov, url = "Ollama", "http://localhost:11434/v1"
        # Scansione automatica modelli locali
        try:
            r = requests.get("http://localhost:11434/api/tags", timeout=2)
            modelli = [m['name'] for m in r.json()['models']]
        except:
            modelli = ["llama3", "phi3", "mistral"]
    else:
        prov, url = "Cloud AI", "https://api.groq.com/openai/v1" if key.startswith("gsk_") else "https://api.openai.com/v1"
        modelli = ["gpt-4o", "llama3-70b-8192", "mixtral-8x7b-32768"]

    console.print("\n[bold yellow]Modelli Rilevati:[/bold yellow]")
    for i, m in enumerate(modelli):
        console.print(f"{i+1}. {m}")
    
    scelta = int(Prompt.ask("\nScegli numero", default="1")) - 1
    return key, prov, url, modelli[scelta]

def esegui_comando(comando):
    """Esegue comandi dopo conferma."""
    console.print(f"\n[bold orange3]PROPOSTA COMANDO:[/bold orange3] [white on blue] {comando} [/white on blue]")
    if Prompt.ask("Eseguire?", choices=["y", "n"], default="y") == "y":
        res = subprocess.run(comando, shell=True, capture_output=True, text=True)
        return f"--- OUTPUT ---\n{res.stdout}\n{res.stderr}"
    return "Annullato."

def main():
    logo()
    key, prov, url, mod = configura_sessione()
    
    console.print(f"\n[bold green]Codez Attivo! ({mod})[/bold green]")
    console.print("[dim]/status (PC check) | /explain (Spiega ultimo comando) | /stop[/dim]\n")

    ultimo_comando_proposto = ""

    while True:
        user_input = input(f"({mod}) > ").strip()
        
        if not user_input: continue
        
        if user_input == "/stop": break
        
        if user_input == "/status":
            system_doctor()
            continue

        if user_input == "/explain":
            if not ultimo_comando_proposto:
                console.print("[yellow]Nessun comando da spiegare ancora![/yellow]")
                continue
            user_input = f"Spiegami in modo semplice cosa fa questo comando: {ultimo_comando_proposto}"
            console.print("[italic cyan]Chiedo spiegazioni all'IA...[/italic cyan]")

        # Logica AI
        prompt_sistema = (
            "Sei Codez. Se devi agire sul PC scrivi 'COMMAND: ' seguito dal comando. "
            "Sii breve e tecnico. Se l'utente chiede spiegazioni (/explain), sii educativo."
        )
        
        payload = {
            "model": mod,
            "messages": [
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": user_input}
            ]
        }
        
        try:
            h = {"Authorization": f"Bearer {key}"} if key.lower() != "ollama" else {}
            r = requests.post(f"{url}/chat/completions", headers=h, json=payload)
            risposta = r.json()['choices'][0]['message']['content']

            if "COMMAND: " in risposta:
                cmd = risposta.split("COMMAND: ")[1].strip().replace('`', '')
                ultimo_comando_proposto = cmd
                esito = esegui_comando(cmd)
                console.print(f"[dim]{esito}[/dim]")
            else:
                console.print(f"\n[bold cyan]AI:[/bold cyan] {risposta}\n")
                
        except Exception as e:
            console.print(f"[red]Errore: {e}[/red]")

if __name__ == "__main__":
    main()