import os
from command_setup import connect_to_server

current_dir = os.path.dirname(os.path.realpath(__file__)) # Répertoire courant où s'exécute le script
cert_path = os.path.join(current_dir, 'server.crt') # Construction du chemin vers le certificat SSL du serveur

# Définition de l'adresse IP et du port du serveur à connecter
ip_server = '192.168.108.172'
port_server = 8889

connect_to_server(ip_server, port_server, cert_path)
