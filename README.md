# Challenge Triple A - Dashboard de Monitoring

## Description

Le challenge consiste à développer un outil simple de monitoring capable d’afficher en temps réel les statistiques d’une machine virtuelle Linux via un dashboard web. L’objectif est de fournir une solution légère, autonome et facilement compréhensible par les équipes techniques.

Ce projet permet de visualiser des informations essentielles telles que l’utilisation du CPU, de la mémoire, et du réseau, le tout dans une interface web intuitive.

## Prérequis

Avant d’utiliser ce projet, assurez-vous d’avoir installé :

- Une machine virtuelle Linux (Ubuntu, Debian ou équivalent)
- Python 3.8+
- Pip (gestionnaire de packages Python)
- Navigateur web moderne (Chrome, Firefox, Edge)

## Installation

Clonez le dépôt :

`git clone https://github.com/nicolas-riera/AAA.git`

## Commandes pour installer les dépendances

`pip install psutil flask`

`psutil` : pour récupérer les statistiques système.

`flask` : pour servir le dashboard web

## Utilisation

### Comment lancer le script

Exécutez le script principal pour démarrer le serveur de monitoring :

`python monitor.py`

#### Dashboard dynamique

Dans votre navigateur, accédez à : `http://localhost:5000` après avoir exécuté le script

#### Ouvrir index.html dans le navigateur

Pour un rendu statique, ouvrez le fichier `index.html` après avoir lancer le script.

## Fonctionnalités

- Surveillance des informations systèmes principales
- Surveillance du CPU (utilisation en % et fréquence)
- Surveillance de la mémoire RAM
- Surveillance du stockage disque
- Surveillance des processsus
- Interface web simple et responsive
- Mise à jour automatique des statistiques en temps réel

## Captures d'écran

TBD

## Difficultés rencontrées

TBD

## Améliorations possibles

TBD

## Auteur

Ce projet a été réalisé par [Nicolas Riera](https://github.com/nicolas-riera), [Gabriel Sempéré](https://github.com/Gabriel-SEMPERE) et [Yannis Sandoval](https://github.com/Yannis-Sandoval).

