import numpy as np


RACES = ["bayshore", "baystate", "bigcottonwood", "berlin", "boston", "california_intl", "chicago", "columbus", "erie", "eugene", "grandmas", "houston", "indianapolis", "lehigh", "mcm", "mountains2beach", "nyc", "ottawa", "philadelphia", "portland", "richmond", "santarosa", "stgeorge", "steamtown", "toronto", "twincities", "vermont"]
# for 2014: "eugene", "vermont"
# for 2015: "bigcottonwood", "toronto"

RACES2017 = ["baystate", "berlin", "boston", "california_intl", "chicago", "columbus", "houston", "indianapolis", "mcm", "nyc", "philadelphia", "portland", "richmond", "stgeorge", "steamtown", "twincities"]
RACES2016 = ["bayshore", "baystate", "berlin", "boston", "california_intl", "chicago", "columbus", "erie", "eugene", "grandmas", "houston", "indianapolis", "lehigh", "mcm", "mountains2beach", "nyc", "ottawa", "philadelphia", "portland", "richmond", "santarosa", "stgeorge", "steamtown", "twincities", "vermont"]

CUTOFFS = {2016: 147, 2015: 62, 2014: 98, 2013: 0, 2012: 74} # seconds

# assumption: 2017 will have a field size of 30k
FIELD_SIZES = {2017: 30000, 2016: 30000, 2015: 30000, 2014: 36000, 2013: 27000, 2012: 27000}
FOR_QUAL = 0.8 # approx. 80% is for qualifiers


# (race_id, qual_year, age, max_age, age_group, max_age_group, margin, max_margin, ran?)
#dt = np.dtype([('race', 'u1'), ('year', 'u2'), ('age', 'u1'), ('max_age', 'u1'), ('age_group', 'u1'), ('max_age_group', 'u1'), ('margin', 'u2'), ('max_margin', 'u2'), ('ran', 'u1')])
data = np.load("data.npy")

register_history = [[] for race in RACES]
register_est = [None for race in RACES]

# all:
use_races = np.array(range(len(RACES)))
# 2017 only:
#use_races = np.array([RACES.index(r) for r in RACES2017])


def main():
  display_registration(data, margin_field="max_margin", display_format="html")
  margin_histogram(data, 2012, 2016)
  for year in range(2012, 2018):
    print
    print "Qualifying year %i" % year
    display_year_data(data, year)
    if year > 2012:
      simple_analysis(data, year, CUTOFFS[year-1], margin_field='margin')
      stage1_analysis(data, year, CUTOFFS[year-1], margin_field='max_margin')
      stage2_analysis(data, year, CUTOFFS[year-1], margin_field='max_margin')

'''
  yeardata = np.sort(data[data["year"] == year], order=margin_field)[::-1]
  yeardata = yeardata[np.in1d(yeardata["race"], use_races)]
  has_races = np.array(list(set(yeardata["race"])))
  print "%i records for %i" % (yeardata.shape[0], year)

  if yeardata.shape[0] < 1:
    print "No data for %s" % year
    continue

  # compute weights per race
  register_rate = np.zeros(len(RACES), dtype='f4')

  # we can get actual qualifiers who met cutoff
  if CUTOFFS.has_key(year):
    print "%i cutoff: %i sec" % (year, CUTOFFS[year])
    met_cutoff = yeardata[yeardata[margin_field] >= CUTOFFS[year]].shape[0]
    print "For %i, %i met the cutoff." % (year, met_cutoff)
    total_registration_rate = float(total_ran) / met_cutoff
    print "Registration rate: %f" % (total_registration_rate)
    print "Expected registrants: %i" % (float(total_ran) / met_cutoff * total_qualifiers)
    print "Met cutoff: %i" % (met_cutoff)
    print "Actually ran: %i" % (total_ran)
    print "Proportion of field: %f" % (float(total_ran) / FIELD_SIZES[year])

    for r in xrange(len(RACES)):
      met_cutoff = racedata[r][racedata[r][margin_field] >= CUTOFFS[year]].shape[0]
      ran = racedata[r][racedata[r]["ran"] == 1].shape[0]
      register_rate[r] = float(ran) / max(1, met_cutoff)

  # if we have cutoff data too, we can produce the expected registrants even though we also know the truth
  if CUTOFFS.has_key(last_year):
    print "%s cutoff: %i seconds" % (last_year, CUTOFFS[last_year])

    lastyeardata = np.sort(data[data["year"] == last_year], order=margin_field)[::-1]
    # filter down to the set of races for the current year
    lastyeardata = lastyeardata[np.in1d(lastyeardata["race"], has_races)]


    # using this year's true registration rates (near perfect "prediction"):
    predicted_margins = [(yeardata[i][margin_field], register_rate[yeardata[i]["race"]]) for i in xrange(yeardata.shape[0])]
    # using last year's registration rates
    predicted_margins = [(yeardata[i][margin_field], register_est[yeardata[i]["race"]]) for i in xrange(yeardata.shape[0])]

    last_met_cutoff = lastyeardata[lastyeardata[margin_field] >= CUTOFFS[last_year]]
    #last_ran = sum(register_est[last_met_cutoff[i]["race"]] for i in xrange(last_met_cutoff.shape[0]))
    last_ran = lastyeardata[lastyeardata["ran"] == 1].shape[0]

    n_met = sum(m[1] for m in predicted_margins if m[0] >= CUTOFFS[last_year])

    # add simulated qualifiers from ALL OTHER marathons using:
    # last year's average registration rate
    # 2014's margin distribution

    #other_ran = FIELD_SIZE[last_year]*FOR_QUAL - last_ran
    last_registration_rate = float(last_ran) / last_met_cutoff
    #est_other_met_cutoff = other_ran / last_registration_rate

    print "Estimated qualifiers from all other marathons: %i" % 0#est_other_qual

    # adjust for qualification difference:
    last_qual = lastyeardata[lastyeardata[margin_field] >= 0].shape[0]
    expected_registrants = float(last_ran) / last_met_cutoff.shape[0] * last_qual
    print "Predicted registrants: %i" % expected_registrants

    # adjust for difference in field size:
    target_ran = last_ran * float(FIELD_SIZES[year]) / FIELD_SIZES[last_year]
    print "Predicted runners: %i" % target_ran

    target_ran = lastyeardata[lastyeardata["ran"] == 1].shape[0] # last year's # runners

    tot = 0
    prev = None
    for m in predicted_margins:
      if m[0] != prev:
        prev = m[0]
      tot += m[1]
      if tot >= target_ran:
        predicted_cutoff = m[0]
        break

    print "For %s, %.2f people from these races ran." % (last_year, last_ran)
    print "For %s, %.2f people who met the %s cutoff would register." % (year, n_met, last_year)
    print "For %s, %.2f people would get to run given the field size difference (%i - %i)." % (year, target_ran, FIELD_SIZES[last_year], FIELD_SIZES[year])
    print "For %s, %.2f registering people would meet a cutoff of %i seconds." % (year, target_ran, predicted_cutoff)


  # update average recidivism
  for r in xrange(len(RACES)):
    # weights are the fraction of *people who met the cutoff* who actually ran
    register_history[r].append(register_rate[r])
    regs = [a for a in register_history[r] if a > 0]
    # running average:
    #register_est[r] = sum(regs)/max(1, len(regs))
    # last 2 avg:
    #register_est[r] = (regs[-1] + regs[-2])/2 if len(regs) >= 2 else 0
    # last:
    register_est[r] = regs[-1] if len(regs) > 0 else 0
    print RACES[r], ["%.4f" % reg for reg in register_history[r]], "%.4f" % register_rate[r]
'''


def display_year_data(data, year, races=RACES, margin_field='margin', display_format="tab"):
  if display_format == "tab":
    begin = ""
    delimiter = "\t"
    end = ""
  elif display_format == "html":
    print "<table><thead><tr><th>Race</th><th>Finishers</th><th>Qualifiers</th><th>Ran Boston</th><th>Registration Rate (%)</th></tr></thead><tbody>"
    begin = "<tr><td>"
    delimiter = "</td><td>"
    end = "</td></tr>"

  yeardata = np.sort(data[data["year"] == year], order=margin_field)[::-1]

  total_finishers = 0
  total_qualifiers = 0
  total_ran = 0
  for r in [RACES.index(race) for race in races]:
    racedata = yeardata[yeardata["race"] == r]

    finishers = racedata.shape[0]
    qualifiers = racedata[racedata[margin_field] >= 0].shape[0]
    ran = racedata[racedata["ran"] == 1].shape[0]
    print begin, RACES[r], delimiter, finishers, delimiter, qualifiers, delimiter, ran, delimiter, "%.2f%%" % (float(ran)/max(1, qualifiers)*100), end
    total_finishers += finishers
    total_qualifiers += qualifiers
    total_ran += ran

  print begin, "Total", delimiter, total_finishers, delimiter, total_qualifiers, delimiter, total_ran, delimiter, "%.2f%%" % (float(total_ran)/total_qualifiers*100), end

  if display_format == "html":
    print "</tbody></table>"


def display_registration(data, races=RACES, margin_field='margin', display_format="tab"):
  if display_format == "tab":
    begin = ""
    delimiter = "\t"
    end = ""
  elif display_format == "html":
    print "<table><thead><tr><th>Race</th><th>Q2012</th><th>Q2013</th><th>Q2014</th><th>Q2015</th><th>Q2016</th></tr></thead><tbody>"
    begin = "<tr><td>"
    delimiter = "</td><td>"
    end = "</td></tr>"

  yeardata = [np.sort(data[data["year"] == year], order=margin_field)[::-1] for year in range(2012, 2017)]

  for r in [RACES.index(race) for race in races]:
    print begin, RACES[r], delimiter,
    for year in range(2012, 2017):
      racedata = yeardata[year-2012][yeardata[year-2012]["race"] == r]
      met_cutoff = racedata[racedata[margin_field] >= CUTOFFS[year]].shape[0]
      ran = racedata[racedata["ran"] == 1].shape[0]
      print "%.4f" % ((float(ran) / met_cutoff) if met_cutoff > 0 else 0), delimiter,
    print end

  reg_rate = []
  field_size = []
  qualifiers = []
  met_cutoff = []
  cutoff = []

  delimiter = delimiter.replace('td', 'th')
  for year in range(2012, 2017):
    yeardata = data[data["year"] == year]
    qual = yeardata[yeardata[margin_field] >= 0].shape[0]
    met = yeardata[yeardata[margin_field] >= CUTOFFS[year]].shape[0]
    ran = yeardata[yeardata["ran"] == 1].shape[0]
    reg_rate.append(float(ran) / met)
    field_size.append(FIELD_SIZES[year])
    cutoff.append(CUTOFFS[year])
    qualifiers.append(qual)
    met_cutoff.append(met)

  print begin.replace('td', 'th'), "Total", delimiter,
  for i in xrange(len(reg_rate)):
    print "%.4f" % (reg_rate[i]), delimiter,
  print end

  if display_format == "html":
    print "</tbody></table>"


  # more global stats
  stats = {
      "Field Size (FS)": ["%i" % f for f in field_size],
      "Qualifiers (Q)": ["%i" % f for f in qualifiers],
      "Met Cutoff (M)": ["%i" % f for f in met_cutoff],
      "Registration Rate (R)": ["%.4f" % f for f in reg_rate],
      "Expected Registrants (Q x R)": ["%i" % (qualifiers[i] * reg_rate[i]) for i in xrange(len(qualifiers))],
      "Ran Boston (M x R)": ["%i" % (met_cutoff[i] * reg_rate[i]) for i in xrange(len(met_cutoff))],
      "% of Field [(M x R) / FS]": ["%.2f%%" % (met_cutoff[i] * reg_rate[i] / field_size[i] * 100) for i in xrange(len(met_cutoff))],
      "Cutoff": ["%i" % f for f in cutoff],
  }

  print
  if display_format == "html":
    delimiter = delimiter.replace('th', 'td')
    print "<table><thead><tr><th>Race</th><th>Q2012</th><th>Q2013</th><th>Q2014</th><th>Q2015</th><th>Q2016</th></tr></thead><tbody>"

  for key in stats.keys():
    print begin, key, delimiter,
    for i in xrange(len(stats[key])):
      print stats[key][i], delimiter,
    print end

  if display_format == "html":
    print "</tbody></table>"


  # reg rate by race (google chart data)
  print "["
  print "  ['Year', " + ','.join("'%s'" % race for race in races) + "],"
  for year in range(2012, 2017):
    yeardata = data[data["year"] == year]
    print "  [%i, " % year,
    for r in [RACES.index(race) for race in races]:
      racedata = yeardata[yeardata["race"] == r]
      met_cutoff = racedata[racedata[margin_field] >= CUTOFFS[year]].shape[0]
      ran = racedata[racedata["ran"] == 1].shape[0]
      print ("%.4f, " % (float(ran) / met_cutoff)) if met_cutoff > 0 else "null, ",
    print "],"
  print "]"


def margin_histogram(data, start_year, end_year, margin_field='margin'):
  margin_hist = []
  for year in range(start_year, end_year+1):
    yeardata = np.sort(data[data["year"] == year], order=margin_field)[::-1]
    n_qualifiers = yeardata[yeardata[margin_field] >= 0].shape[0]
    margin_distr = np.zeros(1000)
    for a in yeardata:
      if a[margin_field] > 10000 or a[margin_field] < 0:
        continue
      margin_distr[int(a[margin_field])/10] += 1.0 #/n_qualifiers
    if len(margin_hist) == 0:
      for i in xrange(len(margin_distr)):
        margin_hist.append([i*10, margin_distr[i]])
    else:
      for i in xrange(len(margin_distr)):
        margin_hist[i].append(margin_distr[i])
  print "["
  print "  ['Margin'," + ','.join("'%i'" % y for y in range(start_year, end_year+1)) + "],"
  for c in margin_hist[:401]:
    print "  [" + ','.join(["%i" % a for a in c]) + "],"
  print "]"


# 1:1 people analysis (no weighting)
def simple_analysis(data, year, last_cutoff, margin_field='margin'):
  yeardata = np.sort(data[data["year"] == year], order=margin_field)[::-1]
  has_races = np.array(list(set(yeardata["race"])))

  lastyeardata = np.sort(data[data["year"] == (year - 1)], order=margin_field)[::-1]
  # filter down to the set of races for the current year
  lastyeardata = lastyeardata[np.in1d(lastyeardata["race"], has_races)]

  last_n_met = lastyeardata[lastyeardata[margin_field] >= last_cutoff].shape[0]
  n_met = yeardata[yeardata[margin_field] >= last_cutoff].shape[0]

  predicted_cutoff = yeardata[last_n_met-1][margin_field]
  print "For %s, %i met the cutoff of %i seconds." % (year-1, last_n_met, last_cutoff)
  print "For %s, %i met a cutoff of %i seconds." % (year, n_met, last_cutoff)
  print "For %s, %i met a cutoff of %i seconds." % (year, last_n_met, predicted_cutoff)


# weight qualifiers by the registration rate for their race and pick
# the top last_met_cutoff people
def stage1_analysis(data, year, last_cutoff, margin_field='margin'):
  yeardata = np.sort(data[data["year"] == year], order=margin_field)[::-1]
  has_races = np.array(list(set(yeardata["race"])))
  lastyeardata = np.sort(data[data["year"] == (year - 1)], order=margin_field)[::-1]
  lastyeardata = lastyeardata[np.in1d(lastyeardata["race"], has_races)]

  last_met_cutoff = lastyeardata[lastyeardata[margin_field] >= last_cutoff].shape[0]
  last_ran = lastyeardata[lastyeardata["ran"] == 1].shape[0]
  registration_rate = float(last_ran) / last_met_cutoff
  print "For %i, %.2f%% of qualifiers registered." % (year-1, registration_rate*100)

  weights = []
  for r in xrange(len(RACES)):
    racedata = lastyeardata[lastyeardata["race"] == r]
    n_ran = racedata[racedata["ran"] == 1].shape[0]
    n_met_cutoff = racedata[racedata[margin_field] >= last_cutoff].shape[0]
    weights.append((float(n_ran) / n_met_cutoff) if n_met_cutoff > 0 else 0)

  cumulative_weight = 0
  for i in xrange(yeardata.shape[0]):
    cumulative_weight += weights[yeardata[i]["race"]]
    if cumulative_weight >= last_ran:
      break

  print "%i qualifiers from %i required to reach %i's total" % (i, year, year-1)
  print "They meet a margin of %i seconds" % (yeardata[i][margin_field])


# experimentation
def stage2_analysis(data, year, last_cutoff, margin_field='margin'):
  yeardata = np.sort(data[data["year"] == year], order=margin_field)[::-1]
  has_races = np.array(list(set(yeardata["race"])))
  lastyeardata = np.sort(data[data["year"] == (year - 1)], order=margin_field)[::-1]
  lastyeardata = lastyeardata[np.in1d(lastyeardata["race"], has_races)]

  last_met_cutoff = lastyeardata[lastyeardata[margin_field] >= last_cutoff].shape[0]

  last_ran = lastyeardata[lastyeardata["ran"] == 1].shape[0]

  registration_rate = float(last_ran) / last_met_cutoff
  print "For %i, %.2f%% of qualifiers registered." % (year-1, registration_rate*100)

  weights = []
  for r in xrange(len(RACES)):

    racedata = lastyeardata[lastyeardata["race"] == r]

    n_ran = racedata[racedata["ran"] == 1].shape[0]
    n_met_cutoff = racedata[racedata[margin_field] >= last_cutoff].shape[0]
    weights.append((float(n_ran) / n_met_cutoff) if n_met_cutoff > 0 else 0)

  cumulative_weight = 0
  for i in xrange(yeardata.shape[0]):
    cumulative_weight += weights[yeardata[i]["race"]]
    if cumulative_weight >= last_ran:
      break

  print "%i qualifiers from %i required to reach %i's total" % (i, year, year-1)
  print "They meet a margin of %i seconds" % (yeardata[i][margin_field])


if __name__ == "__main__":
  main()
