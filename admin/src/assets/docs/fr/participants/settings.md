### Ajouter des Participants

Les participants sont ajoutés manuellement via la section participants de la campagne :

1. Accédez à la section participants de la campagne
2. Cliquez sur le bouton "Ajouter"
3. Saisissez les informations du participant :
   - **Identifiant** (_requis_) : Un identifiant unique qui fait référence au registre externe des participants de votre organisation (par ex., ID collaborateur·trice·s, numéro de badge)
   - **Classe d'âge** (optionnel) : Sélectionnez parmi les tranches d'âge prédéfinies (16-17, 18-24, 26-44, 45-64, 65+)
   - **Taux d'emploi** (optionnel) : Pourcentage d'emploi à temps plein (0-100%)
   - **Taux de télétravail** (optionnel) : Pourcentage de temps de travail à distance (0-100%)
   - **Véhicule de société** (optionnel) : Bouton à activer pour indiquer si le participant a accès à un véhicule de société
4. Cliquez sur "Enregistrer" pour ajouter le participant

**Important :** Le champ identifiant fait référence au système de registre des participants de votre organisation. Saisissez uniquement des identifiants qui existent dans votre système interne pour assurer un suivi approprié et la protection des données.

### Informations sur les Participants

Chaque entrée de participant dans le tableau affiche :

- **Identifiant** : L'identifiant unique faisant référence à votre registre externe des participants
- **Jeton** : Un jeton d'accès unique généré pour ce participant
- **Statut** : Statut de participation actuel (par ex., ouvert, complété)
- **Actions** : Boutons de modification ou de suppression pour gérer le participant

### Accéder à l'Enquête

Chaque participant se voit attribuer un **jeton** unique qui donne accès à l'enquête :

1. Le jeton apparaît dans le tableau des participants
2. Cliquez sur le jeton pour ouvrir le lien de l'enquête dans un nouvel onglet
3. Utilisez le bouton de copie à côté du jeton pour copier l'URL de l'enquête dans le presse-papiers
4. Partagez ce lien unique avec le participant via le canal de communication préféré de votre organisation

**Format de l'URL de l'enquête :** `https://collect.example.com/go/{token}`

**Important :**

- Chaque jeton est unique et ne doit être partagé qu'avec le participant correspondant
- Les jetons n'expirent pas mais deviennent invalides une fois la campagne terminée
- Les participants peuvent utiliser le même jeton pour accéder et compléter leur enquête plusieurs fois jusqu'à la soumission

### Gérer les Participants

#### Modifier les Participants

Pour mettre à jour les informations d'un participant :

1. Cliquez sur le bouton de modification (icône crayon) à côté du participant
2. Modifiez les détails du participant :
   - Identifiant (ne peut pas être modifié si l'enquête est commencée)
   - Classe d'âge
   - Taux d'emploi
   - Taux de télétravail
   - Statut du véhicule de société
3. Cliquez sur "Enregistrer" pour mettre à jour le participant

#### Supprimer des Participants

Pour supprimer un participant d'une campagne :

1. Sélectionnez le(s) participant(s) à supprimer
2. Cliquez sur "Supprimer le participant"
3. Confirmez la suppression

**Important :**

- Les participants supprimés ne peuvent plus accéder à l'enquête
- Toutes les données d'enquête en cours ou complétées sont conservées
- Les participants peuvent être rajoutés ultérieurement si nécessaire

### Statut des Participants

Les participants peuvent avoir différents statuts tout au long de la campagne :

- **Ouvert** : Le participant n'a pas encore accédé à l'enquête ou l'enquête a été commencée mais pas complétée
- **Complété** : Enquête soumise avec succès

### Exporter les Données des Participants

Pour exporter les informations des participants :

1. Cliquez sur "Télécharger CSV" dans la section participants
2. Un fichier CSV est automatiquement généré contenant :
   - Identifiant
   - Jeton
   - URL de l'enquête
   - Statut
   - Classe d'âge
   - Taux d'emploi
   - Taux de télétravail
   - Statut du véhicule de société
   - Date de création
   - Date de dernière mise à jour

**Utilisations de l'export :**

- Partage des liens d'enquête avec les participants
- Suivi de la progression et rapports
- Relance des non-répondants
- Intégration avec les systèmes internes
- Analyses de campagne

### Communication avec les Participants

#### Communication au Niveau de la Campagne

Toutes les communications avec les participants utilisent les informations de contact définies dans les paramètres de la campagne :

- Si des informations de contact spécifiques à la campagne sont définies, les participants contactent cette personne
- Si non défini, les informations de contact au niveau de l'organisation sont utilisées
- Cela garantit que les participants ont toujours un point de contact pour leurs questions