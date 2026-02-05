## Gestion des Participants

Les participants sont des employés ou des membres d'une entreprise qui répondent aux enquêtes de mobilité dans le cadre d'une campagne. Chaque campagne maintient sa propre liste de participants identifiés par un identifiant unique qui fait référence au registre externe des participants de l'entreprise.

### Ajouter des Participants

Les participants sont ajoutés manuellement via la section participants de la campagne :

1. Accédez à la section participants de la campagne
2. Cliquez sur le bouton "Ajouter"
3. Saisissez les informations du participant :
   - **Identifiant** (_requis_) : Un identifiant unique qui fait référence au registre externe des participants de votre entreprise (par ex., ID employé, numéro de badge)
   - **Classe d'âge** (optionnel) : Sélectionnez parmi les tranches d'âge prédéfinies (16-17, 18-24, 26-44, 45-64, 65+)
   - **Taux d'emploi** (optionnel) : Pourcentage d'emploi à temps plein (0-100%)
   - **Taux de télétravail** (optionnel) : Pourcentage de temps de travail à distance (0-100%)
   - **Véhicule de société** (optionnel) : Bouton à activer pour indiquer si le participant a accès à un véhicule de société
4. Cliquez sur "Enregistrer" pour ajouter le participant

**Important :** Le champ identifiant fait référence au système de registre des participants de votre entreprise. Saisissez uniquement des identifiants qui existent dans votre système interne pour assurer un suivi approprié et la protection des données.

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
4. Partagez ce lien unique avec le participant via le canal de communication préféré de votre entreprise

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
- Si non défini, les informations de contact au niveau de l'entreprise sont utilisées
- Cela garantit que les participants ont toujours un point de contact pour leurs questions

## Bonnes Pratiques

### Lors de l'Ajout de Participants

1. **Utilisez des identifiants précis** : Assurez-vous que les identifiants correspondent à votre registre interne des participants
2. **Fournissez des données démographiques complètes** : Les champs optionnels aident à améliorer les analyses de l'enquête
3. **Ajoutez les participants avant le début de la campagne** : Préparez la liste complète à l'avance
4. **Maintenez la cohérence des identifiants** : Utilisez le même format pour toutes les campagnes

### Lors du Partage des Liens d'Enquête

1. **Protégez la confidentialité des jetons** : Chaque jeton est unique et ne doit être partagé qu'avec le participant correspondant
2. **Utilisez des canaux de communication sécurisés** : Envoyez les jetons via les méthodes de communication approuvées par votre entreprise
3. **Incluez le contexte** : Expliquez l'objectif de la campagne lors du partage du lien de l'enquête
4. **Fixez des délais clairs** : Communiquez la date de fin de la campagne

### Lors du Suivi de la Progression

1. **Vérifiez régulièrement les taux de complétion** : Surveillez tout au long de la campagne
2. **Relancez les non-répondants** : Contactez les participants qui n'ont pas commencé
3. **Utilisez la fonction de recherche** : Filtrez les participants par identifiant pour suivre des individus spécifiques
4. **Exportez les données pour analyse** : Téléchargez le CSV pour analyser les schémas de participation

## Problèmes Courants et Solutions

### "Participant en double"

**Problème :** Tentative d'ajout d'un participant qui existe déjà dans la campagne
**Solution :**

- Vérifiez la liste des participants existants
- Vérifiez que l'identifiant est unique dans cette campagne
- Mettez à jour le participant existant au lieu d'en ajouter un nouveau

### Jeton ne fonctionne pas

**Problème :** Le participant signale que le lien de l'enquête ne fonctionne pas
**Solution :**

- Vérifiez que le jeton a été copié correctement (y compris l'URL complète)
- Vérifiez que la campagne est toujours active (non terminée)
- Assurez-vous que le participant utilise le bon format de lien
- Générez une nouvelle entrée de participant si nécessaire

### Données démographiques manquantes

**Problème :** Besoin de mettre à jour les informations du participant après sa création
**Solution :**

- Utilisez le bouton de modification pour modifier les détails du participant
- Ajoutez la classe d'âge, le taux d'emploi ou le taux de télétravail
- Enregistrez les modifications pour mettre à jour l'enregistrement du participant

## Modèle d'Export CSV

Lorsque vous téléchargez le fichier CSV, il contiendra les colonnes suivantes :

```csv
identifier,token,url,status,age_class,employment_rate,remote_work_rate,company_vehicle,created_at,updated_at
EMP001,abc123xyz,https://collect.example.com/go/abc123xyz,completed,26-44,100,20,true,2026-01-15T10:33:27.3464322,2026-02-01T14:22:16.456784
EMP002,def456uvw,https://collect.example.com/go/def456uvw,in progress,18-24,80,0,false,2026-02-05T12:18:52.577117,2026-02-05T12:44:05.381780
```

**Colonnes :**

- **identifier** : Identifiant unique du participant depuis votre registre
- **token** : Jeton d'accès unique pour l'enquête
- **url** : URL complète de l'enquête
- **status** : Statut de participation actuel
- **age_class** : Tranche d'âge sélectionnée (si fournie)
- **employment_rate** : Pourcentage d'emploi (si fourni)
- **remote_work_rate** : Pourcentage de télétravail (si fourni)
- **company_vehicle** : Si le participant a accès à un véhicule de société (si fourni)
- **created_at** : Date à laquelle le participant a été ajouté
- **updated_at** : Date de la dernière modification du participant
