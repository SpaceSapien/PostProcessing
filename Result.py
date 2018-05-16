import CSVClasses
import SQLiteClasses
import Worth
import csv
import os

class Result:

    """
    :type _simulation_data: SimulationResults
    """


    def __init__(self, basedir, folder):

        self._basedir = basedir
        self._folder = folder

        if (not os.path.isdir(self.getPath() ) ):

            raise Exception("Folder " + self.getPath() + " doesn't exist")

        datafile = self.getCSVDataFile("datafile.csv")
        temperature = self.getCSVDataFile("temperature-data.csv")
        tally = self.getCSVDataFile("tallydata.csv")
        worth = self.getCSVDataFile("worth.csv")
        moderator_worth  = self.getCSVDataFile("moderator-worth.csv")
        fuel_worth = self.getCSVDataFile("fuel-worth.csv")



        # 'Neutron Lifetime sigma [s]','Power [W/m^3]','k_eff','Beta_eff sigma','Iteration', 'neutron lifetime [s]',
        # 'Edge Temp [K]','Run Time [s]','Group 1','Group 2','Group 3','Group 5','Group 4','Group 6'

        microcell_temperature = self.getCSVDataFile("microscale-aggregate-data.csv")

        if microcell_temperature:

            self._microcell_temperature = CSVClasses.TimeBasedCSVDataObject(microcell_temperature, 'Time [s]')

        else:

            self._microcell_temperature = False

        if datafile:

            self._simulation_data = CSVClasses.SimulationResults(datafile, 'Time [s]')

        if temperature:

            self._temperature_data = CSVClasses.TemperatureData(temperature, 'Time [s]')
        else:
            self._temperature_data = False

        if tally:

            self._tally_data =  SQLiteClasses.TallyData(u"Tallies", self.getPath() )

        else:

            self._tally_data = False

        if worth:

            self._worth_data = Worth.WorthResults(worth)

        else:

            self._worth_data = False


        if moderator_worth:

            self._moderator_worth_data = Worth.WorthResults(moderator_worth, type="Moderator")

        else:

            self._moderator_worth_data = False

        if fuel_worth:

            self._fuel_worth_data = Worth.WorthResults(fuel_worth)

        else:

            self._fuel_worth_data = False

        self._ordered_temperature = False
        self._ordered_time = False

    def getSimulationData(self,microcell=False):

        return self._simulation_data

    def getPath(self):

        return self._basedir + self._folder

    def getFolderName(self):

        return self._folder

    def getTemperatureExtremes(self):

        if self._temperature_data:

            return self._temperature_data.getTemperatureExtremes()

        else:

            return [300, 3000]

    def getCSVDataFile(self, datafile):

        datafile_path = self.getPath() + "/" + datafile

        if (not os.path.isfile(datafile_path)):

            print("Datafile " + datafile_path + " doesn't exist")
            return False

        csv_data = self.getFileData(datafile_path)

        return csv_data

        # def processTallyData(self):
    def getTemperatureVsTime(self, positions):

        #if self._ordered_time == False or self._ordered_temperature == False:

        ordered_data = []
        times = []

        for row in self._temperature_data.csv_data:

            times.append(row["Time [s]"])


        for key in self._temperature_data.keys:

            if key != "Time [s]" and key != "Time [s] " and key != " " and key != "":

                key_data = { "temperature" : [], "position" : float(key) }

                for row in self._temperature_data.csv_data:

                    key_data["temperature"].append(float(row[key]))

                ordered_data.append(key_data)

        ordered_data.sort(key=lambda position: position['position'])

        max_position = ordered_data[-1]["position"]

        if max_position <= 0:
            max_position = 1

        for data in ordered_data:

            data["position"] *= 100.0/ max_position

        times = [ float(time) for time in times]


        return_ordered_data = []

        for position in positions:

            lower = -1

            for index in range( len(ordered_data) ):


                higher = ordered_data[index]["position"]

                if (position >= lower and position <= higher) or index == len(ordered_data) - 1:

                    return_ordered_data.append(ordered_data[index])
                    break

                lower = higher

        return_ordered_data.sort(key=lambda position: position['position'])

        #self._ordered_temperature = return_ordered_data
        #self._ordered_time = times

        return [times, return_ordered_data]




    def getFixedTimeData(self,desired_time_array, sync_tally = True):

        ending_time = self.getEndingTime()

        time_array = [ time for time in desired_time_array ]

        data = self._simulation_data.getFixedTimeData(time_array)
        [positions, all_temperatures] = self._temperature_data.getFixedTimeData(time_array)

        tally_data = []
        if self._tally_data and sync_tally:

            tally_data = self._tally_data.getFixedTimeData(time_array)

        microcell_temp = []
        if self._microcell_temperature:

            microcell_temp = self._microcell_temperature.getFixedTimeData(time_array)


        return { "time": time_array, "data" : data, "positions" : positions, "temperatures" : all_temperatures, "tallies" : tally_data, "microcell-temperature" : microcell_temp }



    def getEndingTime(self):

        return self._simulation_data.getEndingTime()


    def getInputFileData(self,input_file="input_file.inp"):

        input_file_path = self.getPath() + "/" + input_file

        radaii_command =   "cat '" + input_file_path + "' | perl -ne '/^Radaii:[\\s]+?([^#]+)[\\s]+?.*$/ && print $1'"
        material_command = "cat '" + input_file_path +  "' | perl -ne '/^Materials:[\\s]+?([^#]+)[\\s]+?.*$/ && print $1'"

        radaii = os.popen(radaii_command).read().split()
        materials = os.popen(material_command).read().split()

        radaii = [ float(radius) for radius in radaii ]

        return { "materials" : materials, "radaii" : radaii }




    def getFileData(self, csv_file ):

        output = []

        with open( csv_file, 'r') as csv_file_object:

            csv_data = csv.DictReader(csv_file_object, delimiter=',' )


            for row in csv_data:

                output.append(row)

        return output
