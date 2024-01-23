
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

Les dépendances spécifiées dans requirement.txt pour chaque composant.
Pour installer les dépendances :

```python
pip install -r requirement.txt
```

## ⚙️ Configuration
Assurez-vous que les configurations de réseau (adresse IP, port, etc.) dans les scripts client et serveur sont correctement définies pour permettre une communication fluide.

Il est recommandé de mettre en place une IP fixe sur les deux machines.
Le RAT_Server génére automatiquement un certificat qu'il transmet et **installe** sur le RAT_client.

Enfin il faudras modifier le main.py du RAT_client en fonction de l'IP du serveur, Splinter affiche l'IP du serveur lors du lancement du script : 

```python
ip_server = 'votre_ip'
```

## 📚 Utilisation
Démarrage du **serveur** :

```python
python3 main.py
```
*Le serveur attendra les connexions des clients.*

Démarrage du **client** :
```python
python3 main.py
```
*Le client tentera de se connecter au serveur.*

## ✨ Fonctionnalités
**Commandes distantes** : Exécutez des commandes sur les machines clientes à partir du serveur. Utiliser "**help**" pour voir les commandes disponibles.

**Communication sécurisée** : Les scripts sont configurés pour utiliser des connexions sécurisées.