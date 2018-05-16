from pylab import *
from scipy import interpolate
import re
import os
import numpy
import sqlite3
import csv


class CSVDataObject(object):

    """
    :type keys: list[str]
    :type csv_data: list[ { str:str  } ]
    """

    def __init__(self, csv_data ):

        row = csv_data[0]
        self.keys = [ key for key in row ]
        self.csv_data = csv_data

    def getColumnData(self, column):

        data_list = []

        for row in self.csv_data:

            data = row[column]
            data_list.append(data)

        return data_list

class TimeBasedCSVDataObject(CSVDataObject):

    def __init__(self, csv_data, time_column ):

        super(TimeBasedCSVDataObject, self).__init__(csv_data)
        self.time_column = time_column

        self._interpolate_function = {}
        for column in self.keys:

            self._interpolate_function[column] = False

    def getInterpolatedDataTimeSeries(self, time_array, column):


        if self._interpolate_function[column] == False:

            raw_time, raw_value = self.getRawDataTimeSeries(column)

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

        time_array = self.getColumnData(self.time_column)
        return float(time_array[-1])

    def getFixedTimeData(self,time_array):

        return self.interpolatedData(time_array)

class SimulationResults(TimeBasedCSVDataObject):

    def __init__(self, csv_data, time):

        super(SimulationResults,self).__init__(csv_data,time)
        self.populateExtraFields()

    def populateExtraFields(self):

        integrated_power = 0
        power_column = "Power [W/m^3]"
        beta_column = "Beta_eff"
        beta_uncertainty_column = "Beta_eff sigma"
        k_eff_column = "k_eff"
        k_eff_sigma_column = "k_eff sigma"

        integrated_outward_power_key = "Integrated Outward Power [W*s/m^3]"
        instantaneous_power_key = 'Current Power Out [W/m^3]'

        last_time = 0
        row_index = 0
        row_length = len(self.csv_data)
        outward_power = 0

        last_power = float(self.csv_data[0][power_column])

        for row in self.csv_data:


            power = float(row[ power_column ])

            try:

                time = float(row[self.time_column])

            except:

                self.time_column = " " + self.time_column
                time = float(row[self.time_column])

            k_eff = float(row[k_eff_column])

            integrated_power = integrated_power + (time - last_time ) * (power + last_power) / 2
            row['Integrated Power [J/m^3]'] = integrated_power

            reactivity = ( k_eff - 1.0 ) / k_eff
            row['Reactivity [pcm]'] = reactivity * 10000

            k_eff_sigma = float(row[ k_eff_sigma_column ])




            if integrated_outward_power_key in row and not instantaneous_power_key in row:

                if row_index >= 1:

                    current_outward_integrated_power = float(row[integrated_outward_power_key])
                    last_outward_integrated_power = float(self.csv_data[row_index - 1][integrated_outward_power_key])


                    outward_power = (current_outward_integrated_power - last_outward_integrated_power)/(time - last_time)

                else:

                    outward_power =power

                row[instantaneous_power_key] = outward_power






            #reactivity_sigma = abs(reactivity) * ( abs(k_eff_sigma/(k_eff-1))  + abs(k_eff_sigma / k_eff))
            #row["Reactiviy Sigma [pcm]"] = reactivity_sigma * 10000

            beta = float(row[beta_column])
            reactivity_dollars = reactivity / beta
            row['Reactivity [$]'] = reactivity_dollars

            beta_sigma = float(row[beta_uncertainty_column])
            #reactivity_dollars_sigma = abs( reactivity_dollars ) * (abs( beta_sigma / beta) + abs( reactivity_sigma / reactivity ))
            #row['Reactivity Sigma [$]'] = reactivity_dollars_sigma
            last_power = power
            last_time = time

            row_index += 1

        for row in self.csv_data:

            if  instantaneous_power_key in row:
                row["Power Difference [W/m^3]"] = float(row[power_column]) - float(row[instantaneous_power_key])

class TemperatureData(TimeBasedCSVDataObject):

    def getFixedTimeData(self,time_array):

        data = super(TemperatureData,self).getFixedTimeData(time_array)

        ordered_keys_dict = {}
        ordered_keys_list = []


        for key in data:

            if key == self.time_column or key == '':

                continue

            try:

                float_key = float(key)
                ordered_keys_dict[float_key] = key
                ordered_keys_list.append(float_key)

            except:

                pass

            finally:

                positions = sort(ordered_keys_list)

        all_temperatures = []

        for index in range(0, len(time_array) ):

            spatial_temperature_values_at_time = []

            for position in positions:

                spatial_temperature_values_at_time.append(data[ordered_keys_dict[position]][index])
                #print str(time_array[index]) + " time " + ordered_keys_dict[key] + " location " + str(data[ordered_keys_dict[key]][index])

            all_temperatures.append(spatial_temperature_values_at_time)

        return [ positions, all_temperatures ]

    def getTemperatureExtremes(self):

        max_temperature = -1
        min_temperature = 1e100

        for time_data in self.csv_data:

            for key in time_data:

                if key != 'Time [s]' and key != "" and key != " ":

                    try:

                        temperature = float(time_data[key])

                    except:

                        temperature  = 800

                        print(key, time_data[key])

                    if  temperature > max_temperature:

                        max_temperature = temperature

                    if temperature < min_temperature:

                        min_temperature = temperature

        return [ min_temperature, max_temperature ]