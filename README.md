Cutoff Analysis
===============

Data should exist in the following directory structure:

    results/
      meta.txt
      race0/
        race0_<year>.csv
        race0_<year>.csv
      race1/
        race1_<year>.csv
        race1_<year>.csv
      race2/
        race2_<year>.csv
        race2_<year>.csv

Data for each race/year should exist in a CSV file with header that looks like:

    Name,Age,Sex,Time[,Max Age]
    AAAAHH,18,M,10000,35
    Bob Jones,70,M,10000,99
    stacy d orange,37,F,10000
    ...

Max Age can be included if only the age *group* is specified, to mark the last value, but is not required

-   Name: String (possibly UTF-8)
-   Age: Integer (1 - 99, unknown: 0)
-   Max Age: Integer (3 - 101, unknown: 0)
-   Sex: M|F
-   Time: Chip finish time in *seconds* (integer)

Of note, names should be normalized to "*FIRST [M] LAST*", not "LAST, FIRST", but capitalization is irrelevant.

Add race and years to meta.txt for which data exists in the following format, where `run_year` is the actual year the race was run and `qual_year` is the Boston marathon year for which the race qualifies:

    race,run_year,qual_year
    race0,2015,2017
    race0,2014,2016
    race0,2013,2015
    race1,2016,2017
    race1,2015,2016
    race1,2014,2015

I suspect, but have not tested, that double qualifiers can simply be included twice.

The following derived data are computed:

-   Boston age group
-   Boston age group for maximum age on race day (generally, Age or Max Age + 2 years)
-   Qualifying margin, in seconds, where positive values are qualifiers
-   Max qualifying margin, same using Max Age
-   If Boston has already been run for this qualifying year:
      How many of the qualifiers actually ran
      (this is based on my rough matching of names and ages, undoubtedly it is not perfect)

The aptly named "`convert_data.py`" converts these data to a numpy array in a file also aptly named "`data.npy`" in this form:
    numpy.dtype([('race', 'u1'), ('year', 'u2'), ('age', 'u1'), ('max_age', 'u1'), ('age_group', 'u1'), ('max_age_group', 'u1'), ('margin', 'i4'), ('max_margin', 'i4'), ('ran', 'u1')])

Then just run predict.py and it will dump a ton of information.
