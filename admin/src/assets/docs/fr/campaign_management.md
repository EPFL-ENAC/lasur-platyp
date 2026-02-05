## Gestion des campagnes

Les campagnes sont des enquêtes ou initiatives de mobilité limitées dans le temps au sein d'une entreprise. Chaque entreprise peut avoir plusieurs campagnes.

### Paramètres de la campagne

#### Informations de base

- **Nom** (_obligatoire_) : Identifiant de la campagne
- **Description** : Présentation de l'objectif de la campagne
- **Date de début** : Date de lancement de la campagne
- **Date de fin** : Date de clôture de la campagne
- **Slug** : Identifiant unique pour l'URL (généré automatiquement, ex. : "acme-corp-printemps-2024-mobilite-vx7k")

#### Informations de contact

Les campagnes peuvent remplacer les informations de contact définies au niveau de l'entreprise :

- **Nom du contact** : Personne de contact spécifique à la campagne
- **Email du contact** : Adresse email spécifique à la campagne
- **URL d'information** : Lien d'information spécifique à la campagne

Si ces champs sont laissés vides, la campagne utilisera les informations de contact de l'entreprise.

#### Lieux de travail

Les campagnes doivent définir la gestion des lieux de travail :

**Lieux de travail ouverts :**

- Si activé, les participants peuvent saisir n'importe quelle adresse de lieu de travail lors du remplissage du questionnaire
- Utile pour les entreprises avec de nombreux sites ou des modalités de travail flexibles

**Lieux de travail définis :**

- Créez une liste de lieux de travail spécifiques
- Chaque lieu de travail nécessite :
  - **Nom** : Identifiant du lieu (ex. : "Plateforme Logistique 12", "Bureau Centre-ville")
  - **Adresse** : Adresse complète
  - **Coordonnées** : Latitude et longitude (remplies automatiquement lors de la validation de l'adresse)
- Les participants choisissent dans cette liste lors du questionnaire

**Important :** Au moins une de ces options doit être configurée :

- Soit activer "Lieux de travail ouverts", OU
- Définir au moins un lieu de travail spécifique

**Import en masse :**

- Importez un fichier CSV pour ajouter plusieurs lieux de travail en une fois
- Colonnes CSV requises : name, address, lat, lon
- Utilisez le bouton "Importer CSV" dans l'onglet des lieux de travail

#### Mesures spécifiques à la campagne

Par défaut, les campagnes héritent des mesures employeur définies au niveau de l'entreprise. Cependant, vous pouvez activer des mesures spécifiques à la campagne :

1. Activez "Avec des mesures employeur spécifiques à cette campagne"
2. Sélectionnez les mesures propres à cette campagne
3. Utile pour :
   - Pilotes testant de nouvelles initiatives
   - Mesures saisonnières
   - Mesures spécifiques à un site
   - Avantages à durée limitée

## Bonnes pratiques

### Lors de la configuration des mesures

1. **Révisez régulièrement les mesures** : Mettez à jour lors du lancement de nouvelles initiatives ou de la fin d'anciennes
2. **Considérez les déplacements personnels et professionnels** : Beaucoup d'entreprises se concentrent sur les trajets domicile-travail, mais les déplacements professionnels sont tout aussi importants
3. **Soyez précis avec les mesures personnalisées** : Des libellés clairs et descriptifs aident les participants à comprendre les options disponibles

### Lors de la création des campagnes

1. **Choisissez des noms explicites** : Incluez l'année ou la saison pour plus de clarté
2. **Fixez des dates de fin réalistes** : Laissez suffisamment de temps pour la participation
3. **Définissez soigneusement les lieux de travail** : Des localisations précises permettent de meilleurs calculs de temps de trajet et d'émissions
4. **Envisagez des mesures spécifiques à la campagne** : Utilisez-les pour tester de nouvelles initiatives avant un déploiement à l'échelle de l'entreprise

## Problèmes courants et solutions

### "La localisation est requise, assurez-vous que l'adresse est valide"

**Problème :** L'adresse du lieu de travail ne peut pas être validée
**Solution :**

- Vérifiez que l'adresse est complète et correcte
- Essayez un format d'adresse plus précis
- Vérifiez que les coordonnées sont bien renseignées

### "Au moins un lieu de travail doit être défini pour la campagne"

**Problème :** La campagne n'a pas de configuration de lieu de travail
**Solution :**

- Soit activer "Lieux de travail ouverts", OU
- Ajouter au moins un lieu de travail avec une adresse valide

### Les mesures personnalisées n'apparaissent pas

**Problème :** Une mesure personnalisée a été créée mais n'apparaît pas dans les listes déroulantes
**Solution :**

- Rafraîchissez l'éditeur d'entreprise
- Vérifiez que la mesure possède des libellés dans les deux langues
- Vérifiez que le bon groupe a été sélectionné
