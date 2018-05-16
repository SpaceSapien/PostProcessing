from pylab import *
from scipy import interpolate
import re
import os
import numpy
import sqlite3
import csv


class SQLLiteObject(object):

    """
    :type _keys: List[unicode]
    :type _db_path: unicode
    :type _db_conn: sqlite3.sqlite3
    :type _db_exe: sqlite3.Cursor
    :type _table_name: unicode
    """

    _keys = None
    _csv_file_path = ""
    _db_path = ""


    def __init__ \
    (
        self,
        table_name: unicode,
        base_dir: unicode,
        database_file: unicode = u"run-data.db",
        base_csv: unicode = u"tallydata.csv"
    ):
        self._keys = []
        self._table_name = table_name
        # Make sure the directory exists
        if not os.path.isdir(base_dir):
            print("%s directory doesn't exist" % base_dir)
            raise

        # Establish a database connection (which will create the file if it isn't there)
        self._db_path = base_dir + "/" + database_file
        self._db_conn = sqlite3.connect(self._db_path)
        self._db_exe = self._db_conn.cursor()
        self._csv_path = base_dir + "/" + base_csv

        # Establish if the table already exists
        table_check_command = "SELECT name FROM sqlite_master WHERE type='table' AND name='%s'" % table_name
        self._db_exe.execute(table_check_command)

        # If it doesn't, create the table
        if self._db_exe.fetchone() is None:
            print("%s table doesn't exist... creating from %s" % (table_name, base_csv))
            self.process_csv_file()

        # Grab data about the table columns
        command = "PRAGMA table_info(%s)" % self._table_name
        data = self._db_exe.execute(command)

        # Store them in the keys list
        self._keys = []

        for row in data:
            self._keys.append(row[1])

    def process_csv_file(self):

        if not os.path.isfile(self._csv_path):
            print("%s csv doesn't exist." % (self._csv_file_path))
            raise

        with open(self._csv_path, 'r') as csv_file_object:

            csv_data = csv.DictReader(csv_file_object, delimiter=',')
            headers = csv_data.fieldnames

            command = "CREATE TABLE IF NOT EXISTS '%s' ( '%s' text" % (self._table_name, headers[0].strip() )

            for header in headers[1:]:
                command += ", '%s' text" % header.strip()

            command += ")"

            self._db_exe.execute(command)

            for row in csv_data:

                command = "INSERT INTO " + self._table_name + " VALUES('" + row[headers[0]] + "'"

                for header in headers[1:]:
                    command += ",'%s'" % row[header]

                command += ")"

                self._db_exe.execute(command)

    def getColumnData(self, column : unicode):

        return_data = []

        if column in self._keys:

            command = "SELECT \"%s\" FROM \"%s\"" % (column, self._table_name)


            self._db_exe.execute(command)
            db_data = self._db_exe.fetchall()

            for row in db_data:
                return_data.append(row[0])


        else:

            print("No column %s in table %s." % (column, self._table_name))
            raise

            #    "CREATE TABLE IF NOT EXISTS tallies ('tally' text, 'zone' integer, 'cell' integer, 'time' real, 'group' integer, 'lower_energy' real, 'upper_energy' real,  'value' real, 'error' real) ")

        return return_data


class TimeBasedSQLLiteObject(SQLLiteObject):

    def __init__\
    (
        self,
        table_name: unicode,
        base_dir: unicode,
        time_column = "Time [s]",
        database_file: unicode = u"run-data.db",
        base_csv: unicode = u"tallydata.csv"
    ):

        super(TimeBasedSQLLiteObject, self).__init__\
        (
            table_name,
            base_dir,
            database_file,
            base_csv
        )
        self._time_column = time_column

        self._interpolate_function = {}

        for column in self._keys:

            self._interpolate_function[column] = False

    def getInterpolatedDataTimeSeries(self, time_array, column):


        if self._interpolate_function[column] == False:

            raw_time, raw_value = self.getRawDataTimeSeries(column)

            #extending the interpolation to infinity
            record_time = [0] + raw_time + [1e100]
            record_value = [raw_value[0]] + raw_value + [raw_value[-1]]

            self._interpolate_function[column] = interpolate.interp1d(record_time, record_value)


        interpolated_values = self._interpolate_function[column](time_array)

        return interpolated_values

    def getRawDataTimeSeries(self, column):

        time_array = [ float(time) for time in self.getColumnData(self.time_column)]

        value_array = []

        for value in self.getColumnData(column): #type: str

            try:

                value_array.append(float(value))

            except:

                value_array.append(0.0)


        return [time_array, value_array]



    def interpolatedData(self, time_array, keys = None):

        if keys == None:

            keys = self.keys

        values = {}

        for column in keys:

            trimmed_whitespace_column = column.strip()
            values[trimmed_whitespace_column] = self.getInterpolatedDataTimeSeries(time_array,column)

        return values

    def getEndingTime(self):

        time_array = self.getColumnData(self._time_column)
        return float(time_array[-1])

    def getFixedTimeData(self,time_array, keys=[]):

        return self.interpolatedData(time_array,keys)

class SingleTally:

    '''
    :type _tally_data: TallyData
    :type _tally_name: unicode
    '''

    _tally_data = None
    _tally_name = None


    def __init__\
    (
        self,
        tally_data,
        tally_name : unicode
    ):
        self._tally_name = tally_name
        self._tally_data = tally_data

    #Return Monoenergetic tally values and error for all times
    def getTallyTotal(self):

        tally_totals = []
        tally_sigmas = []
        tally_time =   []
        #for time in times:

        command = "SELECT \"value\",\"error\",\"time\" FROM %s WHERE tally=\"%s\" AND \"group\"=%g ORDER BY time * 1" % ( self._tally_data._table_name, self._tally_name, -1 )
        print(command)
        data = self._tally_data._db_exe.execute(command)

        for row in data: #self._tally_data._db_exe.fetchone()

            time = row[2]

            if not time in tally_time:
                tally_totals.append(row[0])
                tally_sigmas.append(row[1])
                tally_time.append(row[2])

        # turn the time strings into floats
        tally_time = [ float(time) for time in tally_time ]
        return [ tally_time, tally_totals, tally_sigmas]



    def getColumnData(self, column : unicode):

        return_data = []

        if column in self._keys:

            command = "SELECT \"%s\" FROM \"%s\" WHERE \"Name\"=\"%s\"" % (column, self._table_name, self._tally_name)


            self._db_exe.execute(command)
            db_data = self._db_exe.fetchall()

            for row in db_data:
                return_data.append(row[0])


        else:

            print("No column %s in table %s." % (column, self._table_name))
            raise

            #    "CREATE TABLE IF NOT EXISTS tallies ('tally' text, 'zone' integer, 'cell' integer, 'time' real, 'group' integer, 'lower_energy' real, 'upper_energy' real,  'value' real, 'error' real) ")

        return return_data





    def getFixedTimeData(self,time_array):

        all_energy_bins = []
        all_energy_values = []
        all_energy_sigmas = []

        for current_time in time_array:

            current_energy_bin = self._tally_data._energies
            current_energy_values = []
            current_energy_sigmas = []
            adjusted_time = self._tally_data.getClosestTime(current_time)

            command = "SELECT \"time\",\"group\",\"error\", \"value\" FROM \"%s\" WHERE tally = \"%s\" AND \"group\" >= 0 AND time=\"%s\" ORDER BY \"group\" LIMIT %g" \
                      % (self._tally_data._table_name, self._tally_name, adjusted_time, len(current_energy_bin))

            print(command)
            tally_data = self._tally_data._db_exe.execute(command)

            for time, group, error, value in tally_data:

                current_energy_values.append(value)
                current_energy_sigmas.append(error)

            all_energy_bins.append(current_energy_bin)
            all_energy_values.append(current_energy_values)
            all_energy_sigmas.append(current_energy_sigmas)


        return [ all_energy_bins, all_energy_values, all_energy_sigmas ]

class TallyData(SQLLiteObject):

    _time_column = "Time [s]"
    _name_column = "Name"
    _number_cells = 0
    _number_zones = 0
    _energies = None
    _times = None
    _tallies = None
    _tally_names = None


    """
    :type _tallies: dict[SingleTally]
    :type _energies: List[float]
    """

    def __init__ \
    (
        self,
        table_name: unicode,
        base_dir: unicode,
        database_file: unicode = u"run-data.db",
        base_csv: unicode = u"tallydata.csv"
    ):

        self._energies = []
        self._times = []
        self._tallies = {}
        self._tally_names = set()


        super(TallyData, self).__init__ \
        (
            table_name,
            base_dir,
            database_file,
            base_csv
        )


        self.initialzeData()

    def getClosestTime(self,time):

        adjusted_time = [ abs( float(single_time) - time ) for single_time in self._times ]
        closest_adjusted_time = min( adjusted_time)
        index = adjusted_time.index(closest_adjusted_time)
        matching_time = self._times[index]
        return matching_time

    def process_csv_file(self):


        if not os.path.isfile(self._csv_path):
            print("%s csv doesn't exist." % (self._csv_path))
            raise

        # Create the table
        self._db_exe.execute("CREATE TABLE IF NOT EXISTS \"%s\" ('tally' text, 'zone' integer, 'cell' integer, 'time' text, 'group' integer,  'value' real, 'error' real) " % ( self._table_name))
        self._db_exe.execute("CREATE INDEX time_index ON \"%s\"(time)" % self._table_name)
        self._db_exe.execute("CREATE INDEX name_index ON \"%s\"(tally)" % self._table_name)

        # second figure out how many cells and zones there are
        self._number_zones = 1
        self._number_cells = 1

        with open(self._csv_path, 'r') as csv_file_object:

            csv_data = csv.DictReader(csv_file_object, delimiter=',')

            # Here we are recovering the energy bin bounds which will be the same for all tallies############################
            energy_matches = []

            keys = csv_data.fieldnames

            first_row = next(csv_data)

            # For some of the older data sets there is a space in the time and or name columns
            if self._name_column not in keys:
                self._name_column = " " + self._name_column

            if self._time_column not in keys:
                self._time_column = " " + self._time_column


            #grab all energy bin differentiation
            for key in keys:

                matches = re.match("Energy-([0-9]+) \[MeV\][ ]?$", key)

                if matches:
                    group = int(matches.group(1))
                    energy_matches.append(group)



            # for each row in the tally data
            for row in csv_data:

                zone_cell = row[self._name_column]
                matches = re.match("^[ ]?((Fission-Rate)|(Absorption-Rate)|(Capture-Rate))-([0-9]+)-([0-9]+)$", zone_cell)

                if not matches:
                    matches = re.match("^[ ]?((Flux)|(Fission)|(Absorption))-([0-9]+)-([0-9]+)$", zone_cell)

                try:
                    zone = int(matches.group(5))
                    cell = int(matches.group(6))
                    tally = matches.group(1)

                    # Some of the older tally files use Absorption when we want absorption rate
                    if tally == "Absorption":
                        tally = "Capture-Rate"



                except:

                    print("No zone cell data for tally" + zone_cell)
                    raise

                # for the tallies that have changed name
                tally_current_name = tally + "-" + str(zone) + "-" + str(cell)

                value = float(row['Value'])
                sigma = float(row['Sigma'])
                time = float( row[self._time_column])

                #insert the initial value
                command = "INSERT INTO \"%s\" VALUES ('%s', %g, %g, %s, %g, %e, %e)" % (self._table_name, tally_current_name, zone, cell, time, -1, value, sigma)
                self._db_exe.execute(command)


                for group_index in range( len(energy_matches)):

                    value = float(row['value-' + str(group_index)])
                    sigma = float(row['sigma-' + str(group_index)])
                    time = float(row[self._time_column])

                    if group_index == 999:
                        pass


                    # insert the initial value
                    command = "INSERT INTO \"%s\" VALUES ('%s', %g, %g, %s, %g, %e, %e)" % (
                    self._table_name, tally_current_name, zone, cell, time, group_index, value, sigma)
                    self._db_exe.execute(command)

                    #print(command)


    def initialzeData(self):

        with open(self._csv_path, 'r') as csv_file_object:

            csv_data = csv.DictReader(csv_file_object, delimiter=',')

            # Here we are recovering the energy bin bounds which will be the same for all tallies############################
            energy_matches = []
            keys = csv_data.fieldnames
            first_row = next(csv_data)

            # grab all energy bin differentiation
            for key in keys:

                matches = re.match("Energy-([0-9]+) \[MeV\][ ]?$", key)

                if matches:
                    group = int(matches.group(1))
                    energy_matches.append(group)

            energy_matches.sort()


            for energy_match in energy_matches:
                key = "Energy-" + str(energy_match) + " [MeV]"
                value = float(first_row[key])
                self._energies.append(value)



        command = "SELECT DISTINCT(tally) FROM \"%s\"" % self._table_name
        data = self._db_exe.execute(command)


        for tally_name, in data:
            self._tally_names.add(tally_name)
            tally = SingleTally(self,tally_name)
            self._tallies[tally_name] = tally

        command = "SELECT DISTINCT(\"time\") FROM \"%s\" ORDER BY \"time\"" % self._table_name
        data = self._db_exe.execute(command)

        for time, in data:
            self._times.append(time)


        command = "SELECT MAX(\"zone\") FROM \"%s\"" % self._table_name
        data = self._db_exe.execute(command)
        self._number_zones, = data.fetchone()

        command = "SELECT MAX(\"cell\") FROM \"%s\"" % self._table_name
        data = self._db_exe.execute(command)
        self._number_cells, = data.fetchone()

    def getFixedTimeData(self,fixed_time_array, desired_keys = None):

        #only use the keys we want to lookup
        if desired_keys is None:

            desired_keys = self._tallies

        fixed_time_tally_data = {}


        for key in desired_keys:
            fixed_time_tally_data[key] = self._tallies[key].getFixedTimeData(fixed_time_array)

        return fixed_time_tally_data

    def getRelativeTallyTotals(self,type="Flux"):

        tally_fractions = {}
        tally_fraction_sigmas = {}
        tally_max = [0] * len(self._times)


        # For every cell/zone look at each timestep and find the maximum tally count
        for zone in range(1,self._number_zones+1):

            for cell in range(1,self._number_cells + 1):

                key = type + "-" + str(zone) + "-" + str(cell)

                tally_obj = self._tallies[key]
                [times, tally_counts, tally_sigmas] = tally_obj.getTallyTotal()

                for index in range( len(tally_counts) ):

                    if tally_max[index] < tally_counts[index]:
                        tally_max[index] = tally_counts[index]


        # For every cell zone and timestep
        for zone in range(1,self._number_zones+1):

            for cell in range(1,self._number_cells + 1):

                key = type + "-" + str(zone) + "-" + str(cell)

                #note sigma is in fraction error
                [times, tally_counts, tally_sigmas] = self._tallies[key].getTallyTotal()

                tally_fractions[key] = [ counts/totals for counts,totals in zip(tally_counts,tally_max)]

                try:
                    tally_fraction_sigmas[key] = [ sigma*fraction for sigma,counts, fraction in zip(tally_sigmas, tally_counts, tally_fractions[key]) ]

                except:

                    tally_fraction_sigmas[key] = [0] * len(self._times)

        return [times, tally_fractions, tally_fraction_sigmas]
