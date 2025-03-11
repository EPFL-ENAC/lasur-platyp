export default {
  main: {
    brand: 'Mobility Toolkit',
  },
  form: {
    error: {
      origin: 'Please enter a valid origin address',
      workplace: 'Please enter a valid work place address',
    },
    age_class: 'What is your age group?',
    age_class_option: {
      '16_17': '16 - 17',
      '18_24': '18 - 24',
      '25_44': '25 - 44',
      '45_64': '45 - 64',
      '65': '65 and more',
    },
    employment_rate: 'What is your employment rate?',
    remote_work_rate: 'What is your remote work rate?',
    company_vehicle: 'Do you have a company vehicle?',
    yes: 'Yes',
    no: 'No',
    workplace: 'Address of usual place of work',
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
      disabled: 'Parking card for disabled people',
    },
    equipments: 'Which of the following do you have access to for your daily commute?',
    equipments_option: {
      bike: 'Bicycle',
      upt_subs: 'Urban public transport subscription',
      train_subs: 'Train subscription',
      car_driver: 'Car (as driver)',
      moto: 'Motorcycle / scooter / moped',
      eab: 'Electrically assisted bicycle',
      mob_subs: 'Shared mobility subscription',
      car_passenger: 'Car (as passenger)',
    },
    freq_mod: 'How often do you use the following modes of transportation to get to work?',
    freq_mod_hint: 'Number of days in a usual week',
    mode: {
      walking: 'Walking (>10 min.)',
      bike: 'Bicycle (or electric bike)',
      pub: 'Public transport',
      moto: 'Motorcycle/scooter',
      car: 'Car (driver/passenger)',
      train: 'Train',
      plane: 'Plane',
      pub_train: 'Public transport and train',
      car_moto: 'Car and motorcycle/scooter',
      combined: 'A combination of these modes of transportation',
    },
    freq_trav_pro_local: 'To what extent do you have to travel locally as part of your work?',
    freq_trav_pro_region: 'To what extent do you have to travel regionally as part of your work?',
    freq_trav_pro_inter:
      'To what extent do you have to travel internationally as part of your work?',
    freq_trav_pro_local_hint: 'Local (<10km: Geneva and surroundings)',
    freq_trav_pro_region_hint: 'Regional (10-300km: Lausanne, Lyon, Bern, Zurich)',
    freq_trav_pro_inter_hint: 'International (>300km: Milan, Paris, Francfort)',
    days_per_month: 'days per month',
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
    adjectives_hint: 'Select up to 3 adjectives per mode of transport',
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
      bad_weather: 'Bad weather',
      reliable: 'Reliable',
      congested: 'Congested',
    },
    comments: 'Thank you! Do you have any comments on this survey or on the mobility plan process?',
    recommendations:
      'Based on the information you have entered, the following modes of transport are recommended for your home-to-work journeys',
    actions:
      'To encourage more sustainable commuting, your employer is implementing the following measures that may be relevant to you',
  },
  reco: {
    covoit: 'Carpooling',
    elec: 'Electric vehicle',
    inter: 'International',
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
    shuttle: 'Shuttle from the enarest train station',
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
  resume: 'Resume',
  start_new: 'Or start a new survey',
  start: 'Start',
  token: 'Token',
  type_enter_to_lookup_address: 'Type enter to lookup the address location',
  welcome: 'Welcome to {brand}',
  welcome_intro: 'Please fill out the survey to help us improve your daily commute.',
  no_results: 'No results',
}
