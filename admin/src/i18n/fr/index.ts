const transportationModes = {
  // --- Active Mobility ---
  walking: 'Marche',
  walk: 'Marche',
  marche: 'Marche',
  bike: 'Vélo',
  velo: 'Vélo',
  ebike: 'Vélo électrique',
  vae: 'Vélo à assistance électrique',
  cargo: 'Vélo cargo',

  // --- Motorcycles & Small Motorized ---
  moto: 'Moto / scooter',
  elec_moto: 'Moto / scooter électrique',

  // --- Public Transport ---
  pub: 'Transports publics urbains',
  pub_train: 'Transports publics (y compris le train)',
  tpu: 'Transports publics',
  transit: 'Transports publics',
  bus: 'Bus',
  train: 'Train',
  rail: 'Train',

  // --- Private Motorized Vehicles (Cars) ---
  car: 'Voiture',
  car_driver: 'Voiture (en tant que conducteur)',
  car_passenger: 'Voiture (en tant que passager)',
  car_moto: 'Voiture ou moto',
  elec: 'Voiture électrique',
  ev: 'Véhicule électrique',
  carpool: 'Covoiturage',
  covoit: 'Covoiturage',

  // --- Long Distance / Heavy Transport ---
  truck: 'Camion',
  elec_truck: 'Camion / utilitaire électrique',
  plane: 'Avion',
  boat: 'Bateau',

  // --- Alternative & Abstract ---
  avoid: 'Éviter le déplacement',
  inter: 'Intermodalité',
  combined: 'Combiné',
  other: 'Autre',
  unknown: 'Inconnu',
}

const emissionsLabels = {
  emissions: 'Émissions CO₂ totales',
  journeys: 'Nombre de trajets',
  distances: 'Distance totale',
  current: 'Actuel',
  postSaving: 'Total après recommandations',
}

export default {
  main: {
    brand: 'Mobilyse',
  },
  company: {
    label: 'Organisation',
    actions: 'Mesures employeur',
    employer_measures_description:
      'Cette section permet d’ajouter, si besoin, des mesures personnalisées mises en place par l’organisation. Lors de la création ou l’édition d’une campagne, celles-ci s’ajouteront aux mesures par défaut qui vous seront proposées.',
    custom_actions: 'Mesures spécifiques',
    custom_actions_hint:
      'Ajouter ou supprimer des mesures employeur personnalisées qui faciliteront la mobilité des collaborateur·trice·s. Ces mesures sont regroupées par mode de transport ou sont globales.',
    administrators: 'Administrateur·trice',
    administrators_hint:
      "L'adresse email des administrateur·trice pour cette organisation (tapez Entrée pour ajouter une entrée).",
    mobility_advisors: 'Conseiller·ère mobilité',
    mobility_advisors_hint:
      "L'adresse email des conseiller·ère·s mobilité pour cette organisation (tapez Entrée pour ajouter une entrée).",
    contact_name: 'Nom du contact',
    contact_name_hint: 'Le nom de la personne de contact pour la mobilité dans cette organisation.',
    contact_email: 'Email du contact',
    contact_email_hint:
      "L'adresse email de la personne de contact pour la mobilité dans cette organisation.",
    contact_info: 'Informations de contact',
    info_url: "Lien d'information",
    info_url_hint:
      "Un lien vers plus d'informations sur les options de mobilité de cette organisation.",
    can_be_cited: 'Peut être citée comme utilisateur de mobilyse',
    can_be_cited_toggle:
      'Je ne souhaite pas que la Fondation Modus cite le nom de mon organisation comme utilisateur de mobilyse',
    your_role: 'Votre rôle',
    roles: {
      admin: 'Administrateur·trice',
      mobility_advisor: 'Conseiller·ère mobilité',
      none: 'Aucun',
    },
  },
  campaign: {
    label: 'Campagne',
    slug: 'Identifiant',
    slug_hint:
      "Identifiant unique pour l'URL de la campagne (ex. 'printemps-2024-enquete-mobilite'). Seules les lettres, chiffres, tirets et underscores sont autorisés.",
    description: 'Description',
    with_professional_questions: 'Inclure des questions sur les déplacements professionnels',
    with_professional_questions_hint: "Par défaut, nous vous donnons la possibilité d'étudier les déplacements domicile-travail et les déplacements professionnels des collaborateur·trice·s. Si cette dernière option (déplacements professionnels) ne vous intéresse pas, vous pouvez retirer cette partie du questionnaire avec ce bouton.",
    with_actions: 'Avec des mesures employeur spécifiques à cette campagne',
    employer_measures_hint:
      'Vous pouvez préciser ici les mesures déjà en place en soutien à la mobilité de vos collaborateur·rice·s. Les mesures qui apparaissent ici sont une sélection de mesures "par défaut" ainsi que les "mesures spécifiques" entrées dans la section précédente "Mesures employeur".',
    rewards: {
      toggle: 'Je souhaite récompenser les participant·e·s.',
      hint: 'Récompenser les collaborateur·trice·s répondant au questionnaire (que ce soit systématiquement ou via un tirage au sort / lotterie) permet d\'obtenir un taux plus élevé de réponses. Si vous souhaitez récompenser les participant·e·s, mobilyse peut fournir une "attestation" (document PDF) à la fin du remplissage du questionnaire à chaque répondant·e, qui prouvera sa participation. Le ou la répondant·e pourra alors transférer cette attestation auprès de la personne en charge d\'organiser les récompenses. Nous vous proposons de personnaliser le message qui sera affiché sur cette attestation, en expliquant la démarche à suivre (à qui transférer cette preuve, comment récupérer sa récompense, quelles sont les modalités du tirage au sort...).',
      default_message:
        "Bravo et merci pour votre participation à l'enquête mobilyse ! Vos réponses sont précieuses et nous permettront de mieux comprendre comment vous aider dans votre mobilité au quotidien. En téléchargeant ce document et en le transférant à [...], vous pourrez profiter de [...].",
      message_placeholder: 'Message pour les participants',
    },
    contact_name: 'Nom du contact',
    contact_name_hint:
      "Le nom de la personne de contact pour la mobilité dans cette organisation (si différent du contact de l'organisation).",
    contact_email: 'Email du contact',
    contact_email_hint:
      "L'adresse email de la personne de contact pour la mobilité dans cette organisation (si différent du contact de l'organisation).",
    contact_info: 'Informations de contact',
    info_url: "Lien d'information",
    info_url_hint:
      "Un lien vers plus d'informations sur les options de mobilité de cette organisation (si différent du lien d'information de l'organisation).",
    nb_employees: 'Nombre de collaborateur·trice·s',
    nb_employees_hint:
      'Fournissez le nombre de collaborateur·trice·s travaillant dans cette organisation ou sur le(s) lieu(x) de travail associé(s) à cette campagne. Cette information est utilisée pour contextualiser les statistiques de mobilité.',
    csv_missing_columns:
      'Le fichier CSV téléversé est manquant les colonnes requises suivantes : {columns}.',
    import_workplaces_hint:
      'Téléversez un fichier CSV pour ajouter/mette à jour plusieurs lieux de travail à la campagne en une seule fois. Le fichier doit contenir les colonnes suivantes : name, address, lat, lon.',
    workplaces: {
      title: 'Lieux de travail',
      number: 'Nombre de lieux de travail',
      hint: 'Déclarez les lieux de travail associés à cette campagne : soit les lieux de travail peuvent être déclarés par le participant ou au moins un est requis.',
      name: 'Nom',
      name_hint: 'Nom du lieu de travail (ex. "Hub logistique 12").',
      required: 'Au moins un lieu de travail doit être défini pour la campagne.',
      open_workplaces: 'Lieux de travail ouverts',
      open_workplaces_hint:
        "Si activé, les participants pourront sélectionner n'importe quel lieu de travail lors du remplissage de l'enquête.",
      workplaces_list: 'Liste des lieux de travail connus',
      show_isochrone: "Afficher l'isochrone",
      isochrones_hint:
        "Une isochrone est une carte représentant les lieux accessibles, depuis un point de départ, avec certains modes, dans un temps imparti. L'isochrone montre ici quelle partie du territoire est accessible avec différents modes de transport depuis un lieu de travail, vous permettant de visualiser notamment jusqu'où les collaborateur·trice·s peuvent se rendre depuis ce site.",
    },
    email_template: {
      buttonText: "Modèle d'email",
      modalTitle: "Modèle d'email pour {campaign}",
      contactEmail: 'Email de contact',
      contactName: 'Nom du contact',
      surveyLink: 'Lien vers le sondage',
      defaultContactEmail: 'EMAIL_DE_CONTACT',
      defaultContactName: 'NOM_DE_CONTACT',
      template: `Chères collaboratrices, chers collaborateurs,

Mobilyse est un outil proposé par la Fondation Modus et l'EPFL pour aider les organisations à adapter les aides à la mobilité proposées aux collaboratrices et collaborateurs. Nous utilisons aujourd'hui cet outil pour comprendre comment vous accompagner au mieux dans votre mobilité quotidienne, que ce soit vos déplacements domicile-travail ou vos déplacements professionnels (dans le cadre de vos fonctions). 🚲🚃🚶🚈

Nous avons pour cela besoin de mieux connaitre vos pratiques et aspirations, et vous invitons à participer en répondant au questionnaire suivant. Cela vous prendra 10 minutes maximum et l'outil vous donnera directement des suggestions personnalisées pour vos déplacements :

[{surveyLink}]({surveyLink})

Pourquoi participer ?

- Obtenir des recommandations pour vos déplacements basées sur votre situation (desserte en transports, distances, contraintes, votre avis sur les modes de transport, vos priorités…) ✅
- Connaître les aides adaptées que votre organisation met en place pour vous 🎯
- Donner votre avis sur l’accompagnement proposé pour votre mobilité, et aider ainsi à le faire évoluer 🙋
- Contribuer à l’amélioration d’un outil gratuit et open access 🎁

Le questionnaire est anonyme et aucune donnée personnelle n’est enregistrée. 🔐 A noter, vous pouvez sélectionner la langue (FR/EN) en haut à droite. Pour en savoir plus sur mobilyse, vous pouvez vous rendre ici : https://modus-ge.ch/project/mobilyse/.

Nous vous remercions pour votre précieuse collaboration ! En cas de question, n’hésitez pas à contacter : [{contactEmail}](mailto:{contactEmail}).

{contactName}`,
      copyTemplate: "Copier le modèle d'email",
      copyTemplateSuccess: "Modèle d'email copié dans le presse-papiers",
      copyTemplateError: "Erreur lors de la copie du modèle d'email. Veuillez réessayer.",
    },
  },
  docs: {
    title: 'Documentation',
    hint: 'Trouvez des guides et des ressources pour vous aider à utiliser mobilyse.',
    general: {
      title: 'Général',
      privacy: {
        title: 'Politique de confidentialité',
        caption: 'En savoir plus sur la politique de confidentialité de mobilyse',
      },
      terms: {
        title: "Conditions d'utilisation",
        caption: "En savoir plus sur les conditions d'utilisation de mobilyse",
      },
      what_next: {
        title: 'Et après ?',
        caption:
          'Découvrez les étapes suivantes après la création de votre organisation et de votre campagne',
      },
      need_more_help: {
        title: 'Vous ne trouvez pas la réponse à votre question ?',
        caption:
          "Contactez-nous pour toute question ou besoin d'accompagnement concernant la gestion de vos campagnes de mobilité",
      },
    },
    organisations: {
      title: 'Organisations',
      create: {
        title: 'Comment créer une organisation ?',
        caption: 'Un guide pour créer une organisation et gérer ses campagnes',
      },
      settings: {
        title: "Comment gérer les paramètres d'une organisation ?",
        caption:
          "Un guide pour mettre à jour les informations et les paramètres d'une organisation",
      },
      employer_measures: {
        title: 'Comment gérer les aides à la mobilité par défaut ?',
        caption: 'Un guide pour gérer les aides employeur pour votre organisation',
      },
      custom_measures: {
        title: 'Comment ajouter des aides à la mobilité personnalisées ?',
        caption: 'Un guide pour gérer les aides personnalisées pour votre organisation',
      },
      common_issues: {
        title: 'Problèmes courants',
        caption:
          "Solutions aux problèmes fréquemment rencontrés lors de la gestion d'une organisation",
      },
      best_practices: {
        title: "Bonnes pratiques pour la création d'une organisation",
        caption: 'Conseils pour structurer votre organisation et vos campagnes de manière efficace',
      },
      mobility_advisor: {
        title: 'Quel est le rôle de conseiller·ère mobilité ?',
        caption:
          'Apprenez à utiliser un·e conseiller·ère mobilité pour accompagner votre organisation',
      },
    },
    campaigns: {
      title: 'Campagnes',
      description:
        "Les campagnes sont des enquêtes ou initiatives de mobilité limitées dans le temps au sein d'une organisation. Chaque organisation peut avoir plusieurs campagnes.",
      settings: {
        title: "Comment gérer les paramètres d'une campagne ?",
        caption: 'Apprenez à créer et à mettre à jour les paramètres de votre campagne',
      },
      share_link: {
        title: 'Comment partager le lien vers le questionnaire ?',
        caption:
          'Apprenez à partager le lien vers le questionnaire de votre campagne auprès des participant·e·s',
      },
      isochrone: {
        title: "Qu'est-ce qu'une isochrone et comment l'afficher sur la carte ?",
        caption: "Apprenez à afficher l'isochrone sur la carte",
      },
      reward: {
        title: 'Comment récompenser les participant·e·s qui répondent au questionnaire ?',
        caption: 'Apprenez comment récompenser les participant·e·s de votre campagne',
      },
      common_issues: {
        title: 'Problèmes courants',
        caption: "Solutions aux problèmes fréquemment rencontrés lors de la gestion d'une campagne",
      },
      best_practices: {
        title: "Bonnes pratiques pour la création d'une campagne",
        caption:
          'Conseils et recommandations pour tirer le meilleur parti des fonctionnalités de campagne dans Mobilyse',
      },
      dashboard: {
        title: 'Comment se servir du Tableau de bord pour analyser les résultats ?',
        caption:
          'Apprenez à utiliser le Tableau de bord de campagne pour suivre les résultats et les statistiques de votre campagne',
      },
    },
  },
  role: {
    'platyp-user': 'Utilisateur·trice',
    'platyp-admin': 'Administrateur·trice',
  },
  participant: {
    identifier: 'Identifiant',
    age_class: "Classe d'âge",
    employment_rate: "Taux d'emploi",
    remote_work_rate: 'Taux de télétravail',
    company_vehicle: 'Véhicule de fonction',
    status: {
      open: 'Ouvert',
      completed: 'Terminé',
    },
  },
  actions: {
    personnal: 'Personnel',
    professional: 'Professionnel',
    mesures_globa_label: 'Global',
    mesures_globa_hint: '',
    mesures_tpu_label: 'Transports publics',
    mesures_tpu_hint: '',
    mesures_train_label: 'Train',
    mesures_train_hint: '',
    mesures_inter_label: 'Inter-modalité',
    mesures_inter_hint: '',
    mesures_velo_label: 'Vélo',
    mesures_velo_hint: '',
    mesures_covoit_label: 'Covoiturage',
    mesures_covoit_hint: '',
    mesures_elec_label: 'Electrique',
    mesures_elec_hint: '',
    mesures_pro_globa_label: 'Global',
    mesures_pro_globa_hint: '',
    mesures_pro_velo_label: 'Vélo',
    mesures_pro_velo_hint: '',
    mesures_pro_tpu_label: 'Transports publics',
    mesures_pro_tpu_hint: '',
    mesures_pro_train_label: 'Train',
    mesures_pro_train_hint: '',
    mesures_pro_elec_label: 'Electrique',
    mesures_pro_elec_hint: '',
    budget: 'Budget mobilité',
    wfh: 'Possibilité de télétravailler au domicile',
    wftp: 'Possibilité de télétravailler dans un tiers-lieu',
    wfro: 'Possibilité de télétravailler occasionnellement',
    videoconf:
      'Système de visioconférence réservable au travail pour limiter les longs déplacements',
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
    bike_courses: 'Mise en place de cours pour la pratique du vélo sur le lieu de travail',
    carpool_subs: 'Remboursement des trajets de covoiturage',
    carpool_connect: 'Mise en relation avec des collègues pour covoiturer',
    carpool_parking: 'Places de stationnement réservées covoiturage',
    ev_charging: 'Chargement de véhicule électrique sur le lieu de travail',
    mobility_pass: 'Abonnement autopartage mobility',
    ebike_fleet: 'Flotte de vélos électriques pour les déplacements professionnels',
    tpu_pro: 'Abonnement transports publics (UNIRESO)',
    tpu_rmb: 'Remboursement des billets de transports publics pour les déplacements professionnels',
    train_pro: 'Abonnement train (abonnement général)',
    train_obl:
      "Obligation d'utiliser le train dans la mesure du possible, pour les voyages professionnels",
    train_rmb: 'Remboursement des billets de train pour les déplacements professionnels',
    ev_fleet: 'Flotte de véhicules électriques pour les déplacements professionnels',
  },
  stats: {
    title: 'Rapport de mobilité',
    no_charts_to_export: 'Aucun graphique à exporter en PDF.',
    charts_height: 'Hauteur des graphiques',
    records_count: "Nombre d'enregistrements",
    in_progress: 'En cours',
    completed: 'Terminé',
    pending: 'En attente',
    filter_by_zone: 'Filtrer par zone',
    switch_to_carousel: 'Passer en vue carrousel',
    switch_to_grid: 'Passer en vue grille',
    pdf_report: 'Rapport PDF',
    nb_employees: 'Nombre de collaborateur·trice·s',
    percent_employees: '% de collaborateur·trice·s',
    total: 'N : {count}',
    no_data: 'Aucune donnée disponible',
    observed: 'Données des participant·e·s',
    participants_median: 'Médiane des participant·e·s',
    geneva_median: 'Médiane de la région de Genève',
    reference_data: 'Données de référence (canton de Genève)',
    units: {
      tco2eq_per_year: 'tCO₂eq/an',
    },
    sections: {
      mobility_analysis: {
        title: 'Diagnostic de mobilité',
        description: `Les graphes ci-dessous présentent des informations sur les pratiques actuelles de mobilité des participant·e·s: leur répartition géographique, leur usage des modes de transport, leurs équipements et leurs contraintes.

Certains impacts sont aussi calculés :
- sur l'environnement, via les émissions de gaz à effet de serre calculées avec les facteurs mobi-tools [(source)](https://www.i14y.admin.ch/fr/catalog/dataservices/171b09a4-5b5f-4577-8921-3af7fc6eee39/description)
- sur la santé des participant·e·s, via les dépenses énergétiques (metabolic equivalent task) quotidiennes moyennes lors des déplacements. Les recommandations de la Confédération et l'OMS préconisent 150 minutes en effort modéré (vélo/marche rapide) par semaine, soit 150kcal/jour. [(source)](https://www.who.int/fr/news-room/fact-sheets/detail/physical-activity). Le manque d'activité physique a des effets directs sur la santé physique et mentale (psychique, cognitive), et impacte ainsi directement le bien-être des collaborateur·trice·s, les taux d'arrêts maladie, la productivité ou encore l'ambiance de travail.`,
      },
      mobility_potentials: {
        title: 'Potentiels de mobilité',
        description: `Cette section expose les recommandations personnalisées suggérées aux participant·e·s. Mobilyse indique ainsi quels modes sont les plus susceptibles de convenir aux collaborateur·trice·s en fonction de leurs habitudes, contraintes, désirs, localisation résidentielle et de travail… Certains graphes illustrent également les gains potentiels en matière d'impact sur les émissions de gaz à effet de serre et de santé, dans le cas où tou·te·s les participant·e·s adopteraient les recommandations formulées par mobilyse.`,
        insights: {
          most_potential:
            "Le mode de transport avec le plus fort potentiel d'utilisateur.trices est : **{mode}** (recommandé à **{percentage}%** des collaborateur.trices ayant répondu)",
          biggest_emission_reduction:
            'Le mode de transport permettant de générer la plus forte baisse des émissions de CO2 est : **{mode}** pour une réduction de **{reduction} {unit}**, soit **{percentage}%** du gain total potentiel pour les collaborateur.trices ayant répondu.',
          biggest_emission_reduction_extrapolation:
            'En extrapolant aux **{collaborators_count}** collaborateur.trices de votre organisation, cette réduction est estimée à **{reduction} {unit}**.',
          biggest_physical_activity_gain:
            "Le mode de transport permettant d'augmenter le plus l'activité physique des collaborateur.trice.s est : **{mode}**. Ce scénario permet à **{collaborators_count}** collaborateur.trice.s supplémentaires d'atteindre le niveau de dépenses physiques recommandées par l'OMS par jour (150 kcal/jour/pers).",
        },
      },
      behavioural_changes: {
        title: 'Motiver les changements de comportement',
        description: `Cette dernière section apporte des informations sur la volonté des participant·e·s de suivre ou non les recommandations qui leur ont été faites, et leurs besoins ou désirs pour déclencher ces changements de comportement. Cela peut permettre d'orienter vos décisions et de cibler les aides à la mobilité que vous pourriez envisager.`,
      },
      home_to_work: 'Déplacements domicile-travail',
      professional_travel: 'Déplacements professionnels',
    },
    equipments: {
      title: 'Équipements de mobilité',
      labels: {
        bike: 'Vélo',
        upt_subs: 'Abonnement de transports\npublics urbains',
        train_subs: 'Abonnement de train',
        car_driver: 'Voiture (en tant que conducteur)',
        moto: 'Moto / scooter / cyclomoteur',
        ebike: 'Vélo à assistance électrique',
        mob_subs: 'Abonnement de mobilité\npartagée',
        car_passenger: 'Voiture (en tant que passager)',
        car: 'Voiture (conducteur/passager)',
        ev: 'Véhicule électrique',
      },
      mrmt_source:
        'Données de référence, canton de Genève [Microrecensement Mobilité et Transports, 2023](https://statistique.ge.ch/tel/publications/2023/analyses/communications/an-cs-2023-71.pdf)',
    },
    constraints: {
      title: 'Contraintes de mobilité',
      labels: {
        dependent: 'Emmener des enfants\nou des personnes dépendantes',
        heavy: 'Transport de matériel\nlourd ou encombrant',
        night: 'Horaires spéciaux',
        disabled: 'Carte de stationnement pour\npersonne à mobilité réduite',
        other: 'Autre *',
        none: 'Aucune contrainte',
      },
      texts: {
        other:
          'Le détail des autres contraintes est accessible en téléchargeant le détail des données.',
      },
    },
    locationsHeatmap: {
      title: 'Répartition géographique des lieux de résidence et de travail',
      households: 'Lieux de domicile',
      workplaces: 'Lieux de travail enregistrés',
    },
    travel_time: {
      title: 'Temps de trajet',
      xaxis: 'Temps (min)',
      texts: {
        default:
          'Le temps de trajet domicile-travail médian sur le canton de Genève est de 30 minutes (enquête Modus, 2024)',
        specific:
          'Le temps de trajet domicile-travail médian des répondant·es est de {median} minutes.',
      },
    },
    reco_dt2: {
      title: 'Répartition modale potentielle',
      labels: {
        ...transportationModes,
      },
    },
    reco_pros: {
      title: 'Recommandations (professionnel)',
      labels: {
        ...transportationModes,
      },
    },
    freq_mod: {
      title: 'Répartition modale',
      title_mrmt: 'Données de référence (canton de Genève)',
      labels: {
        ...transportationModes,
      },
      texts: {
        default:
          'Le mode Voiture est le mode le plus utilisé dans le canton de Genève ([Microrecensement Mobilité et Transports, 2015](https://statistique.ge.ch/tel/publications/2023/analyses/communications/an-cs-2023-71.pdf)).',
        specific:
          'Le mode {top_1} est le plus utilisé par les répondant·es, suivi de {top_2} et {top_3}.',
      },
    },
    freq_mod_pro: {
      title: 'Répartition modale (déplacements professionnels)',
      xaxis: 'Trajets par année',
      labels: {
        ...transportationModes,
        local: 'Local',
        region: 'Régional',
        national: 'National',
        europe: 'Européen',
        inter: 'International',
      },
    },
    emissions_freq_mod: {
      title: 'Émissions de CO₂ par mode de transport',
      yaxis: 'Émissions CO₂ par trajet (kgCO₂éq)',
      xaxis: 'Trajets par année',
      labels: {
        ...transportationModes,
        ...emissionsLabels,
      },
      texts: {
        specific:
          "{carMotoJourneysPercentage}% des trajets des répondant·es sont réalisés en voiture/moto/scooter, représentant {carMotoEmissionsPercentage}% des émissions de CO₂ annuelles pour l'entreprise.",
      },
    },
    emissions_reductions_mod: {
      title: 'Potentiel de réduction sur les émissions liées aux déplacements pendulaires',
      yaxis: 'Émissions évitées (kgCO₂éq)',
      xaxis: 'Mode recommandé',
      series: 'Réduction potentielle',
      labels: {
        ...transportationModes,
        ...emissionsLabels,
      },
      texts: {
        default:
          "Ce graphe montre la diminution des émissions CO₂ allouée à chaque recommandation, dans le cas où les collaborateur·trice·s suivent celles-ci : c'est le potentiel gain en termes d'émissions.",
        specific:
          'Les recommandations permettraient de passer de {current_emissions} à {new_emissions} {unit} / an sur les participant·e·s ayant répondu. Cela correspond à {cheeseburgers} cheeseburgers, ou encore à la fabrication de {vacuum} aspirateurs ou {shirt} chemises en coton [source : [https://impactco2.fr/doc](https://impactco2.fr/doc)].',
      },
    },
    emissions_reductions_share: {
      title: "Répartition des gains d'émissions par mode de transport",
      series: 'Réduction potentielle',
      labels: {
        ...transportationModes,
        ...emissionsLabels,
      },
      texts: {
        default:
          'Ce graphe affiche la part de réduction d’émissions de CO₂éq correspondant à chaque mode recommandé, dans le cas où les collaborateur·trice·s suivraient les recommandations.',
        specific:
          "{percentage}% de réduction potentielle dépendent d'une recommandation principale {mode}.",
      },
    },
    emissions_freq_mod_pro: {
      title: 'Émissions de CO₂ par mode de transport (déplacements professionnels)',
      yaxis: 'Émissions CO₂ par trajet (kgCO₂éq)',
      xaxis: 'Trajets par année',
      labels: {
        ...transportationModes,
        ...emissionsLabels,
      },
      texts: {
        specific:
          '{firstPercent}% des émissions sont dues à {firstMode}, {secondPercent}% à {secondMode}. Chaque trajet en {firstMode} émet en moyenne {firstEmissions}kgCO₂éq/trajet, contre moins de {remainingEmissions}kgCO₂éq/trajet pour les autres.',
      },
    },
    emissions_reductions_mod_pro: {
      title: 'Potentiel de réduction sur les émissions liées aux déplacements professionnels',
      yaxis: 'Émissions évitées (kgCO₂éq)',
      xaxis: 'Mode recommandé',
      series: 'Réduction potentielle',
      labels: {
        ...emissionsLabels,
      },
      texts: {
        default:
          "Ce graphe montre la diminution des émissions CO₂ allouée à chaque recommandation, dans le cas où les collaborateur·trice·s suivent celles-ci : c'est le potentiel gain en termes d'émissions.",
        specific:
          'Les recommandations permettraient de passer de {current_emissions} à {new_emissions} {unit} / an sur les participant·e·s ayant répondu. Cela correspond à la fabrication de {laptop} ordinateurs portables, à l’envoi de {email_sent} emails ou à {visio_hour} heures de visioconférence [source : [https://impactco2.fr/doc](https://impactco2.fr/doc)].',
      },
    },
    mod_reco: {
      title: 'Recommandations de report modal',
      texts: {
        default:
          'Ce graphe montre quels modes de transport ont été recommandés (à droite) en fonction du mode utilisé actuellement (à gauche).',
        specific:
          'Le mode "{mode}" semble être le mode de transport le plus pertinent pour les répondants.',
      },
    },
    mod_reco_pro: {
      title: 'Recommandations de changement modal (professionnel)',
      texts: {
        default:
          'Ce graphe montre quels modes de transport ont été recommandés (à droite) en fonction du mode utilisé actuellement (à gauche).',
        specific:
          'Le mode "{mode}" semble être le mode de transport comportant le potentiel de report modal le plus élevé.',
      },
    },
    energy_journey: {
      title_current: 'Dépenses énergétiques quotidiennes moyennes lors des déplacements',
      title_reco: 'Dépenses énergétiques quotidiennes moyennes potentielles lors des déplacements',
      title_share:
        'Modes de transport avec le potentiel de gain le plus élevé en matière de dépenses énergétiques ',
      yaxis: 'Énergie dépensée (kcal/jour/pers)',
      xaxis: 'Ensemble des participant·e·s (trié·e·s par énergie dépensée)',
      whoMin: 'Activité physique minimum recommandée par l’OMS',
      participantsAverage: 'Activité physique moyenne des participants',
      texts: {
        default:
          "L'OMS recommande d'exercer une activité physique active modérée (comme la marche ou le vélo) brûlant quotidiennement environ 150 kcal/jour/pers, soit l'équivalent de 37 min de marche, 23min de fitness ou 14min de football par jour.",
        specific_current:
          'Actuellement, les participant·e·s dépensent en moyenne {energy} kcal/jour/pers pour leurs déplacements domicile-travail.',
        specific_reco: `Si les recommandations faites par Mobilyse sont suivies, la dépense énergétique moyenne augmentera de {added_energy} kcal/jour/pers (l'équivalent de {yoga_min} minutes de yoga par personne et par jour).
          De plus, {count} personnes supplémentaires passeront au-dessus des recommandations d'activité physique journalière de l'OMS, passant de {percent_current}% à {percent_potential}%.`,
        default_share:
          "Ce graphe montre quels sont les modes recommandés qui amélioreraient le plus l'activité physique des participant·e·s.",
        specific_share:
          "{percentage}% de l'amélioration de l'activité physique des participant·e·s viendrait de {mode}.",
      },
    },
    behavior_change_levers: {
      title: 'Mesures souhaitées pour adopter les recommandations de mobilité durable formulées',
      labels: {
        finance: 'Aides financières',
        flexibility: 'Flexibilité',
        collective: 'Changement collectif',
        environment: 'Aménagement environnement',
        autres: 'Autres',
        total: 'Total',

        ...transportationModes,
        allModes: 'Tous les modes',
      },
      texts: {
        info: 'Les modes affichés sont ceux qui ont été recommandés à suffisamment de personnes ayant répondu à cette question.',
        default:
          "Ce graphique permet de comprendre comment les participant·e·s souhaiteraient être accompagné·e·s dans l'évolution de leur mobilité.",
        specific: "L'aide dont les participant·e·s estiment avoir le plus besoin est {lever}.",
      },
    },
    behavior_change_motivation: {
      title: "Volonté d'adopter les recommandations",
      labels: {
        l1: 'Pas intéressé·e',
        l2: 'Plutôt pas',
        l3: 'Neutre',
        l4: 'Plutôt motivé·e',
        l5: 'Très motivé·e',

        ...transportationModes,
        allModes: 'Tous les modes',
        autres: 'Autres',
        total: 'Total',
      },
      texts: {
        info: 'Les modes affichés sont ceux qui ont été recommandés à suffisamment de personnes ayant répondu à cette question.',
        default:
          'Ce graphe montre la motivation des participant·e·s à adopter les recommandations qui leur sont faites par Mobilyse pour leur déplacement domicile-travail.',
        specific:
          'Ce graphe montre la motivation des participant·e·s à adopter les recommandations qui leur sont faites par Mobilyse pour leur déplacement domicile-travail, en fonction du mode recommandé. Au total, {percentage}% des participant·e·s sont motivé·e·s pour adopter les recommandations qui leur sont faites.',
      },
    },
    equipments_by_recommendations: {
      title: 'Équipements par recommandations',
      tooltip: `{count} des participant·e·s qui ont obtenu la recommandation "{reco}" sont équipés avec "{equipment}".<br />
      Cela représente {percentage}% des participant·e·s ayant obtenu la recommandation "{reco}".
      `,
      simpleMode: 'Mode simple',
      labels: {
        ...transportationModes,

        mob_subs: "Abo. d'autopartage",
        train_subs: 'Abo. de train',
        upt_subs: 'Abo. de transports publics',
        inter: 'Intermodalité',
        tpu: 'Transports publics',

        allModes: 'Tous les modes',
      },
      texts: {
        default:
          'Ce tableau montre les équipements des participant·e·s en fonction des recommandations qui leur ont été faites. Cela permet de comprendre si les participant·e·s ont dans leur ensemble déjà accès au mode qui leur a été recommandé, ou si il serait pertinent de les aider à y avoir accès.',
        specific:
          'Par exemple, {percentage}% des participant·e·s à qui le mode {mode} est recommandé sont actuellement équipés pour suivre cette recommandation.',
        hover_hint: 'Passez la souris sur les cellules pour plus de détails',
      },
    },
  },
  transportation_modes: {
    ...transportationModes,
  },
  record: {
    reco: 'Mode de transport recommandé : {mode}',
    isochrones: 'Isochrones',
    isochrones_hint: 'Temps de trajet avec le mode de transport recommandé.',
    map_options: 'Options de la carte',
    modes: 'Modes de transport',
    transit: 'Transports publics',
    transit_options: {
      show_lines: "Afficher les lignes de transports publics passant par l'isochrone",
    },
    pois: "Points d'intérêt",
    mode: {
      ...transportationModes,
    },
    categories: {
      food: 'Nourriture',
      education: 'Éducation',
      service: 'Service',
      health: 'Santé',
      leisure: 'Loisirs',
      transport: 'Transports',
      commerce: 'Commerce',
    },
    minutes: '{count} min',
    raw_data: 'Données enregistrées',
    data: 'Données collectées',
    typo: 'Données de typologie modale',
    typo_reco: 'Recommandations',
    typo_reco_pro: 'Recommandations (professionnel)',
    typo_reco_actions: 'Actions recommandées',
    typo_reco_pro_actions: 'Actions recommandées (professionnel)',
  },
  draw_mode: {
    simple_select_hint:
      'Cliquez sur le bouton polygone en haut à droite de la carte pour commencer à dessiner une zone. Les zones existantes seront supprimées.',
    direct_select_hint:
      'Vous êtes en train de modifier le polygone. Faites glisser les points pour ajuster la forme.',
    draw_polygon_hint:
      'Cliquez sur la carte pour ajouter des points à votre polygone. Double-cliquez pour terminer le dessin.',
    zoom_hint: 'Pour zoomer, utilisez la molette de la souris',
  },
  map_filter: {
    workplaces: {
      title: 'Filtre des lieux de travail',
      hint: 'Dessinez une zone pour ne filtrer que les lieux de travail situés dans cette zone.',
    },
  },
  data_protection_notice: {
    title: 'Notice sur la protection des données',
    content: `Le rapport que nous allons vous transmettre dans le cadre de la campagne lancée via l’outil mobilyse contient des données agrégées, résultant des réponses fournies de manière volontaire et anonyme par vos collaborateur·trice·s.

Cependant, en fonction de la taille de votre organisation et de la structure des réponses, il n’est pas exclu que certaines données agrégées permettent, directement ou indirectement, d’identifier une ou plusieurs personnes.
Dans ce cas, le rapport pourrait contenir des données personnelles, soumises à la législation applicable en matière de protection des données (telle que la Loi fédérale sur la protection des données, ou le RGPD si des participant·e·s sont établi·e·s dans l’UE).

En acceptant de recevoir ce rapport, vous vous engagez à le traiter dans le respect de ces dispositions légales, notamment en garantissant la confidentialité des données et en évitant toute utilisation permettant l’identification individuelle d’une collaboratrice ou d'un collaborateur sans base légale valable.

Par ailleurs, nous vous recommandons d’adapter votre registre du traitement en conséquence.

*Dernière mise à jour : mars 2026*`,
  },
  error: {
    accept_terms_and_conditions: 'Vous devez accepter les termes et conditions.',
    registration_failed: "L'inscription a échoué. Veuillez réessayer plus tard.",
    password_complexity_not_met: 'Le mot de passe ne répond pas aux exigences de complexité.',
    invalid_email: 'Une adresse email valide est requise.',
    form_invalid: 'Certains champs sont invalides.',
    loading_company:
      "Erreur lors du chargement de l'organisation. Il se peut qu'elle n'existe pas ou que vous n'y ayez pas accès.",
    loading_record:
      "Erreur lors du chargement de l'enregistrement. Il peut ne pas exister ou vous n'y avez pas accès.",
    pdf_export_failed: "Erreur lors de l'exportation du PDF. Veuillez réessayer plus tard.",
    no_charts_to_export: 'Aucun graphique à exporter en PDF.',
  },
  footer: {
    modus: `[Fondation Modus
Pour une mobilité durable à Genève](https://www.modus-ge.ch)`,
    epfl: `
[Laboratoire de sociologie urbaine (LASUR)](https://www.epfl.ch/labs/lasur/)

[ENAC-IT4R](https://www.epfl.ch/schools/enac/about/data-at-enac/enac-it4research/)`,
  },
  generated_report: {
    title: 'Rapport de mobilité',
    final_page_title: 'Prochaines étapes',
    final_page_subtitle: 'Quelles sont les prochaines étapes de votre stratégie de mobilité ?',

    final_page_body: `1. **Nommer un responsable de la mobilité** pour l'entreprise, souvent appelé « Mobility Manager ».
2. **Identifier tout besoin de soutien**…¹
3. … pour la **mise en œuvre de mesures de mobilité** dans le cadre d'un plan de mobilité.²
4. **Effectuer des revues périodiques** et/ou en fonction des étapes de vie de votre organisation afin de mesurer les changements dans les pratiques de mobilité des employés et, par conséquent, l'impact des mesures de soutien. De cette manière, en adéquation avec l'accessibilité, les modes de transport et les évolutions sociétales, les mesures de mobilité que vous proposez peuvent évoluer pour rester pertinentes.

---

¹ **Liste de conseillers spécialisés et informations complémentaires :** Mobility Management Suisse
² **Soutien financier ou ressources :** programmes communaux et cantonaux ([Plan de mobilité - ge.ch](https://www.ge.ch/dossier/plan-mobilite-geneve/mobilite-entreprises/plan-mobilite) ; [SIL - rsGE H 1 21.03 : Règlement sur les plans de mobilité d'entreprise (RPMob)](https://silgeneve.ch/legis/index.aspx)), programmes fédéraux ([Promotion d'initiatives de mobilité durable dans les entreprises](https://www.suisseenergie.ch/encouragement-de-projet/mobilite-durable/?_fumanNewsletterId=329385:cf700aa7d3be4a638e5f29d79d3998b5), etc.`,
  },
  action: 'Mesure',
  add: 'Ajouter',
  address_input_hint: "Tapez Entrée pour rechercher l'adresse.",
  address: 'Adresse',
  administration: 'Administration',
  administrator: 'Administrateur·trice',
  all: 'Tous',
  campaigns: 'Campagnes',
  comments: 'Commentaires',
  completed: 'Complétés',
  download: 'Télécharger',
  records: 'Enregistrements',
  no_records: "Pas d'enregistrements",
  records_not_super_admin:
    'Seuls les super administrateurs peuvent voir les enregistrements directement sur Mobilyse. Cependant, ils sont toujours disponibles pour téléchargement sur le bouton ci-dessus',
  close: 'Fermer',
  cancel: 'Annuler',
  companies: 'Organisations',
  company_campaign: 'Organisation (campagne)',
  company_removed: 'Organisation supprimée',
  campaign_removed: 'Campagne supprimée',
  content: 'Contenu',
  doc: 'Documentation',
  dashboard: 'Tableau de bord',
  data: 'Données',
  download_csv: 'Télécharger CSV',
  overview: 'Vue d’ensemble',
  participation_following: 'Suivi de participation',
  view: 'Voir',
  edit: 'Editer',
  email: 'Email',
  enabled: 'Activé',
  end_date: 'Date de fin',
  error_not_found: 'Oops. Rien ici...',
  field_required: 'Ce champ est requis',
  first_name: 'Prénom',
  form_version: 'Version du formulaire',
  general: 'Général',
  go_home: 'Accueil',
  group: 'Groupe',
  help: 'Aide',
  identifier: 'Identifiant',
  welcome: 'Bienvenue !',
  introduction_text: `Bienvenue dans l'interface d'administration de Mobilyse !
Utilisez le menu pour naviguer à travers les différentes sections et gérer les organisations, les campagnes, les utilisateurs, et consulter les statistiques de mobilité. La section Documentation est notamment à votre disposition pour vous renseigner et vous guider sur les différentes fonctionnalités de Mobilyse.`,
  label_en: 'Libellé (EN)',
  label_fr: 'Libellé (FR)',
  last_modified: 'Dernière modification',
  last_name: 'Nom',
  legal_notice: 'Mentions légales',
  link_copied:
    'Lien copié dans le presse-papiers, vous pouvez maintenant le partager avec le participant',
  location: 'Localisation',
  location_required: 'Localisation requise, veuillez sélectionner une adresse valide',
  signout: 'Déconnexion',
  signin: 'Connexion',
  signup: 'Inscription',
  name: 'Nom',
  no_results: 'Aucun résultat',
  participants_campaign_hint:
    "Vous pouvez partager le lien vers l'enquête de cette campagne avec les participants. Ce lien reste valide jusqu'à la fermeture de la campagne.",
  participants_individual_hint:
    "Ou vous pouvez assigner individuellement des participants à cette campagne, avec des données individuelles préparées. Chaque participant recevra un jeton unique pour accéder à l'enquête. Une fois l'enquête terminée, le jeton n'est plus valide.",
  participants: 'Participants',
  password_copied: 'Mot de passe copié dans le presse-papiers',
  password_hint:
    'Le mot de passe doit comporter au moins 8 caractères et contenir un mélange de lettres (majuscules et minuscules), de chiffres et de caractères spéciaux.',
  password_temp_hint:
    "Mot de passe temporaire que l'utilisateur·trice mettra à jour lors de la prochaine connexion. Celui-ci doit comporter au moins 8 caractères et contenir un mélange de lettres (majuscules et minuscules), de chiffres et de caractères spéciaux.",
  password: 'Mot de passe',
  recommendations: 'recommandations',
  remove_campaign_text:
    "Êtes-vous sûr de vouloir supprimer la campagne '{name}' et toutes les données personnelles associées des participants?",
  remove_campaign: 'Supprimer la campagne',
  remove_company_text:
    "Êtes-vous sûr de vouloir supprimer l'organisation '{name}' et toutes les campagnes associées et les données personnelles des participants?",
  remove_company: "Supprimer l'organisation",
  remove_participant_text:
    "Êtes-vous sûr de vouloir supprimer le participant '{identifier}' et toutes les données personnelles associées?",
  remove_participant: 'Supprimer le participant',
  remove_record_text: "Êtes-vous sûr de vouloir supprimer l'enregistrement '{token}'?",
  remove_record: "Supprimer l'enregistrement",
  remove_user_text: "Êtes-vous sûr de vouloir supprimer l'utilisateur·trice '{name}'?",
  remove_user: "Supprimer l'utilisateur·trice",
  remove: 'Supprimer',
  report: 'Rapport',
  report_global: 'Rapport global',
  report_campaign: 'Rapport de campagne',
  reset_password: 'Réinitialiser le mot de passe',
  roles: 'Rôles',
  select: 'Sélectionner',
  show_less: 'Afficher moins',
  show_more: 'Afficher plus',
  signup_successful: 'Inscription réussie ! Vous pouvez maintenant vous connecter.',
  start_date: 'Date de début',
  status: 'Statut',
  statistics: 'Statistiques',
  survey_link_copied:
    "Lien vers l'enquête copié dans le presse-papiers, vous pouvez maintenant le partager avec les participants",
  survey_link: "Lien vers l'enquête",
  terms_and_conditions: 'Termes et conditions',
  terms_and_conditions_accept: "J'accepte les termes et conditions",
  terms_and_conditions_show: 'Voir les termes et conditions',
  token: 'Jeton',
  upload_csv: 'Téléverser CSV',
  users: 'Utilisateurs',
  valid_email_required: 'Une adresse email valide est requise',
  valid_url_required: 'Une URL valide est requise (commençant par http:// ou https://)',
  your_role: 'Votre rôle est: {role}',
  created_at: 'Ajouté le',
  updated_at: 'Mis à jour le',
  do_not_show_again: 'Ne plus afficher',
  dark_mode: 'Mode sombre',
  ok: 'OK',
  back: 'Retour',
  print: 'Imprimer',
  mobility_statistics: 'Statistiques de mobilité',
  transit_lines: 'Réseau transports publics',
  documentation: 'Documentation',
}
