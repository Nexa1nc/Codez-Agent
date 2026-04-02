import os
import requests
import subprocess
import json
import psutil
import datetime
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

# --- CONFIGURAZIONE GLOBALE ---
VERSIONE_ATTUALE = "0.2.7"
console = Console()

def logo():
    """Pulisce lo schermo e stampa il logo ASCII di Codez."""
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
    console.print(Panel(ascii_art, border_style="cyan", title=f"CODEZ AGENT v{VERSIONE_ATTUALE}"))

def check_updates():
    """Controlla se esiste una nuova versione su PyPI (Accessibilità)."""
    try:
        # Interroga l'API di PyPI per il tuo pacchetto
        response = requests.get("https://pypi.org/pypi/Codez-Agent/json", timeout=1.5)
        ultima_v = response.json()["info"]["version"]
        if ultima_v != VERSIONE_ATTUALE:
            console.print(Panel(f"🚀 [bold yellow]Nuova versione disponibile: {ultima_v}[/bold yellow]\n"
                                f"Stai usando la {VERSIONE_ATTUALE}.\n"
                                f"Aggiorna con: [cyan]pip install --upgrade Codez-Agent[/cyan]", 
                                title="Update Check", border_style="yellow"))
        else:
            log_msg("INFO", "Il software è aggiornato.")
    except:
        pass # Se offline o pacchetto non trovato, proseguiamo

def log_msg(tipo, messaggio):
    """Stampa messaggi con tag colorati per migliorare la leggibilità."""
    colori = {
        "INFO": "[bold blue][INFO][/bold blue]",
        "SUCCESS": "[bold green][SUCCESS][/bold green]",
        "WARNING": "[bold yellow][WARNING][/bold yellow]",
        "ERROR": "[bold red][ERROR][/bold red]"
    }
    tag = colori.get(tipo, "[INFO]")
    console.print(f"{tag} {messaggio}")

def scrivi_log_md(comando, esito):
    """Salva la cronologia in formato Markdown (Open Source & Educativo)."""
    orario = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    file_log = "CODEZ_HISTORY.md"
    
    # Puliamo l'esito PRIMA di metterlo nella f-string per evitare l'errore del backslash
    esito_pulito = esito[:200].strip().replace('\n', ' ')
    
    # Crea intestazione se il file è nuovo
    if not os.path.exists(file_log):
        with open(file_log, "w", encoding="utf-8") as f:
            f.write("# 📜 Diario di Bordo Codez Agent\n\n")
            f.write("In questo file trovi tutti i comandi che hai imparato a usare.\n\n")

    with open(file_log, "a", encoding="utf-8") as f:
        f.write(f"### 🕒 Sessione: {orario}\n")
        f.write(f"**💻 Comando Terminale:**\n```bash\n{comando}\n```\n")
        f.write(f"**📝 Risultato (estratto):**\n> {esito_pulito}...\n\n")
        f.write("---\n")
        
def system_doctor():
    """Monitora le risorse hardware (Principio Budget 0)."""
    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory().percent
    
    status = "[bold green]OTTIMO[/bold green]" if ram < 75 else "[bold red]CRITICO[/bold red]"
    color = "green" if ram < 75 else "red"
    
    panel_content = f"💻 CPU: {cpu}% | 🧠 RAM: {ram}% | Stato: {status}"
    console.print(Panel(panel_content, title="🏥 System Doctor", border_style=color))

def configura_sessione():
    """Configura il provider e scansiona i modelli disponibili."""
    console.print("\n[italic]Inserisci 'ollama' per locale o la tua API Key per il cloud[/italic]")
    key = input("Chiave: ").strip()
    
    if key.lower() == "ollama":
        prov, url = "Ollama", "http://localhost:11434/v1"
        try:
            r = requests.get("http://localhost:11434/api/tags", timeout=2)
            modelli = [m['name'] for m in r.json()['models']]
        except:
            log_msg("WARNING", "Ollama non risponde. Uso modelli predefiniti.")
            modelli = ["llama3", "phi3", "mistral"]
    else:
        prov, url = "Cloud AI", "https://api.groq.com/openai/v1" if key.startswith("gsk_") else "https://api.openai.com/v1"
        modelli = ["gpt-4o", "llama3-70b-8192", "mixtral-8x7b-32768"]

    console.print("\n[bold yellow]Modelli Rilevati:[/bold yellow]")
    for i, m in enumerate(modelli):
        console.print(f"{i+1}. {m}")
    
    scelta = int(Prompt.ask("\nQuale modello vuoi usare?", default="1")) - 1
    return key, prov, url, modelli[scelta]

def esegui_comando(comando):
    """Esegue il comando, gestisce gli errori e salva il log Markdown."""
    console.print(f"\n[bold orange3]PROPOSTA COMANDO:[/bold orange3] [white on blue] {comando} [/white on blue]")
    
    if Prompt.ask("Vuoi eseguire?", choices=["y", "n"], default="y") == "y":
        try:
            res = subprocess.run(comando, shell=True, capture_output=True, text=True)
            
            if res.returncode == 0:
                log_msg("SUCCESS", "Eseguito correttamente.")
                scrivi_log_md(comando, res.stdout)
                return f"OUTPUT:\n{res.stdout}"
            else:
                log_msg("ERROR", f"Il terminale ha risposto: {res.stderr}")
                # Logghiamo anche l'errore per studiarlo
                scrivi_log_md(comando, f"ERRORE: {res.stderr}")
                return f"ERRORE:\n{res.stderr}"
        except Exception as e:
            log_msg("ERROR", f"Errore di sistema: {e}")
            return str(e)
            
    return "Esecuzione annullata."

def main():
    logo()
    check_updates() # Controlla PyPI all'avvio
    
    key, prov, url, mod = configura_sessione()
    log_msg("SUCCESS", f"Codez è attivo! Modello: {mod}")
    console.print("[dim]Comandi speciali: /status | /history | /explain | /stop[/dim]\n")

    ultimo_comando_generato = ""

    while True:
        user_input = input(f"({mod}) > ").strip()
        
        if not user_input: continue
        if user_input == "/stop": break
        
        if user_input == "/status":
            system_doctor()
            continue

        if user_input == "/history":
            log_msg("INFO", "Apro il diario Markdown...")
            os.system('notepad CODEZ_HISTORY.md' if os.name == 'nt' else 'open CODEZ_HISTORY.md')
            continue

        if user_input == "/explain":
            if not ultimo_comando_generato:
                log_msg("WARNING", "Non ci sono ancora comandi da spiegare.")
                continue
            user_input = f"Spiegami come a un principiante cosa fa questo comando: {ultimo_comando_generato}"
            log_msg("INFO", "Generazione spiegazione...")

        # --- LOGICA INTELLIGENZA ARTIFICIALE ---
        prompt_sistema = (
            "Sei Codez, un assistente terminale open-source. "
            "Se devi suggerire un'azione, usa sempre il prefisso 'COMMAND: ' seguito dal codice. "
            "Se l'utente chiede spiegazioni, sii semplice e accessibile. "
            "Usa un tono amichevole ma professionale."
        )
        
        payload = {
            "model": mod,
            "messages": [
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": user_input}
            ]
        }
        
        try:
            headers = {"Authorization": f"Bearer {key}"} if key.lower() != "ollama" else {}
            r = requests.post(f"{url}/chat/completions", headers=headers, json=payload)
            r.raise_for_status()
            risposta = r.json()['choices'][0]['message']['content']

            if "COMMAND: " in risposta:
                # Estraiamo il comando pulito
                cmd = risposta.split("COMMAND: ")[1].strip().replace('`', '')
                ultimo_comando_generato = cmd
                esito = esegui_comando(cmd)
                console.print(f"[dim]{esito}[/dim]")
            else:
                console.print(f"\n[cyan]AI:[/cyan] {risposta}\n")
                
        except Exception as e:
            log_msg("ERROR", f"Impossibile connettersi all'IA: {e}")

if __name__ == "__main__":
    main()