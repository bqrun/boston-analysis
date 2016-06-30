import pandas as pd
import numpy as np

RACES = ["bayshore", "baystate", "bigcottonwood", "berlin", "boston", "california_intl", "chicago", "columbus", "erie", "eugene", "grandmas", "houston", "indianapolis", "lehigh", "london", "mcm", "mohawkhudson", "mountains2beach", "nyc", "ottawa", "philadelphia", "portland", "richmond", "santarosa", "stgeorge", "steamtown", "toronto", "twincities", "vermont", "wineglass"]
# includes the top 25 for any of the past 3 years

CUTOFFS = {"2016": 147, "2015": 62, "2014": 98, "2013": 0, "2012": 74} # seconds

# assumption: 2017 will have a field size of 30k
FIELD_SIZES = {"2017": 30000, "2016": 30000, "2015": 30000, "2014": 36000, "2013": 27000, "2012": 27000}
FOR_QUAL = 0.8
# approx. 80% is for qualifiers

QUAL_TIMES = ["3:35:00", "3:40:00", "3:45:00", "3:55:00", "4:00:00", "4:10:00", "4:25:00", "4:40:00", "4:55:00", "5:10:00", "5:25:00",
              "3:05:00", "3:10:00", "3:15:00", "3:25:00", "3:30:00", "3:40:00", "3:55:00", "4:10:00", "4:25:00", "4:40:00", "4:55:00",
              "0:00:00"] # people with no age group cannot qualify

AGE_GROUPS = [(18, 34, 'F'), (35, 39, 'F'), (40, 44, 'F'), (45, 49, 'F'), (50, 54, 'F'), (55, 59, 'F'), (60, 64, 'F'), (65, 69, 'F'), (70, 74, 'F'), (75, 79, 'F'), (80, 99, 'F'),
              (18, 34, 'M'), (35, 39, 'M'), (40, 44, 'M'), (45, 49, 'M'), (50, 54, 'M'), (55, 59, 'M'), (60, 64, 'M'), (65, 69, 'M'), (70, 74, 'M'), (75, 79, 'M'), (80, 99, 'M'),
              None]
ag_lookup = {}
for i in xrange(len(AGE_GROUPS)-1):
  ag = AGE_GROUPS[i]
  for a in xrange(ag[0], ag[1]+1):
    ag_lookup[ag[2] + str(a)] = i


QUAL_SECS = [int(q.split(':')[0]) * 3600 + int(q.split(':')[1]) * 60 + int(q.split(':')[2]) for q in QUAL_TIMES]


def age_group_stats(d):
  print "Age Group\tFinishers\tQualifiers (%)"
  for i in xrange(len(AGE_GROUPS)):
    ag = AGE_GROUPS[i]
    group = d[d["Age Group"] == i]
    qual = group[group["Qualifier"] == "BQ"]
    print "%s %i-%i" % (ag[2], ag[0], ag[1]), '\t',  group.shape[0], '\t', qual.shape[0], "(%.2f%%)" % (float(qual.shape[0])/group.shape[0]*100)


def margin_stats(d):
  print "Margin (min)\tFinishers\tPercent"
  for margin_low, margin_high in [(-np.inf,0), (0,60), (60,120), (120,180), (180,240), (240,300), (300,600), (600,1200), (1200,np.inf)]:
    group = d[(d["Margin"] >= margin_low) & (d["Margin"] < margin_high)]
    print "%s\t%i\t%.2f%%" % ((("[" if margin_low > -np.inf else "(") + str(margin_low/60) + "," + str(margin_high/60) + ")"), group.shape[0], (float(group.shape[0]) / d.shape[0] * 100))


def add_age_group(d):
  ag = []
  max_ag = []
  for rid, record in d.iterrows():
    found = False

    if 18 <= record["Age"] <= 99:
      a = str(record["Sex"]) + str(int(record["Age"]))
      ag.append(ag_lookup[a])
    else:
      ag.append(len(AGE_GROUPS)-1)

    ma = record["Max Age" if "Max Age" in record else "Age"]
    if 18 <= ma+2 <= 101:
      a = str(record["Sex"]) + str(min(int(ma) + 2, 99))
      max_ag.append(ag_lookup[a])
    else:
      max_ag.append(len(AGE_GROUPS)-1)

  d["Age Group"] = ag
  d["Max Age Group"] = max_ag


def add_margin(d):
  m = []
  n = [] # max age group margin
  for rid, record in d.iterrows():
    m.append((QUAL_SECS[int(record["Age Group"])] - int(record["Time"])) if int(record["Time"]) != 0 else -100000)
    n.append((QUAL_SECS[int(record["Max Age Group"])] - int(record["Time"])) if int(record["Time"]) != 0 else -100000)
  d["Margin"] = m
  d["MAG Margin"] = n


def add_bq(d):
  d["Qualifier"] = ["BQ" if record["Margin"] >= 0 else "" for rid, record in d.iterrows()]
  d["MAG Qualifier"] = ["BQ" if record["MAG Margin"] >= 0 else "" for rid, record in d.iterrows()]


def actually_ran(d, boston):
  ran = {record["Name"]:record for rid, record in boston.iterrows()}
  fn_ln_map = {}
  for rid, record in boston.iterrows():
    names = record["Name"].split()
    # remove first or middle initial, as the case may be
    if len(names) > 2:
      if len(names[1]) == 1:
        names.pop(1)
      elif len(names[0]) == 1:
        names.pop(0)
    if len(names) == 1:
      # can't match these people unless they're prefect hits
      continue
    fn = names[0]
    ln = names[-1]
    fn_ln_map[fn+' '+ln] = record
  n = 0
  ran_flag = []
  for rid, record in d.iterrows():
    # consider only possible qualifiers
    if record["MAG Margin"] < 0:
      ran_flag.append(0)
      continue
    match = None
    # check for perfect hit
    if ran.has_key(record["Name"]):
      match = ran[record["Name"]]
    # check for close fn:ln hit
    else:
      names = record["Name"].split()
      if len(names) > 2:
        if len(names[1]) == 1:
          names.pop(1)
        elif len(names[0]) == 1:
          names.pop(0)
      elif len(names) == 1:
        ran_flag.append(0)
        continue
      fn = names[0]
      ln = names[-1]
      if fn_ln_map.has_key(fn+' '+ln):
        match = fn_ln_map[fn+' '+ln]
    if match is not None:
      if "Max Age" in record and record["Age"] <= match["Age"] and record["Max Age"] + 2 >= match["Age"]: # as permissive as possible
        ran_flag.append(1)
        n += 1
      elif match["Age"] >= record["Age"] and match["Age"] - record["Age"] <= 2:
        ran_flag.append(1)
        n += 1
      else:
        ran_flag.append(0)
        pass
    else:
      ran_flag.append(0)
  d["Ran"] = ran_flag
  return n


if __name__ == "__main__":

  # load meta information
  data = [line.strip().split(',') for line in open("results/meta.txt").read().strip().split('\n')]
  meta = {(d[0], d[2]): {data[0][i]: d[i] for i in xrange(len(d))} for d in data[1:]} # index by (name, qual_year)
  races = list(set(d[0] for d in data[1:]))

  data = []

  for year in ["2012", "2013", "2014", "2015", "2016", "2017"]:
    print
    print "Qualifying for %s:" % year
    print "Race\tFinishers\tQualifiers\tRan Boston"

    # get boston results for this year
    boston = None
    if int(year) < 2017:
      boston = pd.read_csv("results/boston/boston_%s.csv" % year)
      add_age_group(boston)

    # --------------------- Race Loop ---------------------

    for race in races:
      r = RACES.index(race)
      print race
      if not meta.has_key((race, year)):
        print "No data from %s for qualifying year %s" % (race, year)
        continue
      info = meta[(race, year)]
      d = pd.read_csv("results/%s/%s_%s.csv" % (race, race, info["run_year"]))

      # drop incomplete records
      d.dropna(how='any', subset=["Age", "Sex", "Time"], inplace=True)

      if not "Max Age" in d:
        d["Max Age"] = [record["Age"] for rid, record in d.iterrows()]

      add_age_group(d)
      add_margin(d)
      add_bq(d)

      # get qualifiers
      bq = d.groupby("Qualifier").get_group("BQ").shape[0]
      max_bq = d.groupby("MAG Qualifier").get_group("BQ").shape[0]

      #age_group_stats(d)
      #margin_stats(d)

      if boston is not None:
        name_age_matches = actually_ran(d, boston)
        print race, '\t', d.shape[0], '\t', bq, '-', max_bq, '\t', name_age_matches
      else:
        d["Ran"] = [0 for rid,record in d.iterrows()]
        print race, '\t', d.shape[0], '\t', bq, '-', max_bq

      for rid, record in d.iterrows():
        # (race_id, qual_year, age, max_age, age_group, max_age_group, margin, max_margin, ran?)
        data.append((r, int(year), record["Age"], record["Max Age"], record["Age Group"], record["Max Age Group"], record["Margin"], record["MAG Margin"], record["Ran"]))

    # --------------------- /Race Loop ---------------------

  # (race_id, qual_year, age, max_age, age_group, max_age_group, margin, max_margin, ran?)
  dt = np.dtype([('race', 'u1'), ('year', 'u2'), ('age', 'u1'), ('max_age', 'u1'), ('age_group', 'u1'), ('max_age_group', 'u1'), ('margin', 'i4'), ('max_margin', 'i4'), ('ran', 'u1')])
  datadump = np.array(data, dtype=dt)
  np.save("data.npy", datadump)

