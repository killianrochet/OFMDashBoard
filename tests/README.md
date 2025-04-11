# Tests Instagram Automation avec Appium

## Configuration de l'environnement de test

1. Installer Android Studio
   - Télécharger depuis : https://developer.android.com/studio
   - Installer Android Studio
   - Lancer Android Studio et suivre l'assistant d'installation

2. Créer un émulateur Android
   - Dans Android Studio, cliquer sur "Tools" > "Device Manager"
   - Cliquer sur "Create Device"
   - Sélectionner "Pixel 6" comme appareil
   - Choisir l'image système Android 13.0 (API 33)
   - Finaliser la création de l'émulateur

3. Installer Appium
   ```bash
   npm install -g appium
   appium driver install uiautomator2
   ```

4. Installer les dépendances Python
   ```bash
   cd tests
   pip install -r requirements.txt
   ```

5. Préparer l'environnement de test
   - Créer un dossier `test_media` dans le dossier `tests`
   - Ajouter une image test `test_photo.jpg`
   - Ajouter une vidéo test `test_video.mp4`

## Exécution des tests

1. Démarrer l'émulateur Android Studio
2. Démarrer le serveur Appium
   ```bash
   appium
   ```
3. Installer Instagram sur l'émulateur et se connecter
4. Exécuter les tests
   ```bash
   cd tests
   pytest test_instagram_post.py -v
   ```

## Structure des tests

- `test_instagram_post.py` : Tests pour les posts photos et reels
- `test_media/` : Dossier contenant les médias de test
- `requirements.txt` : Dépendances Python nécessaires

## Notes importantes

- Les tests sont configurés pour ne pas publier réellement sur Instagram
- Assurez-vous que l'émulateur est bien démarré avant de lancer les tests
- Vérifiez que le serveur Appium est en cours d'exécution
- Les identifiants des éléments UI peuvent changer selon la version d'Instagram