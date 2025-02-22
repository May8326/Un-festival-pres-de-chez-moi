# Un festival près de chez moi

Dépôt en ligne de l'application web Flask réalisée dans le cours de Python donné à l'école des Chartes en M2TNAH

## Utilisation du Repo pour le travail en groupe


### Cheat : alias à copier dans le bashrc pour démarrer dataiku en une commande

```bash
alias <nom_de_mon_alias> = "sudo docker run -u dss -v \$HOME/Documents/Volumes/dss:/home/dss -p 127.0.0.1:11000:11000 -it ghcr.io/ahpnils/ahp-dss:latest /home/dss/DSS_DATA_DIR/bin/dss run"
```

### Utilisation de Dataiku

> Attention aux fichiers de plus de 100mo qui ne sont pas pris en charge par GitHub et font bugger le push

Avant chaque session de travail, aller dans son dossier cloné sur son travail

1. **Mettre à jour ses données**
	- `git pull` => pour récupérer le travail des autres
	- s'il faut mettre à jour sa branche par rapport au main (= pour récuperer le travail qui a été fait par qqn d'autre)
		- `git switch <ma branche>`
		- `git merge master`
2. **Pour travailler sur dataiku**
	- démarrer dataiku
	- cliquer sur l'oiseau dataiku : dans projets > nouveau projet > importer un projet
	- importer le dossier `ApplicationFlask.zip` qui se trouve dans le repo git
	- rentrer dans le projet qui vient d'être importé
	- faire ses manips
3. **Partager son travail**
	- Exporter le projet
		- sur la vue du flow, cliquer sur 'ApplicationFlask' en haut à gauche
		- en haut à droite : Actions > Exporter 
		- enregistrer le nouveau `ApplicationFlask.zip` dans sa branche à la place de l'ancien, `git add ApplicationFlask.zip`, `git commit -m "décrire ce qu'on a fait"
	- Partager à tous
		- se positionner sur la branche master `git switch master`
		- merger sa branche avec master `git merge <ma branche>`

C'EST BON, TOUT LE MONDE A ACCES AU TRAVAIL !
