# Générateur d'attestation de sortie confinement en CLI

Ce générateur utilise le site officiel `media.interieur.gouv.fr/deplacement-covid-19/` pour générer l'attestation. Le formulaire du site est rempli grace à Webdrivers de Selenium.

L'attestation est placée dans le repertoire courant et peut être envoyée par message **telegram**.

## Utilisation

### Usage

```
./app.py -h
usage: app.py [-h] [-c CONFIG [CONFIG ...]]

Générateur d'attestation de sortie - utilise le site officiel media.interieur.gouv.fr/deplacement-covid-19/

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG [CONFIG ...], --config CONFIG [CONFIG ...]
                        le/les fichier(s) de configuration (defaut: config.yml)
```

l'option `-c` permet de préciser le nom du fichier de configuration yaml à utiliser. Il est possible d'en utiliser plusieurs en enchainant les noms

`$ ./app.py -c config_toto.yml config_tata.yml`

### Docker

`$ make build`

`$ docker run -it --rm attestation_generator ./app.py`

`$ docker run -it --rm attestation_generator ./app.py -h`

### Classique

Chrome/Chromium ainsi que le `chromedriver` ou `chromium-driver` doit etre installé.

`$ apt-get install chromium chromium-driver`

Installer les dépendances python

`$ pip3 install -r requirements.txt`

Lancer le générateur

`./app.py`

## Configuration

Le générateur fonctionne avec un fichier de configuration (`config.yml` par defaut) qui suit l'architecture suivante:

```yml
username:
  first_name: prénom
  last_name: nom
  birthday: 01/01/1990
  placeofbirth: Place of birth
  address: 00 rue exemple
  zipcode: 75000
  city: City
  reason: achats
```

L'attestation générée se nommera `username_attestation.yml`

La liste des `reasons` est:

- `achats`
- `sante`
- `famille`
- `travail`
- `handicap`
- `sports_animaux`
- `convocation`
- `missions`
- `enfants`

Il est possible de configurer plusieurs utilisateurs:

```yml
toto:
  first_name: toto
  last_name: nom
  birthday: 01/01/1990
  placeofbirth: Place of birth
  address: 00 rue exemple
  zipcode: 75000
  city: City
  reason: achats
tata:
  first_name: tata
  last_name: nom
  birthday: 01/01/1990
  placeofbirth: Place of birth
  address: 00 rue exemple
  zipcode: 75000
  city: City
  reason: achats
```

Pour envoyer l'attestation via **telegram**, il faut un bot telegram et les informations suivantes: 

- le `token` du bot
- le `chat_id` de chaque utilisateur

[Comment faire un bot telegram?](https://fr.jeffprod.com/blog/2017/creer-un-bot-telegram/)

Penser à envoyer un premier message à votre bot pour qu'il puisse vous en envoyer

```yml
toto:
  first_name: prénom
  last_name: nom
  birthday: 01/01/1990
  placeofbirth: Place of birth
  address: 00 rue exemple
  zipcode: 75000
  city: City
  reason: achats
  send:
    telegram:
      token: '000000000:xxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
      chat_id: '0000000000'
```
### TODO

- [ ] plus de senders (gmail? signal?)
