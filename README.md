# 🕵️‍♂️ Splinter

Ce projet comprend deux composants principaux : RAT_server et RAT_client, conçus pour permettre une administration à distance dans un environnement de test de sécurité. Ce projet est destiné à des fins éducatives et de test de pénétration.

# ⚠️ Disclaimer

**Splinter est destiné uniquement à des fins éducatives et de recherche. Les auteurs décline toute responsabilité et/ou obligation légale quant à la manière dont vous choisissez d'utiliser les outils, le code source ou tout fichier fourni. Les auteurs et toute personne affiliée ne seront pas responsables des pertes et/ou dommages liés à l'utilisation de TOUT fichier fourni avec Splinter. En utilisant Splinter ou tout fichier inclus, vous comprenez que vous acceptez de l'UTILISER À VOS PROPRES RISQUES. Encore une fois, Splinter et TOUS les fichiers inclus sont destinés UNIQUEMENT à des fins ÉDUCATIVES et/ou de RECHERCHE. Splinter est destiné à être utilisé uniquement dans vos laboratoires de test de pénétration, ou avec le consentement explicite du propriétaire de la propriété testée.**


## 👥 Auteurs

- [@mrl91](https://github.com/mrl91)
- [@Tarti](https://github.com/JBRabiller)


## 🛠️ Installation

Prérequis :

- **Python**
- **pip**

⚠️ Splinter utilise **secretsdump.py** pour sa fonction hashdump, votre antivirus peut supprimer ce script, il est nécessaire d'**autoriser le fichier** ou de **désactiver votre antivirus** lors du clonage du dépôt ⚠️

Pour installer les dépendances :

```python
pip install -r requirements.txt
```

## ⚙️ Configuration
Assurez-vous que les configurations de réseau (adresse IP, port, etc.) dans les scripts client et serveur sont correctement définies pour permettre une communication fluide.

Il est recommandé de mettre en place une IP fixe sur les deux machines.
Le RAT_Server génére automatiquement un certificat qu'il transmet et l'**installe automatiquement** sur le RAT_client.

Enfin il faudras modifier le main.py du RAT_client en fonction de l'IP du serveur, Splinter affiche l'IP du serveur lors du lancement du script : 

```python
ip_server = 'votre_ip'
```

## 📚 Utilisation
Démarrage du **serveur** :

```python
python3 main.py
```
*Le serveur attendra la connexion du client*

Démarrage du **client** :
```python
python3 main.py
```
*Le client tentera de se connecter au serveur*

## ✨ Fonctionnalités
**Commandes distantes** : Exécutez des commandes sur les machines clientes à partir du serveur. Utiliser "**help**" pour voir les commandes disponibles.

**Communication sécurisée** : Les scripts sont configurés pour utiliser des connexions sécurisées.

## ☕️ Multi Client

Des test ont été effectué pour que Splinter puissent s'utiliser en multiclient mais les test n'ont pas été concluant.
Voici le code de test du main.py du RAT_server

```python
import threading
import socket
from command_setup import create_server, setup_ssl_certificates, start_non_secure_server
from logo import banner
from colorama import init

# Global dictionary to store client connections
clients = {}

def multi_client(client_socket, address):
    # un seul client
    while True:
        try:
            # On récupère les donnée du client et réponse
            data = client_socket.recv(1024)
            if not data:
                break
        except Exception as e:
            print(f"Error with client {address}: {e}")
            break


def main():
    print(banner)
    init(autoreset=True)
    current_dir = os.path.dirname(os.path.realpath(__file__))
    cert_path = os.path.join(current_dir, 'server.crt')
    key_path = os.path.join(current_dir, 'server.key')
    config_file = os.path.join(current_dir, 'cert_config.conf')
    # Setup and start the server
    server_socket = create_server()  

    while True:
        try:
            # Accept new client connections
            client_sock, address = server_socket.accept()
            print(f"Connection established with {address}")

            # Store client information
            clients[address] = client_sock

            # Start a new thread for each client
            client_thread = threading.Thread(target=multi_client, args=(client_sock, address))
            client_thread.start()
            start_non_secure_server()

if __name__ == "__main__":
    main()
```
