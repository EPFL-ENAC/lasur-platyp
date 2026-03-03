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