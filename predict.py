import numpy as np


RACES = ["bayshore", "baystate", "bigcottonwood", "berlin", "boston", "california_intl", "chicago", "columbus", "erie", "eugene", "grandmas", "houston", "indianapolis", "lehigh", "london", "mcm", "mohawkhudson", "mountains2beach", "nyc", "ottawa", "philadelphia", "portland", "richmond", "santarosa", "stgeorge", "steamtown", "toronto", "twincities", "vermont", "wineglass"]
# includes the top 25 for any of the past 3 years

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
  reg_by_margin(data, 2012, 2017)
  for year in range(2012, 2018):
    print
    print "Qualifying year %i" % year
    display_year_data(data, year)
    if year > 2012:
      simple_analysis(data, year, CUTOFFS[year-1], margin_field='margin')
      stage1_analysis(data, year, CUTOFFS[year-1], margin_field='max_margin')
      stage2_analysis(data, year, CUTOFFS[year-1], margin_field='max_margin')


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


def reg_by_margin(data, start_year, end_year, margin_field='margin'):
  margin_hist = []
  rate_hist = []
  ran_hist = []
  for year in range(start_year, end_year+1):
    yeardata = np.sort(data[data["year"] == year], order=margin_field)[::-1]
    print yeardata[yeardata[margin_field] >= 0][-1926], "cutoff:", yeardata[yeardata[margin_field] >= 0][-1926][margin_field]
    n_qualifiers = yeardata[yeardata[margin_field] >= 0].shape[0]
    margin_distr = np.zeros(1000)
    ran_distr = np.zeros(1000)
    for a in yeardata:
      if a[margin_field] > 10000 or a[margin_field] < 0:
        continue
      margin_distr[int(a[margin_field])/10] += 1.0
      if a["ran"] == 1:
        ran_distr[int(a[margin_field])/10] += 1.0
    if len(margin_hist) == 0:
      for i in xrange(len(margin_distr)):
        margin_hist.append([i*10, margin_distr[i]])
        ran_hist.append([i*10, ran_distr[i]])
        rate_hist.append([i*10, ran_distr[i] / margin_distr[i]])
    else:
      for i in xrange(len(margin_distr)):
        margin_hist[i].append(margin_distr[i])
        ran_hist[i].append(ran_distr[i])
        rate_hist[i].append(ran_distr[i] / margin_distr[i])

  print "Qualifiers:"
  print "["
  print "  ['Margin'," + ','.join("'%i'" % y for y in range(start_year, end_year+1)) + "],"
  for c in margin_hist[:401]:
    print "  [" + ','.join(["%i" % a for a in c]) + "],"
  print "]"

  print "Ran:"
  print "["
  print "  ['Margin'," + ','.join("'%i'" % y for y in range(start_year, end_year+1)) + "],"
  for c in ran_hist[:401]:
    print "  [" + ','.join(["%i" % a for a in c]) + "],"
  print "]"

  print "Register rate:"
  print "["
  print "  ['Margin'," + ','.join("'%i'" % y for y in range(start_year, end_year+1)) + "],"
  for c in rate_hist[:401]:
    print "  [" + ','.join(["%.4f" % a for a in c]) + "],"
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
# weight qualifiers by the registration rate for their race AND registration rate by qual margin
# pick the top last_met_cutoff people
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

  # compute weights by margin (<5, 5-10, 10-20, 20+)
  margin_weights = []
  for min_margin, max_margin in [(0, 300), (300, 600), (600, 1200), (1200, 999999999)]:
    margindata = lastyeardata[min_margin <= lastyeardata[margin_field]]
    margindata = margindata[max_margin > margindata[margin_field]]
    n_ran = margindata[margindata["ran"] == 1].shape[0]
    n_met_cutoff = margindata[margindata[margin_field] >= last_cutoff].shape[0]
    margin_weights.append((float(n_ran) / n_met_cutoff) if n_met_cutoff > 0 else 0)

  cumulative_weight = 0
  for i in xrange(yeardata.shape[0]):
    cumulative_weight += weights[yeardata[i]["race"]] / registration_rate * margin_weights[0 if yeardata[i][margin_field] < 300 else (1 if yeardata[i][margin_field] < 600 else (2 if yeardata[i][margin_field] < 1200 else 3))]
    if yeardata[i][margin_field] < 0:
      break

  print "%i qualifiers from %i are expected to register" % (i, year)
  print "Cumulative expected registrants:", cumulative_weight

  cumulative_weight = 0
  for i in xrange(yeardata.shape[0]):
    cumulative_weight += weights[yeardata[i]["race"]] / registration_rate * margin_weights[0 if yeardata[i][margin_field] < 300 else (1 if yeardata[i][margin_field] < 600 else (2 if yeardata[i][margin_field] < 1200 else 3))]
    if cumulative_weight >= last_ran:
      break

  print "%i qualifiers from %i required to reach %i's total" % (i, year, year-1)
  print "Cumulative expected registrants:", cumulative_weight
  print "They meet a margin of %i seconds" % (yeardata[i][margin_field])


if __name__ == "__main__":
  main()
