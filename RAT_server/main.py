import os
from command_setup import create_server, setup_ssl_certificates
from logo import banner
from colorama import Fore, Style, init

# Obtention du chemin du répertoire courant où le script est exécuté
current_dir = os.path.dirname(os.path.realpath(__file__))
# Chemins absolus pour le certificat et la clé
cert_path = os.path.join(current_dir, 'server.crt')
key_path = os.path.join(current_dir, 'server.key')
config_file = os.path.join(current_dir, 'cert_config.conf')

# Initialise Colorama
init(autoreset=True)
print(banner)
# Configuration des certificats SSL
setup_ssl_certificates(cert_path, key_path, config_file)

# Vérification de l'existence des fichiers de certificat et de clé
if not os.path.isfile(cert_path) or not os.path.isfile(key_path):
    print(f"Erreur : Fichier de certificat ou clé manquant. Certificat : {cert_path}, Clé : {key_path}")
else:
    # Création et lancement du serveur
    create_server(8889, cert_path, key_path)