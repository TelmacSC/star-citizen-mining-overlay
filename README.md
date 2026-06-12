# Star Citizen Mining Overlay

Application Windows en Python pour afficher un overlay compact des minerais selectionnes au-dessus de Star Citizen.

## Fonctionnalites

- Fenetre de configuration avec tous les minerais et cases a cocher.
- Sauvegarde automatique des selections dans un fichier JSON.
- Chargement automatique des preferences au demarrage.
- Overlay noir semi-transparent, toujours au-dessus, texte blanc monospace.
- Overlay deplacable a la souris.
- Raccourci global `F10` pour afficher ou masquer l'overlay.
- Option de clic traversant pour laisser passer les clics vers le jeu.

## Installation

1. Installer Python 3.12 ou plus recent.
2. Ouvrir un terminal dans ce dossier.
3. Creer un environnement virtuel :

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

4. Installer les dependances :

```powershell
pip install -r requirements.txt
```

## Lancement

```powershell
python src\main.py
```

Le fichier de preferences est cree automatiquement dans :

```text
%APPDATA%\StarCitizenMiningOverlay\preferences.json
```

## Creation de l'executable

Installer PyInstaller :

```powershell
pip install pyinstaller
```

Puis lancer :

```powershell
.\build.ps1
```

L'executable sera genere dans :

```text
dist\StarCitizenMiningOverlay\StarCitizenMiningOverlay.exe
```

## Notes Star Citizen

L'overlay est concu pour le mode plein ecran fenetre. En plein ecran exclusif, Windows peut empecher l'affichage d'overlays externes.

Si le raccourci `F10` ne fonctionne pas dans le jeu, lancez l'application en tant qu'administrateur.
