
import numpy as np


RACES = ["bayshore", "baystate", "bigcottonwood", "berlin", "boston", "california_intl", "chicago", "columbus", "erie", "eugene", "grandmas", "houston", "indianapolis", "lehigh", "mcm", "mountains2beach", "nyc", "ottawa", "philadelphia", "portland", "richmond", "santarosa", "stgeorge", "steamtown", "toronto", "twincities", "vermont"]
# for 2014: "eugene", "vermont"
# for 2015: "bigcottonwood", "toronto"

RACES2017 = ["baystate", "berlin", "california_intl", "chicago", "columbus", "houston", "indianapolis", "mcm", "nyc", "philadelphia", "portland", "richmond", "stgeorge", "steamtown", "twincities"]
RACES2016 = ["bayshore", "baystate", "berlin", "boston", "california_intl", "chicago", "columbus", "erie", "eugene", "grandmas", "houston", "indianapolis", "lehigh", "mcm", "mountains2beach", "nyc", "ottawa", "philadelphia", "portland", "richmond", "santarosa", "stgeorge", "steamtown", "twincities", "vermont"]

CUTOFFS = {2016: 147, 2015: 62, 2014: 98, 2013: 0, 2012: 74} # seconds

# assumption: 2017 will have a field size of 30k
FIELD_SIZES = {2017: 30000, 2016: 30000, 2015: 30000, 2014: 36000, 2013: 27000, 2012: 27000}
FOR_QUAL = 0.8 # approx. 80% is for qualifiers


# (race_id, qual_year, age, max_age, age_group, max_age_group, margin, max_margin, ran?)
#dt = np.dtype([('race', 'u1'), ('year', 'u2'), ('age', 'u1'), ('max_age', 'u1'), ('age_group', 'u1'), ('max_age_group', 'u1'), ('margin', 'u2'), ('max_margin', 'u2'), ('ran', 'u1')])
data = np.load("data.npy")

recidivism = [[] for race in RACES]
recidivism_est = [None for race in RACES]

margin_field = "max_margin"

for year in range(2012, 2018):
  yeardata = np.sort(data[data["year"] == year], order=margin_field)[::-1]
  has_races = np.array(list(set(yeardata["race"])))
  print "%i records for %i" % (yeardata.shape[0], year)

  if yeardata.shape[0] < 1:
    print "No data for %s" % year
    continue

  last_year = year-1

  racedata = [yeardata[yeardata["race"] == r] for r in xrange(len(RACES))]

  # we can get actual registration percentages
  total_br = yeardata[yeardata["ran"] == 1].shape[0] # br: boston runners
  frac_field = float(total_br) / (FIELD_SIZES[year] * FOR_QUAL)
  print "Qualifiers from these races make up approx. %.2f%% of the Boston field." % (frac_field*100)

  qualifiers_who_ran = [(r, float(racedata[r][racedata[r]["ran"] == 1].shape[0]) / max(1, racedata[r][racedata[r][margin_field] >= 0].shape[0])) for r in xrange(len(RACES))]

  # compute weights per race
  weights = np.zeros(len(RACES), dtype='f4')

  total_finishers = 0
  total_qualifiers = 0
  total_ran = 0
  for r, q_frac in qualifiers_who_ran:

    # total only over a subset of races
    '''
    if not RACES[r] in RACES2016:
      continue
    '''

    finishers = racedata[r].shape[0]
    qualifiers = racedata[r][racedata[r][margin_field] >= 0].shape[0]
    ran = racedata[r][racedata[r]["ran"] == 1].shape[0]
    print RACES[r], '\t', finishers, '\t', qualifiers, '\t', ran, '\t', "%.2f%%" % (q_frac*100)
    weights[r] = float(ran) / max(1, qualifiers)
    total_finishers += finishers
    total_qualifiers += qualifiers
    total_ran += ran
  print "Total", '\t', total_finishers, '\t', total_qualifiers, '\t', total_ran, '\t', "%.2f%%" % (float(total_ran)/total_qualifiers*100)


  # we can get actual qualifiers who met cutoff
  if CUTOFFS.has_key(year):
    print "%i cutoff: %i sec" % (year, CUTOFFS[year])
    met_cutoff = yeardata[yeardata[margin_field] >= CUTOFFS[year]].shape[0]
    print "For %i, %i met the cutoff." % (year, met_cutoff)

  # if we have cutoff data too, we can produce the expected registrants even though we also know the truth
  if CUTOFFS.has_key(last_year):
    print "%s cutoff: %i seconds" % (last_year, CUTOFFS[last_year])

    met_cutoff = sum(weights[a["race"]] for a in yeardata[yeardata[margin_field] >= CUTOFFS[last_year]])
    print "For %s, %.2f people who met the cutoff were expected to register." % (year, met_cutoff)

    lastyeardata = np.sort(data[data["year"] == last_year], order=margin_field)[::-1]
    # filter down to the set of races for the current year
    lastyeardata = lastyeardata[np.in1d(lastyeardata["race"], has_races)]

    # 1:1 people analysis (no weighting)
    last_n_met = lastyeardata[lastyeardata[margin_field] >= CUTOFFS[last_year]].shape[0]
    n_met = yeardata[yeardata[margin_field] >= CUTOFFS[last_year]].shape[0]
    predicted_cutoff = yeardata[last_n_met-1][margin_field]
    print "For %s, %i met the cutoff." % (last_year, last_n_met)
    print "For %s, %i met the same cutoff." % (year, n_met)
    print "For %s, %i met a cutoff of %i seconds." % (year, last_n_met, predicted_cutoff)


    # weighted analysis
    predicted_margins = [(yeardata[i][margin_field], recidivism_est[yeardata[i]["race"]]) for i in xrange(yeardata.shape[0])]
    #predicted_margins.sort(key = lambda a: -a[0]) # sort descending by margin

    # -- using the historical recidivism rates is more accurate overall than the true number of runners from the past year alone
    #last_ran = lastyeardata[lastyeardata["ran"] == 1].shape[0]
    last_qualifiers = lastyeardata[lastyeardata[margin_field] >= CUTOFFS[last_year]]
    last_ran = sum(recidivism_est[last_qualifiers[i]["race"]] for i in xrange(last_qualifiers.shape[0]))

    n_met = sum(m[1] for m in predicted_margins if m[0] >= CUTOFFS[last_year])

    # adjust for difference in field size:
    target_ran = last_ran * float(FIELD_SIZES[year]) / FIELD_SIZES[last_year]

    # adjust for qualification difference:
    last_qual = lastyeardata[lastyeardata[margin_field] >= 0].shape[0]
    #target_ran *= float(total_qualifiers) / last_qual
    # fancy way:
    # y = x/842 - 10.8
    frac_of_field = (float(total_qualifiers) / 842 - 10.8) / 100
    # only 2017 races:
    frac_of_field = (float(total_qualifiers) / 903 - 10.1) / 100
    print "Fraction of field described by these %i qualifiers: %.4f" % (total_qualifiers, frac_of_field)
    target_ran = FIELD_SIZES[year] * frac_of_field

    tot = 0
    prev = None
    for m in predicted_margins:
      if m[0] != prev:
        prev = m[0]
      tot += m[1]
      if tot >= target_ran:
        predicted_cutoff = m[0]
        break

    print "For %s, %.2f 'people' ran based on recidivism." % (last_year, last_ran)
    print "For %s, %.2f people who met the cutoff would want to run." % (year, n_met)
    print "For %s, %.2f people would get to run given the field size difference (%i - %i) and qualifiers (%.2f - %.2f)." % (year, target_ran, FIELD_SIZES[last_year], FIELD_SIZES[year], last_qual, total_qualifiers)
    print "For %s, %.2f registering people would meet a cutoff of %i seconds." % (year, target_ran, predicted_cutoff)


    ran_per_qual = float(total_ran) / total_qualifiers
    last_ran_per_qual = float(last_ran) / last_qual
    actual_target = target_ran * ran_per_qual / max(1, last_ran_per_qual)

    tot = 0
    prev = None
    for m in predicted_margins:
      if m[0] != prev:
        prev = m[0]
      tot += m[1]
      if tot >= actual_target:
        predicted_cutoff = m[0]
        break

    print "If we knew how many people from these races were going to run:"
    print "For %s, %.2f people would get to run." % (year, actual_target)
    print "For %s, %.2f registering people would meet a cutoff of %i seconds." % (year, actual_target, predicted_cutoff)


  # update average recidivism
  for r in xrange(len(RACES)):
    recidivism[r].append(weights[r])
    recs = [rec for rec in recidivism[r] if rec > 0]
    # running average:
    #recidivism_est[r] = sum(recs)/max(1, len(recs))
    # last:
    #recidivism_est[r] = recs[-1] if len(recs) > 0 else 0
    # last 2 avg:
    recidivism_est[r] = (recs[-1] + recs[-2])/2 if len(recs) >= 2 else 0
    print RACES[r], ["%.4f" % rec for rec in recidivism[r]], "%.4f" % recidivism_est[r]
