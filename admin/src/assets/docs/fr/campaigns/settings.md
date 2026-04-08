### Paramètres de la campagne

#### Informations de base

- **Nom** (_obligatoire_) : Identifiant de la campagne
- **Identifiant** : Identifiant unique pour l'URL (généré automatiquement, ex. : "acme-corp-printemps-2024-mobilite-vx7k")
- **Date de début** : Date de lancement de la campagne
- **Date de fin** : Date de clôture de la campagne
- **Nombre de collaborateur·trice·s** : Permet d'ajuster le suivi, dans le Tableau de bord, du taux de participation au questionnaire


#### Informations de contact

Les campagnes peuvent remplacer les informations de contact définies au niveau de l'organisation :

- **Nom du contact** : Personne de contact spécifique à la campagne
- **Email du contact** : Adresse email spécifique à la campagne
- **Lien d'information** : Lien d'information spécifique à la campagne

Si ces champs sont laissés vides, la campagne utilisera les informations de contact de l'organisation.


#### Mesures spécifiques à la campagne

Si des mesures d'accompagnement à la mobilité des collaborateur·trice·s sont déjà en place au moment de la campagne, vous pouvez les renseigner ici afin que les collaborateur·trice·s concernés puissent en avoir l'information :

1. Activez "Avec des mesures employeur spécifiques à cette campagne"
2. Sélectionnez les mesures propres à cette campagne
3. Utile pour :
   - Pilotes testant de nouvelles initiatives
   - Mesures saisonnières
   - Mesures spécifiques à un site
   - Avantages à durée limitée

#### Lieux de travail

Les campagnes doivent définir la gestion des lieux de travail :

**Lieux de travail ouverts :**

- Si activé, les participant·e·s peuvent saisir n'importe quelle adresse de lieu de travail lors du remplissage du questionnaire
- Utile pour les organisations avec de nombreux sites ou des modalités de travail flexibles

**Lieux de travail définis :**

- Créez une liste de lieux de travail spécifiques
- Chaque lieu de travail nécessite :
  - **Nom** : Identifiant du lieu (ex. : "Plateforme Logistique 12", "Bureau Centre-ville")
  - **Adresse** : Adresse complète
  - **Coordonnées** : Latitude et longitude (remplies automatiquement lors de la validation de l'adresse)
- Les participant·e·s choisissent dans cette liste lors du questionnaire

**Important :** Au moins une de ces options doit être configurée :

- Soit activer "Lieux de travail ouverts", OU
- Définir au moins un lieu de travail spécifique

**Import en masse :**

- Importez un fichier CSV pour ajouter plusieurs lieux de travail en une fois
- Colonnes CSV requises : name, address, lat, lon
- Utilisez le bouton "Importer CSV" dans l'onglet des lieux de travail
