export default {
  main: {
    brand: 'Toolkit Mobilité',
  },
  form: {
    error: {
      origin: 'Veuillez entrer un point de départ',
      workplace: 'Veuillez entrer un lieu de travail',
    },
    age_class: "Quelle est votre classe d'âge ?",
    age_class_option: {
      '16_24': 'moins de 25 ans',
      '25_44': '25 - 44 ans',
      '45_64': '45 - 64 ans',
      '65': '65 ans et plus',
    },
    employment_rate: 'Quel est votre taux de travail ?',
    remote_work_rate: 'Quel est votre taux de télétravail ?',
    company_vehicle: 'Avez-vous un véhicule de fonction ?',
    yes: 'Oui',
    no: 'Non',
    workplace: 'Votre lieu de travail habituel',
    origin: "D'où partez-vous habituellement pour vous rendre au travail ?",
    origin_hint:
      'Cette information confidentielle sera uniquement utilisée pour calculer vos options de mobilité pour votre déplacement domicile-travail',
    travel_time:
      'Quel est votre temps de trajet domicile-travail, avec le mode de transport que vous utilisez habituellement ?',
    travel_time_minutes: 'minutes (aller)',
    constraints: 'Avez vous des contraintes potentielles quant à votre mobilité quotidienne ?',
    constraints_option: {
      dependent: "Conduite d'enfants ou de personnes dépendantes",
      heavy: 'Transport de matériel lourd ou encombrant',
      night: 'Travail de nuit',
      disabled: 'Carte de stationnement pour personne à mobilité réduite',
    },
    equipments: 'De quels équipements de mobilité disposez-vous ?',
    equipments_option: {
      bike: 'Vélo',
      upt_subs: 'Abonnement de transports publics urbains',
      train_subs: 'Abonnement de train',
      car_driver: 'Voiture (en tant que conducteur)',
      moto: 'Moto / scooter / cyclomoteur',
      ebike: 'Vélo à assistance électrique',
      mob_subs: 'Abonnement de mobilité partagée (mobility, etc.)',
      car_passenger: 'Voiture (en tant que passager)',
    },
    freq_mod: 'A quelle fréquence utilisez vous les modes suivants pour vous rendre au travail ?',
    freq_mod_hint: "Nombre de jours d'une semaine type",
    mode: {
      walking: 'La marche (>10 min.)',
      bike: 'Le vélo (ou VAE)',
      pub: 'Les transports publics urbains',
      train: 'le train',
      moto: 'La moto / le scooter',
      car: 'La voiture (conducteur ou passager)',
      plane: "L'avion",
      pub_train: 'Les transports publics (y compris le train)',
      car_moto: 'La voiture ou la moto',
      combined: 'Une combinaison de ces modes de transport',
    },
    trav_pro:
      'Dans quelle mesure devez-vous effectuer des déplacements dans le cadre de votre travail ?',
    trav_pro_option: {
      local: 'Local',
      local_hint: '<15 km : Grand Genève',
      region: 'National',
      region_hint: '15-400 km : Lausanne, Berne, Zürich',
      inter: 'International',
      inter_hint: '>400 km : Paris, Londres, Amsterdam',
    },
    freq_trav_pro_local_hint: 'Local',
    freq_trav_pro_region_hint: 'National',
    freq_trav_pro_inter_hint: 'International',

    days_per_month: 'En jours par mois',
    freq_mod_pro:
      'A quelle fréquence utilisez vous les modes suivants pour vos déplacements professionnels ?',
    importance:
      "Quelle est l'importance des aspects suivants pour vous, dans votre mobilité quotidienne ?",
    importance_hint: 'Sur une échelle de 1 (pas important du tout) à 5 (très important)',
    importance_time: 'Temps de trajet',
    importance_cost: 'Coût',
    importance_flex: 'Flexibilité / indépendance',
    importance_rel: 'Fiabilité / ponctualité',
    importance_comfort: 'Confort du trajet',
    importance_most: 'Possibilité de mettre à profit le temps de trajet',
    importance_env: 'Environnement (réduction du la pollution)',
    needs:
      'Dans quelle mesure les modes de transport suivants sont-ils adaptés à vos besoins de mobilité quotidienne ?',
    needs_hint: 'Sur une échelle de 1 (pas du tout adapté) à 5 (tout à fait adapté)',
    adjectives: 'Quels adjectifs associez-vous aux modes de transport suivants ?',
    adjectives_hint: 'Sélectionnez 3 adjectifs par mode de transport',
    adjectives_option: {
      fast: 'Rapide',
      slow: 'Lent',
      cheap: 'Economique',
      expensive: 'Cher',
      practical: 'Pratique',
      impractical: 'Pas pratique',
      ecological: 'Ecologique',
      polluting: 'Polluant',
      safe: 'En sécurité',
      dangerous: 'Dangereux',
      pleasant: 'Plaisant',
      unpleasant: 'Déplaisant',
      autonomous: 'Autonome',
      constraining: 'Contraignant',
      relax: 'Relaxant',
      tiring: 'Fatigant',
      healthy: 'Bon pour la santé',
      bad_weather: 'Exposé aux intempéries',
      reliable: 'Fiable',
      congested: 'Embouteillé',
    },
    comments:
      'Merci! Avez-vous des commentaires sur ce questionnaire ou sur la démarche de plan de mobilité ?',
    recommendations:
      'Les modes de transport suivants sont recommandés pour vos déplacements domicile-travail',
    recommendations_pro:
      'Les modes de transports suivants sont recommandés pour vos déplacements professionnels :',
    actions:
      'Pas de mesures | La mesure de votre employeur : {actions} | Les mesures de votre employeur : {actions}',
    actions_global:
      "Pas de mesures globales | Votre employeur vous propose aussi la mesure d'aide à la mobilité : {actions} | Votre employeur vous propose aussi les mesures d'aide à la mobilité : {actions}",
  },
  main_mode: {
    walking: 'Actuellement, vous vous rendez au travail principalement en marchant.',
    bike: 'Actuellement, vous vous rendez au travail principalement en vélo (ou VAE).',
    pub: 'Actuellement, vous vous rendez au travail principalement en transports publics.',
    moto: 'Actuellement, vous vous rendez au travail principalement en moto ou en scooter.',
    car: 'Actuellement, vous vous rendez au travail principalement en voiture.',
    train: 'Actuellement, vous vous rendez au travail principalement en train.',
    combined:
      'Actuellement, vous vous rendez au travail avec une combinaison de modes de transport.',
    sustainable:
      'Vos déplacements domicile-travail sont déjà durables. Les alternatives suivantes sont à votre disposition :',
    not_sustainable:
      'Sur la base des informations que vous avez renseignées, les alternatives suivantes vous sont recommandées :',
    actions:
      'Votre employeur met en oeuvre les mesures suivantes afin de promouvoir la mobilité durable',
  },
  reco: {
    covoit: 'Le covoiturage',
    elec: 'La voiture électrique',
    inter: "L'intermodalité",
    marche: 'La marche',
    tpu: 'Les transports publics',
    train: 'Le train',
    vae: 'Le vélo à assistance électrique',
    velo: 'Le vélo',
  },
  actions: {
    budget: 'Budget mobilité',
    wfh: 'Possibilité de télétravailler au domicile',
    wftp: 'Possibilité de télétravailler dans un tiers-lieu',
    tpg_pass: 'Abonnement transports publics (UNIRESO)',
    lex_pass: 'Abonnement léman express',
    cff_pass_ag: 'Abonnement train (abonnement général)',
    cff_pass_dtp: 'Abonnement train (demi tarif plus)',
    cff_pass_dt: 'Abonnement train (demi tarif)',
    pnr_pass: 'Abonnement P+R',
    shuttle: 'Navette depuis la gare la plus proche',
    velo_station: 'Abonnement vélo-station',
    bike_subs: "Subvention à l'achat d'un vélo ou vélo électrique",
    shower: 'Douches, casiers et vestiaires',
    bike_parking: 'Stationnement vélo sécurisé',
    ebike_charging: 'Possibilité de chargement vélo électrique',
    bike_equipment: "Subvention à l'achat d'équipement de sécurité vélo",
    carpool_subs: 'Remboursement des trajets de covoiturage',
    carpool_connect: 'Mise en relation avec des collègues pour covoiturer',
    carpool_parking: 'Places de stationnement réservées covoiturage',
    ev_charging: 'Chargement de véhicule électrique sur le lieu de travail',
    mobility_pass: 'Abonement autopartage mobility',
    ebike_fleet: 'Flotte de vélos électriques pour les déplacements professionnels',
    tpu_pro: 'Abonnement transports publics (UNIRESO)',
    train_pro: 'Abonnement train (abonnement général)',
    ev_fleet: 'Flotte de véhicules électriques pour les déplacements professionnels',
  },
  benefits: {
    show: 'Voir les avantages',
    hide: 'Masquer les avantages',
  },
  resume: 'Continuer le questionaire',
  start_new: 'Ou recommencer du début',
  start: 'Démarrer',
  token: 'Identifiant',
  lookup_address_or_select_on_map: 'Rechercher une adresse ou sélectionner sur la carte',
  type_enter_to_lookup_address: "Taper l'adresse puis Entrée pour chercher",
  welcome: 'Bienvenue sur le {brand}',
  welcome_intro:
    'Veuillez remplir ce questionnaire afin de pouvoir vous proposer les mesures de mobilité les plus pertinentes pour vous',
  no_results: 'Pas de résultat',
  local: 'Local',
  regional: 'National',
  international: 'International',
  finish: 'Fin',
  next: 'Suivant',
  previous: 'Précédent',
}
