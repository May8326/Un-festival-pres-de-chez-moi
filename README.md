# Un festival près de chez moi

Dépôt en ligne de l'application web Flask réalisée dans le cours de Python donné à l'école des Chartes en M2TNAH

## Utilisation du Repo pour le travail en groupe

### Utilisation de Dataiku

>IMPORTANT : 

Avant chaque session de travail, aller dans son dossier cloné sur son travail
1. Mettre à jour ses données
	- `git pull` => pour récupérer le travail des autres
	- s'il faut mettre à jour sa branche par rapport au main (= pour récuperer le travail qui a été fait par qqn d'autre)
		- `git switch <ma branche>`
		- `git merge master`
2. Pour travailler sur dataiku :
	- démarrer dataiku
	- cliquer sur l'oiseau dataiku : dans projets > nouveau projet > importer un projet
	- importer le dossier `ApplicationFlask.zip` qui se trouve dans le repo git
	- rentrer dans le projet qui vient d'être importé
	- faire ses manips
3. Partager son travail :
	- Exporter le projet
		- sur la vue du flow, cliquer sur 'ApplicationFlask' en haut à gauche
		- en haut à droite : Actions > Exporter 
		- enregistrer le nouveau `ApplicationFlask.zip` dans sa branche à la place de l'ancien
	- Partager à tous
		- se positionner sur la branche master `git switch master`
		- merger sa branche avec master `git merge <ma branche>`

C'EST BON, TOUT LE MONDE A ACCES AU TRAVAIL !
