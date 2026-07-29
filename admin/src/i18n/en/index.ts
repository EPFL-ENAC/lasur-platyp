const transportationModes = {
  // --- Active Mobility ---
  walking: 'Walking',
  walk: 'Walking',
  marche: 'Walking',
  bike: 'Bicycle',
  velo: 'Bicycle',
  ebike: 'Electric bike',
  vae: 'E-bike (Pedelec)',
  cargo: 'Cargo bike',

  // --- Motorcycles & Small Motorized ---
  moto: 'Motorcycle / scooter',
  elec_moto: 'Electric motorcycle / scooter',

  // --- Public Transport ---
  pub: 'Urban public transport',
  pub_train: 'Public transport (including train)',
  tpu: 'Public transport',
  transit: 'Public transport',
  bus: 'Bus',
  train: 'Train',
  rail: 'Train',

  // --- Private Motorized Vehicles (Cars) ---
  car: 'Car',
  car_driver: 'Car (as driver)',
  car_passenger: 'Car (as passenger)',
  car_moto: 'Car or motorcycle',
  elec: 'Electric vehicle',
  ev: 'Electric vehicle',
  carpool: 'Carpooling',
  covoit: 'Carpooling',

  // --- Long Distance / Heavy Transport ---
  truck: 'Truck',
  elec_truck: 'Electric truck / van',
  plane: 'Plane',
  boat: 'Boat',

  // --- Intermodal ---
  inter_ma_tp: 'Active mobility + Public transport',
  inter_tim_tp: 'Individual motorized transport + Public transport',

  // --- Alternative & Abstract ---
  avoid: 'Avoid travel',
  inter: 'Intermodality',
  combined: 'Combined',
  other: 'Other',
  unknown: 'Unknown',
}

const simpleLabels = {
  MA: 'Active mobility',
  TP: 'Public transport',
  'MA+TP': 'Active mobility + Public transport',
  'MA+TIM': 'Active mobility + Individual motorized transport',
  'TIM+TP': 'Individual motorized transport + Public transport',
  TIM: 'Individual motorized transport',
}

const complexLabels = {
  walking: 'Walking',
  bike: 'Bicycle',
  ebike: 'Electric bike',
  pub: 'Urban public transport',
  train: 'Train',
  moto: 'Motorcycle / scooter',
  car: 'Car',
  carpool: 'Carpooling',
  other: 'Other',
  'pub+bike': 'Public transport + Bicycle',
  'bike+pub': 'Bicycle + Public transport',
  'pub+car': 'Public transport + Car',
  'car+pub': 'Car + Public transport',
  'car+bike': 'Car + Bicycle',
  'bike+car': 'Bicycle + Car',
  'pub+walk': 'Public transport + Walking',
  'walk+pub': 'Walking + Public transport',
  other_inter: 'Other (Intermodal)',
}

const emissionsLabels = {
  emissions: 'Total CO₂ emissions',
  journeys: 'Number of journeys',
  distances: 'Total distance',
  current: 'Current',
  postSaving: 'Total after recommendations',
}

export default {
  main: {
    brand: 'Mobilyse',
  },
  company: {
    label: 'Organisation',
    actions: 'Employer measures',
    employer_measures_description:
      'This section allows you to add, if necessary, any custom metrics set up by your organisation. When creating or editing a campaign, these will be added to the default metrics that are suggested to you.',
    custom_actions: 'Custom measures',
    custom_actions_hint:
      'Add or remove custom employer measures that will facilitate employees mobility. These measures are grouped per transport mode or are global.',
    administrators: 'Administrators',
    administrators_hint:
      'Provide the email address of the administrators for this organisation (type Enter to add entry).',
    mobility_advisors: 'Mobility Advisors',
    mobility_advisors_hint:
      'Provide the email address of the mobility advisors for this organisation (type Enter to add entry).',
    contact_name: 'Contact Name',
    contact_name_hint: 'Provide the name of the contact person for mobility in this organisation.',
    contact_email: 'Contact Email',
    contact_email_hint:
      'Provide the email address of the contact person for mobility in this organisation.',
    contact_info: 'Contact Information',
    info_url: 'Information link',
    info_url_hint: 'Provide a link to more information about the organisation mobility options.',
    can_be_cited: 'Can be cited as a mobilyse user',
    can_be_cited_toggle:
      'I do not want the Modus Foundation to cite the name of my organisation as a user of mobilyse',
    your_role: 'Your role',
    roles: {
      admin: 'Administrator',
      mobility_advisor: 'Mobility Advisor',
      none: 'None',
    },
  },
  campaign: {
    label: 'Campaign',
    slug: 'Identifier',
    slug_hint:
      'Unique identifier for the campaign URL (e.g., "spring-2024-mobility-survey"). Only letters, numbers, hyphens and underscores are allowed.',
    description: 'Description',
    with_professional_questions: 'Include questions about professional travel',
    with_professional_questions_hint:
      'By default, we give you the option to analyse employees’ commutes and business travel. If you are not interested in the latter option (business travel), you can remove this section from the questionnaire with this button.',
    with_actions: 'With employer measures specific to this campaign',
    employer_measures_hint:
      'Here you can specify the measures already in place to support your employees’ mobility. The measures listed here are a selection of "default" measures, as well as the "specific measures" entered in the previous section, "Employer Measures".',
    rewards: {
      toggle: 'I want to reward participants.',
      hint: 'Rewarding employees who respond to the questionnaire (either systematically or via a draw / lottery) helps to achieve a higher response rate. If you wish to reward participants, mobilyse can provide a "certificate" (PDF document) at the end of the questionnaire completion for each respondent, which will prove their participation. The respondent can then forward this certificate to the person in charge of organizing the rewards. We suggest that you customize the message that will be displayed on this certificate, explaining the procedure to follow (who to forward this proof to, how to claim their reward, what are the terms of the lottery...).',
      default_message:
        'Congratulations and thank you for your participation in the mobilyse survey! Your responses are valuable and will help us better understand how to assist you with your daily mobility. By downloading this document and forwarding it to [...], you will be able get [...] as a reward.',
      message_placeholder: 'Message for participants',
    },
    contact_name: 'Contact Name',
    contact_name_hint:
      'Provide the name of the contact person for mobility in this organisation (if different from the organisation contact).',
    contact_email: 'Contact Email',
    contact_email_hint:
      'Provide the email address of the contact person for mobility in this organisation (if different from the organisation contact).',
    contact_info: 'Contact Information',
    info_url: 'Information link',
    info_url_hint:
      'Provide a link to more information about the organisation mobility options (if different from the organisation information link).',
    nb_employees: 'Number of employees',
    nb_employees_hint:
      'Provide the number of employees working in this organisation or at the workplace(s) associated with this campaign. This information is used to contextualize the mobility statistics.',
    csv_missing_columns:
      'The uploaded CSV file is missing the following required columns: {columns}.',
    import_workplaces_hint:
      'Upload a CSV file to add/update multiple workplaces to the campaign at once. The file must contain the following columns: name, address, lat, lon.',
    workplaces: {
      title: 'Workplaces',
      number: 'Number of workplaces',
      hint: 'Declare the workplaces associated with this campaign: either workplaces can be declared by the participant or at least one is required.',
      name: 'Name',
      name_hint: 'Name of the workplace (e.g., "Logistic Hub 12").',
      required: 'At least one workplace must be defined for the campaign.',
      open_workplaces: 'Open workplaces',
      open_workplaces_hint:
        'If enabled, participants will be able to select any workplace when filling the survey.',
      workplaces_list: 'List of known workplaces',
      show_isochrone: 'Show isochrone',
      isochrones_hint:
        'An isochrone map shows the areas that can be reached from a starting point using specific modes of transport within a given time. In this case, the isochrone map illustrates which parts of the region are accessible via different modes of transport from a workplace, allowing you to see, in particular, how far employees can travel from that location.',
    },
    email_template: {
      buttonText: 'Email template',
      modalTitle: 'Email template for {campaign}',
      contactEmail: 'Contact email',
      contactName: 'Contact name',
      surveyLink: 'Survey link',
      defaultContactEmail: 'CONTACT_EMAIL',
      defaultContactName: 'CONTACT_NAME',
      template: `Dear colleagues,

Mobilyse is a tool developed by the Modus Foundation and EPFL to help organisations tailor the help they provide to their employees for daily mobility. We wish to use this tool to understand how best to support you in your daily mobility, whether for commuting or for business trips. 🚲🚃🚶🚈 To do so, we need to better understand your travel habits and aspirations and therefore invite you to participate in the following survey. It will take no more than 10 minutes and will provide you with travel suggestions straight away:

[{surveyLink}]({surveyLink})

Why take part?

- Receive travel recommendations tailored to your situation (available transport services, distances, constraints, your opinion on modes of transport, your priorities, etc.) ✅
- Find out about the mobility support measures your organisation provides for encouraging sustainable mobility 🎯
- Share your opinion on the support provided for your mobility, and help improve it 🙋
- Contribute to improving a free, open-access tool 🎁

The survey is anonymous and no personal data will be recorded. 🔐 Please note that you can select the language (FR/EN) in the top right-hand corner. To find out more about mobilyse, please visit: https://modus-ge.ch/project/mobilyse/.

Thank you for your valuable contribution! If you have any questions, please contact: [{contactEmail}](mailto:{contactEmail}).

{contactName}`,
      copyTemplate: 'Copy email template',
      copyTemplateSuccess: 'Email template copied to clipboard',
      copyTemplateError: 'Error copying email template. Please try again.',
    },
  },
  docs: {
    title: 'Documentation',
    hint: 'Find here all the documentation to help you use Mobilyse administration interface.',
    general: {
      title: 'General',
      privacy: {
        title: 'Privacy and data protection',
        caption: 'Learn about how Mobilyse handles data and ensures the privacy of participants',
      },
      terms: {
        title: 'Terms of use',
        caption:
          'Learn about the terms of use for Mobilyse and your responsibilities as an administrator',
      },
      what_next: {
        title: 'What to do next?',
        caption:
          'Learn about the next steps to take after setting up your organisation and campaign',
      },
      need_more_help: {
        title: 'Need more help?',
        caption: 'Contact us for any questions or support regarding campaign management',
      },
    },
    organisations: {
      title: 'Organisations',
      create: {
        title: 'How to create an organisation?',
        caption: 'Learn how to create a new organisation in Mobilyse',
      },
      settings: {
        title: 'How to manage organisation settings?',
        caption: 'Learn how to update your organisation settings and preferences',
      },
      employer_measures: {
        title: 'How to manage employer measures?',
        caption: 'Learn how to manage employer measures for your organisation',
      },
      custom_measures: {
        title: 'How to manage custom measures?',
        caption: 'Learn how to manage custom measures for your organisation',
      },
      best_practices: {
        title: 'Best practices for using Mobilyse',
        caption: 'Tips and recommendations to make the most of Mobilyse for your organisation',
      },
      common_issues: {
        title: 'Common issues and troubleshooting',
        caption: 'Solutions to frequently encountered problems',
      },
      mobility_advisor: {
        title: 'How to use the mobility advisor?',
        caption: 'Learn how to use the mobility advisor to support your organisation',
      },
    },
    campaigns: {
      title: 'Campaigns',
      description:
        'Campaigns are time-bound mobility surveys or initiatives within an organisation. Each organisation can have multiple campaigns.',
      settings: {
        title: 'How to manage campaign settings?',
        caption: 'Learn how to create and update your campaign settings and preferences',
      },
      share_link: {
        title: 'How to share the link to the survey?',
        caption: 'Learn how to share the link to the survey with collaborators',
      },
      isochrone: {
        title: 'How and why to display the isochrone on the map?',
        caption: 'Learn how and why to display the isochrone on the map',
      },
      reward: {
        title: 'How to reward participants who have completed the survey?',
        caption: 'Learn how to reward participants who have completed the survey',
      },
      common_issues: {
        title: 'Common issues and troubleshooting',
        caption: 'Solutions to frequently encountered problems related to campaign management',
      },
      best_practices: {
        title: 'Best practices for campaign management',
        caption: 'Tips and recommendations to make the most of the campaign features in Mobilyse',
      },
      dashboard: {
        title: 'How to use the campaign dashboard?',
        caption:
          'Learn how to use the campaign dashboard to monitor the progress of your campaign and access key statistics',
      },
    },
  },
  role: {
    'platyp-user': 'User',
    'platyp-admin': 'Administrator',
  },
  participant: {
    identifier: 'Identifier',
    age_class: 'Age Class',
    employment_rate: 'Employment Rate',
    remote_work_rate: 'Remote Work Rate',
    company_vehicle: 'Company Vehicle',
    status: {
      open: 'Open',
      completed: 'Completed',
    },
  },
  actions: {
    personnal: 'Personal',
    professional: 'Professional',
    mesures_globa_label: 'Global',
    mesures_globa_hint: '',
    mesures_tpu_label: 'Public transports',
    mesures_tpu_hint: '',
    mesures_train_label: 'Train',
    mesures_train_hint: '',
    mesures_inter_label: 'Inter-modality',
    mesures_inter_hint: '',
    mesures_velo_label: 'Bicycle',
    mesures_velo_hint: '',
    mesures_covoit_label: 'Care pooling',
    mesures_covoit_hint: '',
    mesures_elec_label: 'Electric',
    mesures_elec_hint: '',
    mesures_pro_globa_label: 'Global',
    mesures_pro_globa_hint: '',
    mesures_pro_velo_label: 'Bicycle',
    mesures_pro_velo_hint: '',
    mesures_pro_tpu_label: 'Public transports',
    mesures_pro_tpu_hint: '',
    mesures_pro_train_label: 'Train',
    mesures_pro_train_hint: '',
    mesures_pro_elec_label: 'Electric',
    mesures_pro_elec_hint: '',
    budget: 'Sustainable mobility budget',
    wfh: 'Ability to work from home',
    wftp: 'Ability to work remotely',
    wfro: 'Ability to work remotely occasionally',
    videoconf:
      'Workplace videoconferencing system that can be booked to reduce long-distance travel',
    tpg_pass: 'Public transport (UNIRESO) pass',
    lex_pass: 'Léman express pass',
    cff_pass_ag: 'Train pass (general pass)',
    cff_pass_dtp: 'Train pass (1/2 fare plus)',
    cff_pass_dt: 'Train pass (1/2 fare)',
    pnr_pass: 'Park and Ride pass',
    shuttle: 'Shuttle from the enarest train station',
    velo_station: 'Velo-station pass',
    bike_subs: 'Subsidy for the purchase of a bicycle/e-bike',
    shower: 'Showers, lockers and changing rooms',
    bike_parking: 'Secure bicycle parking',
    ebike_charging: 'E-bike battery charging',
    bike_equipment: 'Subsidy for the purchase of bicycle safety and comfort gear',
    bike_courses: 'Setting up cycling courses at the workplace',
    carpool_subs: 'Reimbursement of car-pooling journeys',
    carpool_connect: 'Connection to nearby colleagues to facilitate car-pooling',
    carpool_parking: 'Parking spots reserved for car-pooling',
    ev_charging: 'EV charging at the workplace',
    mobility_pass: 'Mobility car-pooling pass',
    ebike_fleet: 'E-bike fleet for professional trips',
    tpu_pro: 'Public transport (UNIRESO) pass',
    tpu_rmb: 'Reimbursement of public transport tickets for business travel',
    train_pro: 'Train pass (general pass)',
    train_obl: 'Obligation to use train where possible, for business journeys',
    train_rmb: 'Reimbursement of train tickets for business travel',
    ev_fleet: 'EV fleet for professional trips',
  },
  stats: {
    title: 'Mobility report',
    no_charts_to_export: 'No charts to export as PDF.',
    charts_height: 'Charts height',
    records_count: 'Records count',
    in_progress: 'In Progress',
    completed: 'Completed',
    pending: 'Pending',
    filter_by_zone: 'Filter by zone',
    switch_to_grid: 'Switch to grid view',
    pdf_report: 'PDF report',
    nb_employees: 'Number of employees',
    percent_employees: '% of employees',
    total: 'N: {count}',
    no_data: 'No data available',
    observed: 'Data from participants',
    participants_median: 'Participants median',
    geneva_median: 'Geneva area median',
    reference_data: 'Reference data (Geneva canton)',
    units: {
      tco2eq_per_year: 'tCO₂eq/year',
    },
    sections: {
      mobility_analysis: {
        title: 'Mobility analysis',
        description: `The graphs below provide information on participants’ current mobility habits, including their use of transport modes, the equipment they possess, the constraints they face, and their geographical distribution.`,
        details: `Some environmental impacts have also been calculated:
- on the environment, via greenhouse gas emissions calculated using mobi-tools factors [(source)](https://www.i14y.admin.ch/fr/catalog/dataservices/171b09a4-5b5f-4577-8921-3af7fc6eee39/description)
- on participants’ health, via average daily energy expenditure (metabolic equivalent task) during their trips. The Swiss Confederation and the WHO recommend 150 minutes of moderate-intensity exercise (cycling/brisk walking) per week, equivalent to 150 kcal per day. [(source)](https://www.who.int/fr/news-room/fact-sheets/detail/physical-activity) A lack of physical activity has a direct impact on physical and mental health (psychological and cognitive), and thus directly affects employees’ well-being, sick leave rates, productivity and the working atmosphere.`,
      },
      mobility_potentials: {
        title: 'Mobility potentials',
        description: `This section presents the personalized recommendations suggested to participants. Mobilyse indicates which modes are most likely to suit employees based on their habits, constraints, preferences, residential and work location… Some graphs also illustrate the potential gains in terms of impact on greenhouse gas emissions and health, in the event that all participants adopt the recommendations formulated by mobilyse.`,
        insights: {
          most_potential:
            'The mode with the highest potential for users is: **{mode}** (recommended to **{percentage}%** of respondents)',
          biggest_emission_reduction:
            'The mode of transport that would generate the greatest reduction in CO2 emissions is: **{mode}**, with a reduction of **{reduction} {unit}**, i.e. **{percentage}%** of the total potential gain for responding employees.',
          biggest_emission_reduction_extrapolation:
            'Extrapolating to the **{collaborators_count}** employees in your organization, this reduction is estimated at **{reduction} {unit}** per year.',
          biggest_physical_activity_gain:
            "The mode of transport that most increases employees' physical activity is: **{mode}**. This scenario enables **{collaborators_count}** additional employees to reach the WHO-recommended daily level of physical expenditure (150 kcal/day/person).",
        },
      },
      behavioural_changes: {
        title: 'Encouraging behavioural changes',
        description: `This final section provides information on participants’ willingness to follow the recommendations made to them, and on their needs or desires in order to bring about these behavioural changes. This can help guide your decisions and identify the mobility aids you might consider.`,
      },
      home_to_work: 'Home-to-work commute',
      professional_travel: 'Professional travel',
    },
    equipments: {
      title: 'Mobility equipments',
      labels: {
        bike: 'Bicycle',
        upt_subs: 'Urban public transport\nsubscription',
        train_subs: 'Train subscription',
        car_driver: 'Car (as driver)',
        moto: 'Motorcycle/scooter/moped',
        ebike: 'Electric bicycle',
        mob_subs: 'Shared mobility subscription',
        car_passenger: 'Car (as passenger)',
        car: 'Car (driver/passenger)',
        ev: 'Electric vehicle',
      },
      mrmt_source:
        'Reference data, Geneva canton [Microcensus of Mobility and Transportation, 2023](https://statistique.ge.ch/tel/publications/2023/analyses/communications/an-cs-2023-71.pdf)',
    },
    constraints: {
      title: 'Mobility constraints',
      labels: {
        dependent: 'Accompanying children\nor dependent persons',
        heavy: 'Transporting heavy/bulky\nequipment',
        night: 'Night work',
        disabled: 'Parking card for people\nwith reduced mobility',
        other: 'Other *',
        none: 'No constraint',
      },
      texts: {
        other: 'Other constraints are available in detail if you download the whole dataset.',
      },
    },
    locations_heatmap: {
      title: 'Geographical distribution of home and workplace locations',
      households: 'Households',
      households_number: 'Number of households',
      workplaces: 'Workplaces',
    },
    travel_time: {
      title: 'Travel time',
      xaxis: 'Time (min)',
      texts: {
        default:
          'The median travel time from home to work in the Geneva canton is 30 minutes (Modus survey, 2024)',
        specific: 'The median travel time from home to work for participants is {median} minutes.',
      },
    },
    reco_inter: {
      title: 'Potential modal split',
      labels: {
        ...transportationModes,
      },
    },
    reco_pros: {
      title: 'Recommendations (professional)',
      labels: {
        ...transportationModes,
      },
    },
    freq_mod: {
      title: 'Modal split',
      title_simple: 'Modal split (simple)',
      title_detailed: 'Modal split (detailed)',
      title_mrmt: 'Reference data (Geneva canton)',
      labels: {
        ...transportationModes,
      },
      modal_split: {
        simple: 'Simple',
        detailed: 'Detailed',
      },
      texts: {
        default:
          'The mode Car is the most used in the Geneva canton ([Microrecensement Mobilité et Transports, 2015](https://statistique.ge.ch/tel/publications/2023/analyses/communications/an-cs-2023-71.pdf)).',
        specific:
          'The mode {top_1} is the most used by participants, followed by {top_2} and {top_3}.',
      },
    },
    freq_mod_pro: {
      title: 'Modal split (professional travel)',
      xaxis: 'Journeys per year',
      labels: {
        ...transportationModes,
        local: 'Local',
        region: 'Regional',
        national: 'National',
        europe: 'European',
        inter: 'International',
      },
    },
    emissions_freq_mod: {
      title: 'CO₂ emissions per transport mode',
      yaxis: 'CO₂ emissions per journey (kgCO₂eq)',
      xaxis: 'Journeys per year',
      labels: {
        ...transportationModes,
        ...emissionsLabels,
      },
      texts: {
        specific:
          "{carMotoJourneysPercentage}% of journeys by respondents are made in a car/motorcycle/scooter, representing {carMotoEmissionsPercentage}% of the company's annual CO₂ emissions.",
      },
    },
    emissions_freq_mod_simple: {
      title: 'CO₂ emissions (simple)',
      yaxis: 'CO₂ emissions per journey (kgCO₂eq)',
      xaxis: 'Journeys per year',
      labels: {
        ...simpleLabels,
        ...emissionsLabels,
      },
    },
    emissions_freq_mod_complex: {
      title: 'CO₂ emissions (detailed)',
      yaxis: 'CO₂ emissions per journey (kgCO₂eq)',
      xaxis: 'Journeys per year',
      labels: {
        ...complexLabels,
        ...emissionsLabels,
      },
    },
    emissions_reductions_mod: {
      title: 'Potential reductions in commuting emissions',
      series: 'Potential reduction',
      yaxis: 'Avoided CO₂ emissions (kgCO₂eq)',
      xaxis: 'Recommended mode',
      labels: {
        ...transportationModes,
        ...emissionsLabels,
      },
      texts: {
        default:
          'This chart shows the reduction in CO₂ emissions allocated to each recommendation, in the case where employees follow these recommendations: this is the potential gain in terms of emissions.',
        specific:
          'The recommendations would allow transitioning from {current_emissions} to {new_emissions} {unit} / year for participants who responded. This corresponds to {cheeseburgers} cheeseburgers, or alternatively to the production of {vacuum} vacuum cleaners or {shirt} cotton shirts [source : [https://impactco2.fr/doc](https://impactco2.fr/doc)].',
      },
    },
    emissions_reductions_mod_simple: {
      title: 'Potential reductions in commuting emissions (simple)',
      series: 'Potential reduction',
      yaxis: 'Avoided CO₂ emissions (kgCO₂eq)',
      xaxis: 'Current simple label',
      labels: {
        ...emissionsLabels,
      },
      texts: {
        default:
          'This chart shows the reduction in CO₂ emissions allocated to each current simple label, in the case where the respondents currently in that group follow their recommendation: this is the potential gain in terms of emissions.',
        specific:
          'The recommendations would allow transitioning from {current_emissions} to {new_emissions} {unit} / year for participants who responded. This corresponds to {cheeseburgers} cheeseburgers, or alternatively to the production of {vacuum} vacuum cleaners or {shirt} cotton shirts [source : [https://impactco2.fr/doc](https://impactco2.fr/doc)].',
      },
    },
    emissions_reductions_mod_complex: {
      title: 'Potential reductions in commuting emissions (detailed)',
      series: 'Potential reduction',
      yaxis: 'Avoided CO₂ emissions (kgCO₂eq)',
      xaxis: 'Current detailed label',
      labels: {
        ...emissionsLabels,
      },
      texts: {
        default:
          'This chart shows the reduction in CO₂ emissions allocated to each current detailed label, in the case where the respondents currently in that group follow their recommendation: this is the potential gain in terms of emissions.',
        specific:
          'The recommendations would allow transitioning from {current_emissions} to {new_emissions} {unit} / year for participants who responded. This corresponds to {cheeseburgers} cheeseburgers, or alternatively to the production of {vacuum} vacuum cleaners or {shirt} cotton shirts [source : [https://impactco2.fr/doc](https://impactco2.fr/doc)].',
      },
    },
    emissions_reductions_share: {
      title: 'Distribution of emissions reductions by transport mode',
      series: 'Potential reduction',
      labels: {
        ...transportationModes,
        ...emissionsLabels,
      },
      texts: {
        default:
          'This chart shows the share of CO₂ emissions reduction per recommended mode of transport.',
        specific:
          '{percentage}% of potential reduction depend on the main recommendation for mode {mode}.',
      },
    },
    emissions_reductions_share_simple: {
      title: 'Distribution of emissions reductions (simple)',
      series: 'Potential reduction',
      labels: {
        ...simpleLabels,
        ...emissionsLabels,
      },
      texts: {
        default: 'This chart shows the share of CO₂ emissions reduction per current simple label.',
        specific:
          '{percentage}% of potential reduction depend on journeys currently labeled {mode}.',
      },
    },
    emissions_reductions_share_complex: {
      title: 'Distribution of emissions reductions (detailed)',
      series: 'Potential reduction',
      labels: {
        ...complexLabels,
        ...emissionsLabels,
      },
      texts: {
        default:
          'This chart shows the share of CO₂ emissions reduction per current detailed label.',
        specific:
          '{percentage}% of potential reduction depend on journeys currently labeled {mode}.',
      },
    },
    emissions_freq_mod_pro: {
      title: 'CO₂ emissions per transport mode (professional travel)',
      yaxis: 'CO₂ emissions per journey (kgCO₂eq)',
      xaxis: 'Journeys per year',
      labels: {
        ...transportationModes,
        ...emissionsLabels,
      },
      texts: {
        specific:
          '{firstPercent}% of emissions are due to {firstMode}, {secondPercent}% to the {secondMode}. Each journey in {firstMode} emits on average {firstEmissions}kgCO₂eq / journey, against less than {remainingEmissions}kgCO₂eq / journey for the others.',
      },
    },
    emissions_reductions_mod_pro: {
      title: 'Potential reductions in professional travel emissions',
      series: 'Potential reduction',
      yaxis: 'Avoided CO₂ emissions (kgCO₂eq)',
      xaxis: 'Recommended mode',
      labels: {
        ...emissionsLabels,
      },
      texts: {
        default:
          'This chart shows the reduction in CO₂ emissions allocated to each recommendation, in the case where employees follow these recommendations: this is the potential gain in terms of emissions.',
        specific:
          'The recommendations would allow transitioning from {current_emissions} to {new_emissions} {unit} / year for participants who responded. This corresponds to building {laptop} laptops, or alternatively to sending {email_sent} emails or {visio_hour} hours of video conferencing [source : [https://impactco2.fr/doc](https://impactco2.fr/doc)].',
      },
    },
    mod_reco: {
      title: 'Modal shift recommendations',
      texts: {
        default:
          'This chart shows which modes of transport have been recommended (on the right) based on the mode currently in use (on the left).',
        specific:
          'The mode "{mode}" appears to be the mode of transport with the highest potential for modal shift.',
      },
    },
    mod_reco_pro: {
      title: 'Modal shift recommendations (professional)',
      texts: {
        default:
          'This chart shows which modes of transport have been recommended (on the right) based on the mode currently in use (on the left).',
        specific:
          'The mode "{mode}" appears to be the mode of transport with the highest potential for modal shift.',
      },
    },
    energy_journey: {
      title_current: 'Average daily energy expenditure during travel',
      title_reco: 'Potential Physical Activity Diagram following Recommendations',
      title_share: 'Transport modes with highest potential energy gains',
      yaxis: 'Energy expenditure (kcal)',
      xaxis: 'Participants (sorted by energy expenditure)',
      whoMin: 'WHO minimum recommended physical activity',
      participantsAverage: 'Average physical activity expenditure of participants',
      texts: {
        default:
          'The WHO recommends engaging in moderate-intensity physical activity (such as walking or cycling) burning approximately 150 kcal/day/person, equivalent to 37 minutes of walking, 23 minutes of fitness, or 14 minutes of football per day.',
        specific_current:
          'Currently, participants spend an average of {energy} kcal/day/person on their home-work travel.',
        specific_reco: `If the recommendations are followed, the average energy expenditure will increase by {added_energy} kcal/day/person (equivalent to {yoga_min} minutes of yoga per person per day).
          In addition, an additional {count} people will exceed the WHO’s daily physical activity recommendations. The proportion of participants who meet at least the WHO’s recommendations through their commute is expected to rise from around {percent_current}% to potentially around {percent_potential}%.`,
        default_share:
          'This chart shows which modes of transport have the most potential for increased physical activity.',
        specific_share:
          '{percentage}% of the improvement in physical activity among participants would come from {mode}.',
      },
    },
    behavior_change_levers: {
      title: 'Support measures requested to adopt mobility recommendations',
      labels: {
        finance: 'Financial incentives',
        test: 'Test periods',
        coaching: 'Individual coaching',
        events: 'Mobility events',
        flexibility: 'Flexibility',
        collective: 'Collective measures',
        environment: 'Workplace adjustments and amenities',
        company_vehicle: 'Company vehicle',
        autres: 'Other',
        total: 'Total',

        ...transportationModes,
        allModes: 'All modes',
      },
      texts: {
        info: 'The modes displayed are those that have been recommended to sufficiently many people who have answered this question.',
        default:
          'This chart helps to understand how participants would like to be supported in evolving their mobility.',
        specific: 'The support that participants feel they need most is {lever}.',
      },
    },
    behavior_change_motivation: {
      title: 'Willingness to adopt recommendations',
      labels: {
        l1: 'Not interested',
        l2: 'Rather not motivated',
        l3: 'Neutral',
        l4: 'Rather motivated',
        l5: 'Very motivated',

        ...transportationModes,
        allModes: 'All modes',
        autres: 'Other',
        total: 'Total',
      },
      texts: {
        info: 'The modes displayed are those that have been recommended to sufficiently many people who have answered this question.',
        default:
          'This graph shows the motivation of participants to adopt the recommendations made by Mobilyse for their home-work travel.',
        specific:
          'This graph shows the motivation of participants to adopt the recommendations made by Mobilyse for their home-work travel, depending on the recommended mode. Overall, {percentage}% (combined rather motivated and very motivated) of participants are motivated to adopt the recommendations made to them.',
      },
    },
    equipments_by_recommendations: {
      title: 'Equipment by recommendation',
      tooltip: `{count} of the participants who got the recommendation "{reco}" are equipped with "{equipment}". <br />
      This represents {percentage}% of participants who got the recommendation "{reco}".`,
      simpleMode: 'Equipments matching recommendation only',
      labels: {
        ...transportationModes,

        mob_subs: 'Mobility sub.',
        tpu_unireso: 'Unireso',
        tpu_leman_pass: 'Léman Pass',
        train_demi_tarif: 'Half-fare Travelcard',
        train_abo_gen: 'GA Travelcard',
        inter: 'Intermodality',
        tpu: 'Public transport',

        allModes: 'All modes',
      },
      texts: {
        default:
          'This table shows the equipment of participants based on the recommendations made to them. This allows us to understand whether participants already have access to the mode recommended to them, or if it would be pertinent to help them gain access.',
        specific:
          'For example, {percentage}% of participants to whom the {mode} mode is recommended are currently equipped to follow this recommendation.',
        hover_hint: 'Hover over the cells for more details',
      },
    },
  },
  transportation_modes: {
    ...transportationModes,
  },
  simple_labels: {
    ...simpleLabels,
  },
  complex_labels: {
    ...complexLabels,
  },
  record: {
    reco: 'Recommended mode of transport: {mode}',
    isochrones: 'Isochrones',
    isochrones_hint: 'Travel time with the recommended mode of transport.',
    modes: 'Transport modes',
    map_options: 'Map options',
    transit: 'Public transport',
    transit_options: {
      show_lines: 'Show lines passing through the isochrone',
    },
    pois: 'Points of interest',
    mode: {
      ...transportationModes,
    },
    categories: {
      food: 'Food',
      education: 'Education',
      service: 'Service',
      health: 'Health',
      leisure: 'Leisure',
      transport: 'Transport',
      commerce: 'Commerce',
    },
    minutes: '{count} min',
    raw_data: 'Recorded data',
    data: 'Collected data',
    typo: 'Modal typology data',
    typo_reco: 'Recommendations',
    typo_reco_pro: 'Recommendations (professional)',
    typo_reco_actions: 'Recommended actions',
    typo_reco_pro_actions: 'Recommended actions (professional)',
  },
  boundary_select: {
    hint: 'Click an area on the map to filter by it. Click it again to remove the filter.',
    zoom_hint: 'Scroll to zoom in or out',
  },
  map_filter: {
    workplaces: {
      title: 'Workplaces filter',
      hint: 'Select an area to only filter workplaces within that area.',
    },
  },
  data_protection_notice: {
    title: 'Data Protection Notice',
    content: `The report you are about to receive as part of the campaign launched via the Mobilyse tool contains aggregated data derived from responses provided voluntarily and anonymously by your employees.

However, depending on the size of your company and the structure of the responses, it cannot be ruled out that certain aggregated data may, directly or indirectly, allow one or more individuals to be identified.
In this case, the report may contain personal data, which is subject to applicable data protection legislation (such as the Federal Data Protection Act, or the GDPR if employees are based in the EU).

By agreeing to receive this report, you undertake to process it in accordance with these legal provisions, in particular by ensuring the confidentiality of the data and by avoiding any use that would allow the individual identification of an employee without a valid legal basis.

Furthermore, we recommend that you adapt your processing register accordingly.

*Last updated: March 2026*`,
  },
  error: {
    session_expired: 'Your session has expired. Please sign in again.',
    accept_terms_and_conditions: 'You must accept the terms and conditions.',
    registration_failed: 'Registration failed. Please try again later.',
    password_complexity_not_met: 'The password does not meet the complexity requirements.',
    invalid_email: 'A valid email address is required.',
    form_invalid: 'Some fields are invalid.',
    loading_company: 'Error loading company. It may not exist or you do not have access to it.',
    loading_record: 'Error loading record. It may not exist or you do not have access to it.',
    pdf_export_failed: 'Error exporting PDF. Please try again later.',
    no_charts_to_export: 'No charts to export as PDF.',
  },
  footer: {
    modus: `[Fondation Modus
Promoting sustainable mobility in the Greater Geneva](https://www.modus-ge.ch)`,
    epfl: `
[Laboratory Of Urban Sociology (LASUR)](https://www.epfl.ch/labs/lasur/)

[ENAC-IT4R](https://www.epfl.ch/schools/enac/about/data-at-enac/enac-it4research/)`,
  },
  generated_report: {
    title: 'Generated mobility report',
    final_page_title: 'Going forward',
    final_page_subtitle: 'What are the next steps for your mobility strategy?',
    final_page_body: `
1. **Appoint a mobility lead** for the company, often referred to as a "Mobility Manager"
2. **Identify any need for support**…¹
3. … for the **implementation of mobility measures** as part of a mobility plan.²
4. **Review periodically** and/or in line with the life stages of your organisation to measure changes in employees’ mobility practices and thus the impact of the support measures. In this way, in line with accessibility, transport modes and societal changes, the mobility measures you propose can evolve to remain relevant.

---

¹ **List of specialist advisers and further information:** Mobility Management Suisse
² **Financial support or resources:** municipal and cantonal programmes ([Mobility Plan - ge.ch](https://www.ge.ch/dossier/plan-mobilite-geneve/mobilite-entreprises/plan-mobilite); [SIL - rsGE H 1 21.03: Regulations on corporate mobility schemes (RPMob)](https://silgeneve.ch/legis/index.aspx)), federal programmes ([Promoting sustainable mobility initiatives in businesses](https://www.suisseenergie.ch/encouragement-de-projet/mobilite-durable/?_fumanNewsletterId=329385:cf700aa7d3be4a638e5f29d79d3998b5)), etc.`,
  },
  action: 'Measure',
  add: 'Add',
  address_input_hint: 'Type Enter to lookup addresses.',
  address: 'Address',
  administration: 'Administration',
  administrator: 'Administrator',
  all: 'All',
  campaigns: 'Campaigns',
  comments: 'Comments',
  completed: 'Completed',
  download: 'Download',
  records: 'Records',
  no_records: 'No records',
  records_not_super_admin:
    'Only super admins can see records directly on Mobilyse. However, they are still available for download on the button above',
  close: 'Close',
  cancel: 'Cancel',
  companies: 'Companies',
  company_campaign: 'Company (campaign)',
  company_removed: 'Company removed',
  campaign_removed: 'Campaign removed',
  content: 'Content',
  doc: 'Documentation',
  dashboard: 'Dashboard',
  data: 'Data',
  download_csv: 'Download CSV',
  overview: 'Overview',
  participation_following: 'Participation following',
  view: 'View',
  edit: 'Edit',
  email: 'Email',
  enabled: 'Enabled',
  end_date: 'End Date',
  error_not_found: 'Oops. Nothing here...',
  field_required: 'This field is required',
  first_name: 'First Name',
  form_version: 'Form version',
  general: 'General',
  go_home: 'Go Home',
  group: 'Group',
  help: 'Help',
  identifier: 'Identifier',
  welcome: 'Welcome!',
  introduction_text: `Welcome to the Mobilyse administration interface!
Use the menu to navigate through the different sections, manage organisations, campaigns, and users, and review mobility statistics. The Documentation section is also available to inform and guide you through the various features of Mobilyse.`,
  label_en: 'Label (EN)',
  label_fr: 'Label (FR)',
  last_modified: 'Last Modified',
  last_name: 'Last Name',
  legal_notice: 'Legal Notice',
  link_copied: 'Link copied to clipboard, you can now share it with the participant',
  location: 'Location',
  location_required: 'Location is required, make sure address is valid',
  signout: 'Sign-out',
  signin: 'Sign-in',
  signup: 'Sign-up',
  name: 'Name',
  no_results: 'No results',
  participants_campaign_hint:
    'You can share a generic campaign link to the survey with multiple participants. This link stays valid until the campaign is closed.',
  participants_individual_hint:
    'Or you can individually assign participants to this campaign, with some prepared individual data entries. Each participant will receive a unique token to access the survey. Once survey is completed, the token is no longer valid.',
  participants: 'Participants',
  password_copied: 'Password copied to clipboard',
  password_hint:
    'The password must be at least 8 characters long and contain a mix of letters (uppercase and lowercase), numbers, and special characters.',
  password_temp_hint:
    'Temporary password that user will update at the next login. It must be at least 8 characters long and contain a mix of letters (uppercase and lowercase), numbers, and special characters.',
  password: 'Password',
  recommendations: 'Recommendations',
  remove_campaign_text:
    "Are you sure you want to remove the campaign '{name}' and all the associated participants personal data?",
  remove_campaign: 'Remove Campaign',
  remove_company_text:
    "Are you sure you want to remove the company '{name}' and all the associated campaigns and participants personal data?",
  remove_company: 'Remove Company',
  remove_participant_text:
    "Are you sure you want to remove the participant '{identifier}' and all the associated personal data?",
  remove_participant: 'Remove Participant',
  remove_record_text: "Are you sure you want to remove the record '{token}'?",
  remove_record: 'Remove Record',
  remove_user_text: "Are you sure you want to remove the user '{name}'?",
  remove_user: 'Remove User',
  remove: 'Remove',
  report: 'Report',
  report_global: 'Global report',
  report_campaign: 'Campaign report',
  reset_password: 'Reset Password',
  roles: 'Roles',
  select: 'Select',
  show_less: 'Show less',
  show_more: 'Show more',
  signup_successful: 'Signup successful! You can now sign in.',
  start_date: 'Start Date',
  status: 'Status',
  statistics: 'Statistics',
  survey_link_copied: 'Survey link copied to clipboard, you can now share it with the participants',
  survey_link: 'Link to survey',
  terms_and_conditions: 'Terms and Conditions',
  terms_and_conditions_accept: 'I accept the terms and conditions',
  terms_and_conditions_show: 'View terms and conditions',
  token: 'Token',
  upload_csv: 'Upload CSV',
  users: 'Users',
  valid_email_required: 'A valid email address is required',
  valid_url_required: 'A valid URL is required (starting with http:// or https://)',
  your_role: 'Your role is: {role}',
  created_at: 'Created at',
  updated_at: 'Updated at',
  do_not_show_again: 'Do not show again',
  dark_mode: 'Dark mode',
  ok: 'OK',
  back: 'Back',
  print: 'Print',
  mobility_statistics: 'Mobility statistics',
  transit_lines: 'Public transport network',
  documentation: 'Documentation',
  less_details: 'Less details',
  more_details: 'More details',
}
