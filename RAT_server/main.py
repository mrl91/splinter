import os
import threading
from command_setup import create_server, setup_ssl_certificates, start_non_secure_server
from logo import banner
from colorama import init

private_server_port = 8889
# Initialisation et démarrage du serveur sécurisé
def main():
    print(banner)
    init(autoreset=True)
    # Définit les chemins vers les certificats SSL et la configuration nécessaire
    current_dir = os.path.dirname(os.path.realpath(__file__))
    cert_path = os.path.join(current_dir, 'server.crt')
    key_path = os.path.join(current_dir, 'server.key')
    config_file = os.path.join(current_dir, 'cert_config.conf')

    setup_ssl_certificates(cert_path, key_path, config_file)  # Configure les certificats SSL pour le serveur
    # Crée un thread pour le serveur sécurisé pour ne pas bloquer l'exécution principale
    server_thread = threading.Thread(target=create_server, args=(private_server_port, cert_path, key_path))
    server_thread.start()
    start_non_secure_server() # Démarre le serveur non sécurisé pour la récupération de certificat

if __name__ == "__main__":
    main()