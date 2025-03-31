# 🎉 Un Festival Près de Chez Moi 🎶

## 1. Présentation du projet

"Un Festival Près de Chez Moi" est une application web développée avec Flask qui permet aux utilisateurs de découvrir des festivals et monuments historiques à proximité de leur localisation. Cette plateforme vise à promouvoir le patrimoine culturel et les événements artistiques en France. 🌍✨

### Fonctionnalités principales

- 🔍 **Recherche multicritères** : trouvez des festivals par nom, période (avant-saison, saison, après-saison), discipline artistique et localisation géographique
- 🗺️ **Visualisation cartographique** : explorez les résultats sur une carte interactive avec regroupement intelligent de marqueurs
- 🏛️ **Monuments à proximité** : découvrez les monuments historiques situés près des festivals
- ⭐ **Gestion de favoris** : créez un compte utilisateur pour sauvegarder vos festivals, monuments ou communes préférés
- 💡 **Autocomplétion** : bénéficiez de suggestions lors de vos recherches pour une expérience utilisateur optimisée

## 2. Structure de l'application

```
appli/
├── app/
│   ├── app.py              # Configuration principale de l'application Flask
│   ├── routes/             # Gestion des routes et des vues
│   │   ├── generales.py    # Routes générales (accueil, recherche)
│   │   ├── favoris.py      # Gestion des favoris utilisateurs
│   │   └── ...
│   ├── models/             # Modèles de données
│   │   ├── database.py     # Définition des tables et relations
│   │   ├── users.py        # Modèle utilisateur
│   │   ├── formulaires.py  # Formulaires WTForms
│   │   └── ...
│   ├── templates/          # Templates Jinja2
│   │   ├── pages/          # Pages principales
│   │   └── partials/       # Composants réutilisables
│   ├── statics/            # Fichiers statiques (CSS, JS, images)
│   │   ├── css/            # Feuilles de style
│   │   └── ...
│   └── utils/              # Utilitaires et fonctions auxiliaires
│       ├── transformations.py
│       ├── proximite.py
│       ├── pagination.py
│       └── ...
└── run.py                  # Point d'entrée pour lancer l'application
```

## 3. Instructions d'installation

### Prérequis

- 🐍 Python 3.8 ou supérieur
- 📦 pip (gestionnaire de paquets Python)
- 🛠️ Git

### Étapes d'installation

1. **Cloner le dépôt** 📂

```bash
git clone https://github.com/[username]/Un-festival-pres-de-chez-moi.git
cd Un-festival-pres-de-chez-moi
```
2. **Télécharger la base de donnée** 🗃️

la base de donnée étant trop lourde pour GitHub, elle est téléchargeable jusqu'au 31/10/2025 à [cette adresse](https://univpsl-my.sharepoint.com/:u:/g/personal/maelys_gioan_chartes_psl_eu/EWkhErcLYQlPonwIXfYIttIBzUZuWAaWVdzW1WNECsXiaw?e=ZlKzep).

3. **Créer un environnement virtuel** 🌐

```bash
python -m venv env
```

4. **Activer l'environnement virtuel** 🚀

* Sous Windows :
```shell
env\Scripts\activate
```
* Sous macOS et Linux

```bash
source env/bin/activate
```

5. **Installer les dépendances** 📋

```bash
pip install -r requirements.txt
```

6. **Configurer le fichier .env** 🛡️

Créez un fichier `.env` à la racine du projet avec les variables suivantes :

```text
# Clé secrète pour la sécurité de l'application
SECRET_KEY=votre_clé_secrète_aléatoire

# Configuration de la base de données
SQLALCHEMY_DATABASE_URI=sqlite:////chemin/absolu/vers/bdd_festiv.sqlite

# Nombre de résultats par page
RESULTATS_PER_PAGE=20

WTF_CSRF_ENABLED=True
```

**Note importante**: Utilisez la base de données fournie `bdd_festiv.sqlite` qui contient déjà toutes les données nécessaires. Assurez-vous d'indiquer le chemin absolu vers cette base de données dans la variable `SQLALCHEMY_DATABASE_URI`.

7. **Lancer l'application** 🏃‍♂️

```bash
python3 festivals-en-fête/run.py
```

## 4. Crédits et remerciements 🙏

Cette application utilise des données ouvertes sur les festivals et monuments historiques de France.

### Remerciements

Nous tenons à remercier chaleureusement :

- **Maxime Challon**, professeur de Flask, pour ses enseignements précieux et son accompagnement. 👨‍🏫
- **Mme Bermès**, responsable pédagogique, pour son soutien et sa disponibilité. 📚
- Tous les professeurs qui nous ont transmis les compétences nécessaires pour mener à bien ce projet. 🎓
