export default {
  main: {
    brand: 'Mobility Toolkit',
  },
  form: {
    error: {
      origin: 'Please enter a starting point',
      workplace: 'Please enter a work place location',
    },
    age_class: 'What is your age group?',
    age_class_option: {
      '16_24': 'under 25',
      '25_44': '25 - 44',
      '45_64': '45 - 64',
      '65': '65 and over',
    },
    employment_rate: 'What is your employment rate?',
    remote_work_rate: 'What is your remote work rate?',
    company_vehicle: 'Do you have a company vehicle?',
    yes: 'Yes',
    no: 'No',
    workplace: 'Your usual place of work',
    origin: 'Where do you usually leave from to reach your workplace?',
    origin_hint:
      'This confidential information will only be used to calculate your mobility options for your home-work journey.',
    travel_time:
      'What is your average travel time from home to work, with the mode of transport you use most often?',
    travel_time_minutes: 'minutes (one way)',
    constraints: 'What are your possible constraints related to daily mobility?',
    constraints_option: {
      dependent: 'Driving children or dependent persons',
      heavy: 'Transporting heavy/bulky equipment',
      night: 'Night work',
      disabled: 'Parking card for people with reduced mobility',
    },
    equipments: 'Which of the following equipments do you have access to?',
    equipments_option: {
      bike: 'Bicycle',
      upt_subs: 'Urban public transport subscription',
      train_subs: 'Train subscription',
      car_driver: 'Car (as driver)',
      moto: 'Motorcycle/scooter/moped',
      ebike: 'Electric bicycle',
      mob_subs: 'Shared mobility subscription (mobility, etc.)',
      car_passenger: 'Car (as passenger)',
    },
    freq_mod: 'How often do you use the following modes of transportation to get to work?',
    freq_mod_hint: 'Number of days in a usual week',
    mode: {
      walking: 'Walking (>10 min.)',
      bike: 'Bicycle (or electric bike)',
      pub: 'Public transport',
      train: 'Train',
      moto: 'Motorcycle/scooter',
      car: 'Car (driver/passenger)',
      plane: 'Plane',
      pub_train: 'Public transport and train',
      car_moto: 'Car and motorcycle/scooter',
      combined: 'A combination of these modes of transportation',
    },
    trav_pro: 'To what extent do you have to travel as part of your work?',
    trav_pro_option: {
      local: 'Local',
      local_hint: '<15 km: Geneva and surroundings',
      region: 'Regional',
      region_hint: '15-400 km: Lausanne, Bern, Zürich',
      inter: 'International',
      inter_hint: '>400 km: Paris, London, Amsterdam',
    },
    freq_trav_pro_local_hint: 'Local',
    freq_trav_pro_region_hint: 'Regional',
    freq_trav_pro_inter_hint: 'International',
    days_per_month: 'In days per month',
    freq_mod_pro: 'How often do you use the following modes of transport for your business trips?',
    importance: 'How important are the following elements to you in your daily mobility?',
    importance_hint: 'On a scale of 1 (not important at all) to 5 (very important)',
    importance_time: 'Travel time',
    importance_cost: 'Cost',
    importance_flex: 'Flexibility/autonomy',
    importance_rel: 'Reliability/punctuality',
    importance_comfort: 'Comfort of the journey',
    importance_most: 'Ability to make the most of travel time',
    importance_env: 'Environment (reducing pollution)',
    needs: 'How suitable are the following modes of transport for your daily mobility needs?',
    needs_hint: 'On a scale of 1 (not at all suitable) to 5 (completely suitable)',
    adjectives: 'What adjectives do you associate with the following modes of transport?',
    adjectives_hint: 'Select 3 adjectives per mode of transport',
    adjectives_option: {
      fast: 'Fast',
      slow: 'Slow',
      cheap: 'Cheap',
      expensive: 'Expensive',
      practical: 'Practical',
      impractical: 'Impractical',
      ecological: 'Ecological',
      polluting: 'Polluting',
      safe: 'Safe',
      dangerous: 'Dangerous',
      pleasant: 'Pleasant',
      unpleasant: 'Unpleasant',
      autonomous: 'Autonomous',
      constraining: 'Constraining',
      relax: 'Relaxing',
      tiring: 'Tiring',
      healthy: 'Healthy',
      bad_weather: 'Exposed to bad weather',
      reliable: 'Reliable',
      congested: 'Congested',
    },
    comments: 'Thank you! Do you have any comments on this survey or on the mobility plan process?',
    recommendations: 'Recommended modes of transport for your home-to-work journeys',
    recommendations_pro: 'Recommended modes of transport for your professional journeys:',
    actions: 'No measures | Your employer measure: {actions} | Your employer measures: {actions}',
    actions_global:
      'No global measures | Your employeur also proposes the measure: {actions} | Your employeur also proposes the measures: {actions}',
  },
  main_mode: {
    walking: 'At present, you mainly walk to get to your workplace.',
    bike: 'At present, you mainly use a bicycle or an electric bike to get to your workplace.',
    pub: 'At present, you mainly use public transport to get to your workplace.',
    moto: 'At present, you mainly use a motorcycle, scooter or moped to get to your workplace.',
    car: 'At present, you mainly use a car to get to your workplace.',
    train: 'At present, you mainly use a train to get to your workplace.',
    combined: 'At present, you mainly use a combination of modes to get to your workplace.',
    sustainable:
      'Your commuting habits are already sustainable. The following alternatives are available to you:',
    not_sustainable:
      'Based on the information you have entered, the following alternative modes are recommended:',
    actions: 'Your employer implements the following measures to promote sustainable mobility',
  },
  reco: {
    covoit: 'Carpooling',
    elec: 'Electric vehicle',
    inter: 'Intermodality',
    marche: 'Walking',
    tpu: 'Public transport',
    train: 'Train',
    vae: 'Electric bike',
    velo: 'Bike',
  },
  actions: {
    budget: 'Sustainable mobility budget',
    wfh: 'Ability to work from home',
    wftp: 'Ability to work remotely',
    tpg_pass: 'Public transport (UNIRESO) pass',
    lex_pass: 'Léman express pass',
    cff_pass_ag: 'Train pass (general pass)',
    cff_pass_dtp: 'Train pass (1/2 fare plus)',
    cff_pass_dt: 'Train pass (1/2 fare)',
    pnr_pass: 'Park and Ride pass',
    shuttle: 'Shuttle from the nearest train station',
    velo_station: 'Velo-station pass',
    bike_subs: 'Subsidy for the purchase of a bicycle/e-bike',
    shower: 'Showers, lockers and changing rooms',
    bike_parking: 'Secure bicycle parking',
    ebike_charging: 'E-bike battery charging',
    bike_equipment: 'Subsidy for the purchase of bicycle safety and comfort gear',
    carpool_subs: 'Reimbursement of car-pooling journeys',
    carpool_connect: 'Connection to nearby colleagues to facilitate car-pooling',
    carpool_parking: 'Parking spots reserved for car-pooling',
    ev_charging: 'EV charging at the workplace',
    mobility_pass: 'Mobility car-sharing pass',
    ebike_fleet: 'E-bike fleet for professional trips',
    tpu_pro: 'Public transport (UNIRESO) pass',
    train_pro: 'Train pass (general pass)',
    ev_fleet: 'EV fleet for professional trips',
  },
  benefits: {
    show: 'Show benefits',
    hide: 'Hide benefits',
  },
  resume: 'Resume',
  start_new: 'Or start a new survey',
  start: 'Start',
  token: 'Token',
  lookup_address_or_select_on_map: 'Lookup address or select on map',
  type_enter_to_lookup_address: 'Type address, then press Enter to lookup',
  welcome: 'Welcome to the {brand}',
  welcome_intro: 'Please fill out the survey to help us improve your daily commute.',
  no_results: 'No results',
  local: 'Local',
  regional: 'Regional',
  international: 'International',
  finish: 'Finish',
  next: 'Next',
  previous: 'Previous',
}
