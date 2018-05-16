import os
import re
import numpy
import matplotlib.pyplot as pyplot
import math
import Result
import time
import csv
import CSVClasses
import matplotlib.patches as patches
import matplotlib as mpl

mpl.rcParams['xtick.labelsize'] = 16
mpl.rcParams['ytick.labelsize'] = 16

class ResultsList(object):
    """
    :type _results: list[TransientResult.TransientResult]
    """

    def __init__(self, output_directory, run_name, label_regex="", label_format=""):

        self._results = []
        self._output_directory = output_directory
        self._run_name = run_name
        self._label_regex = label_regex
        self._label_formal = label_format

        if not os.path.exists(self._output_directory):
            os.makedirs(self._output_directory)

        self._label_font_size = 17
        self._title_font_size = 18
        self._legend_font_size = 14
        self._line_width = 3
        self._colors = ['blue', 'red', 'green', 'purple', 'orange', 'black', '#888800', '#555555', '#ff00ff', '#00ffff']
        self._labels = {}
        self._line_styles = ['-' , '--' , ':' , '-.' , 'steps' ]
        self._ordered_labels = []
        self._min_temperature = 1e100
        self._max_temperature = -1
        self._resonance_data_object = False
        self._data = []

    def addResult(self, result):

        if not isinstance(result, Result.Result):
            raise Exception("Result isn't an intance of TransientResult")

        [ min_result_temperature, max_result_temperature  ] = result.getTemperatureExtremes()

        if max_result_temperature > self._max_temperature:

            self._max_temperature = max_result_temperature

        if min_result_temperature < self._min_temperature:

            self._min_temperature = min_result_temperature

        self._results.append(result)



        folder_name = result.getFolderName()
        pattern = re.compile(self._label_regex)
        match = re.search(pattern, folder_name)
        data = match.group(1)

        self._data.append(data)

        if( callable( self._label_formal) ):

            value = self._label_formal(data)

        else:

            value = self._label_formal.replace("$1", data)

        self._labels[folder_name] = value
        self._ordered_labels.append(folder_name)

    def getLastEndingTime(self):

        ending_times = []

        for result in self._results:
            ending_times.append(result.getEndingTime())

        latest_ending_time = max(ending_times)

        return latest_ending_time

    def syncResultsTiming(self, divisions, time_axis, log_start_time=0.001, sync_tally=True):

        ending_time = self.getLastEndingTime()

        if time_axis == "log":

            time_array = numpy.logspace(numpy.log10(log_start_time), numpy.log10(ending_time), divisions)

        else:

            time_array = numpy.linspace(0, ending_time, divisions)

        synced_data = {}

        for result in self._results:
            name = result.getFolderName()
            data = result.getFixedTimeData(time_array, sync_tally=sync_tally)
            synced_data[name] = data

        synced_data["time"] = time_array

        return synced_data

    def syncResultsTimingSingle(self, time, start_time = 0.001):

        time_array = [start_time, time]

        synced_data = {}

        for result in self._results:
            name = result.getFolderName()
            data = result.getFixedTimeData(time_array)
            synced_data[name] = data

        synced_data["time"] = time_array

        return synced_data

    def getTemperatureExtremes(self, synced_data):

        max_temperature = math.ceil(self._max_temperature / 100) * 100
        min_temperature = math.floor(self._min_temperature / 100) * 100

        return [min_temperature, max_temperature]

    def plotResonanceEnergies(self, axis, isotopes = [ "U-235", "U-238" ], resonance_types = [ "fission", "capture", "absorption"], enrichment = 0.15 ):

        enrichment_percent = enrichment * 100

        if self._resonance_data_object == False:

            resonance_data = []

            with open("resonance.csv", 'r') as csv_file_object:

                csv_data = csv.DictReader(csv_file_object, delimiter=',')

                for row in csv_data:
                    resonance_data.append(row)


            self._resonance_data_object = CSVClasses.CSVDataObject(resonance_data)

        energies_raw = self._resonance_data_object.getColumnData("Energy [eV]")
        energies = [float(energy) / 1e6 for energy in energies_raw]

        ax2 = axis.twinx()

        if "W" in isotopes:

            w_resonance_data = []

            with open("tungsten-resonance.csv", 'r') as csv_file_object:

                csv_data = csv.DictReader(csv_file_object, delimiter=',')

                for row in csv_data:
                    w_resonance_data.append(row)

            tugsten_resonance_data_object = CSVClasses.CSVDataObject(w_resonance_data)
            cs_raw = tugsten_resonance_data_object.getColumnData("W Capture [b]")
            cross_sections = [float(cross_section) for cross_section in cs_raw]

            w_energies_raw = tugsten_resonance_data_object.getColumnData("Energy [eV]")
            w_energies = [float(energy) / 1e6 for energy in w_energies_raw]

            ax2.plot(w_energies, cross_sections, label="W Capture", color='#990000')

        if "U-238" in isotopes:

            if 'capture' in resonance_types:

                cs_raw = self._resonance_data_object.getColumnData("U-238 Capture [b]")
                cross_sections = [ float(cross_section)  for cross_section in cs_raw]

                ax2.plot(energies, cross_sections, label="U-238 Capture", color='orange')

            if 'absorption' in resonance_types:

                cs_raw = self._resonance_data_object.getColumnData("U-238 Capture [b]")
                cross_sections = [ float(cross_section)  for cross_section in cs_raw]

                ax2.plot(energies, cross_sections, label="U-238 Absorption", color='orange')

        if "U-235" in isotopes:

            if 'capture' in resonance_types:

                cs_raw = self._resonance_data_object.getColumnData("U-235 Capture [b]")
                cross_sections = [float(cross_section) for cross_section in cs_raw]

                ax2.plot(energies, cross_sections, label="U-235 Capture", color='orange')

            if 'fission' in resonance_types:

                cs_raw = self._resonance_data_object.getColumnData("U-235 Fission [b]")
                cross_sections = [float(cross_section) for cross_section in cs_raw]

                ax2.plot(energies, cross_sections, label="U-235 Fission", color='#CC511E')

            if 'absorption' in resonance_types:

                abs_cs_raw = self._resonance_data_object.getColumnData("U-235 Capture [b]")
                fission_cs_raw = self._resonance_data_object.getColumnData("U-235 Fission [b]")

                cross_sections = [float(absorption) + float(fission) for fission,absorption in zip(fission_cs_raw, abs_cs_raw) ]

                ax2.plot(energies, cross_sections, label="U-235 Absorption", color='orange')

        if "U" in isotopes:

            if 'capture' in resonance_types:
                abs_cs_raw_235 = self._resonance_data_object.getColumnData("U-235 Capture [b]")
                abs_cs_raw_238 = self._resonance_data_object.getColumnData("U-238 Capture [b]")

                cross_sections = [
                    enrichment * (float(capture_235) ) + (1 - enrichment) * float(capture_238) for
                    capture_235, capture_238 in zip( abs_cs_raw_235, abs_cs_raw_238)]

                ax2.plot(energies, cross_sections, label="U Capture " + str(enrichment_percent) + "% Enrich" , color='orange')

            if 'fission' in resonance_types:

                cs_raw = self._resonance_data_object.getColumnData("U-235 Fission [b]")
                cross_sections = [float(cross_section) for cross_section in cs_raw]

                ax2.plot(energies, cross_sections, label="U Fission", color='#CC511E')

            if 'absorption' in resonance_types:

                abs_cs_raw_235 = self._resonance_data_object.getColumnData("U-235 Capture [b]")
                fission_cs_raw_235 = self._resonance_data_object.getColumnData("U-235 Fission [b]")
                abs_cs_raw_238 = self._resonance_data_object.getColumnData("U-238 Capture [b]")

                cross_sections = [ enrichment * (float(capture_235) + float(fission_235)) + (1 - enrichment) * float(capture_238) for fission_235,capture_235, capture_238 in zip(fission_cs_raw_235, abs_cs_raw_235, abs_cs_raw_238) ]


                ax2.plot(energies, cross_sections, label="U Absorption " + str(enrichment_percent) + "% Enrich", color='orange')



        ax2.set_xlim([10 ** -9, 10])
        ax2.set_ylim([10 ** -3, 10**4])
        ax2.set_ylabel("Cross Section [b]", fontsize=self._label_font_size)
        ax2.set_yscale('log')
        ax2.legend(loc=1, fontsize=self._legend_font_size)
        return ax2

    def plotBasicTemperatureAverages(self, time_axis="log", log_start_time=0.001, uncertainty=False,ending_time=-1):


        fig = pyplot.figure(figsize=(7.58, 4.40))
        ax = fig.add_subplot(111)

        ax.plot([0,0],[0,0],color="red",label="Fuel")
        ax.plot([0, 0], [0, 0], color="blue", label="Moderator")

        ortensi_time_fuel =  [0.0496122262773723,0.0860678441084463,0.118339040431149,0.141081371852769,0.163830492030037,0.191026247156906,0.222722947278560,0.263435114901084,0.299490196148911,0.403086607341125,0.425645642360242,0.461917963788814,0.498237806506923,0.552907655742237,0.593993204925414,0.654099294833548,0.740934268330245,0.882581654930871,1.03328524156626,1.19312649330418,1.36662672140637,1.53554453944599,1.79115476711370,2.01478316692253,2.29312893725621,2.66726404978662,2.88171405195903,3.16913638859441,3.73027456421137,4.31422295880644,4.65636266596667,4.98027456421137]
        ortensi_temp_fuel =  [812.500000000000, 816.964285714286, 824.303154566570, 831.743630757046, 838.440059328475, 857.785297423713, 883.826964090380, 921.773392661808, 970.136487899903, 1115.96982123324, 1143.49958313800, 1168.05315456657, 1187.39839266181, 1195.58291647133, 1192.60672599514, 1182.13206934027, 1165.01897410217, 1140.46540267360, 1123.35230743550, 1104.75111695931, 1089.12611695931, 1075.73325981646, 1060.85230743550, 1051.17968838788, 1044.48325981646, 1039.27492648312, 1035.55468838788, 1034.06659314979, 1033.32254553074, 1032.57849791169, 1034.06659314979, 1033.32254553074]
        ortensi_time_mod =   [0, 0.0634137665102537,0.204803180396246,0.282310403632256,0.355242005561349,0.419015576120959,0.491892868004866,0.573901036235662,0.674143802137643,0.824541894768856,0.952156923444560,1.09803370481404,1.30773836678832,1.53115631517205,1.73179798835593,1.97806009949600,2.22889783194300,2.49342169577685,2.81726570646507,3.34638132168926,3.97586190041710,4.63273510818561,4.98854736922141]
        ortensi_temp_mod =   [799.851190476191,799.851190476191,803.571428571429,808.779761904762,815.476190476190,825.892857142857,838.541666666667,850.446428571429,863.839285714286,880.208333333333,893.601190476191,905.505952380952,921.875000000000,935.267857142857,944.940476190476,954.613095238095,962.797619047619,970.982142857143,977.678571428571,986.607142857143,995.535714285714,1002.23214285714,1005.20833333333]

        ax.plot(ortensi_time_mod, ortensi_temp_mod, color="#98ca3a", linewidth=2, label="Ortensi Moderator")
        ax.plot(ortensi_time_fuel, ortensi_temp_fuel, linewidth=2,color="green", label="Ortensi Fuel")
        ax.legend()

        [max_time, min_value, max_value] = self.graphAttribute(ax, 0, "Moderator Temp [K]", time_axis,
                                                               'linear', log_start_time=log_start_time,
                                                               ending_time=ending_time)

        [max_time, min_value, max_value] = self.graphAttribute(ax, 0, "Fuel Temp [K]", time_axis,
                                                               'linear', log_start_time=log_start_time,
                                                                ending_time=ending_time, color_override='red')


        ax.set_ylim([750, 1250])
        fig2 = pyplot.figure(figsize=(7.58, 4.40))
        power_ax = fig2.add_subplot(211)
        [max_time, min_value, max_value] = self.graphAttribute(power_ax, 0, "Power [W/m^3]", time_axis,
                                                               'linear', log_start_time=log_start_time,
                                                               nominalized=True, ending_time=ending_time)
        power_ax.set_ylabel("Relative Power")
        power_ax = fig2.add_subplot(212)
        [max_time, min_value, max_value] = self.graphAttribute(power_ax, 0, "k-fixed", time_axis,
                                                               'linear', log_start_time=log_start_time,
                                                               nominalized=True, ending_time=ending_time)

        fig.tight_layout()
        pyplot.show()

    def plotInitialTemperatures(self, zone_shading=True,multiscale=False):

        synced_data = self.syncResultsTimingSingle(0, start_time=0)
        fig = pyplot.figure(figsize=(12,6))
        ax = fig.add_subplot(111)
        self.graphTemperature(ax, 0, synced_data, legend=True)

        if multiscale:
            ax.legend(loc=2)
            self.graphTemperature(ax, 0, synced_data, type="fuel")
            #y1, y2 = ax.get_ylim()

            ax.set_ylim([800, 1200])

        figure_path = self._output_directory + self._run_name + "-Initial-Temperature-View.png"

        data = self._results[0].getInputFileData()

        zone_color = ["#ffff00", "#000000", "#0000ff"]

        inner_radius = 0
        index = 0
        radius_match = (6/math.pi)**(1.0/3.0)
        max_radius = max(data['radaii'])*radius_match
        line = []

        for radius in data['radaii']:

            if not radius == data['radaii'][-1]:
                outer_radius = radius

            else:
                outer_radius = max_radius

            x_o = inner_radius * 100 / max_radius
            width = (outer_radius - inner_radius) * 100 / max_radius
            ax.add_patch(
                patches.Rectangle
                (
                    ( x_o, 0),  # (x,y)
                    width ,  # width
                    5000,  # height
                    alpha=0.25,
                    facecolor=zone_color[index]
                )
            )

            #label = data['material'][index]

            inner_radius = outer_radius
            index += 1

        #ax.legend(handles=line, loc=4)
        ax.set_xlim([0,100])
        fig.suptitle("Temperatures at Time = 0 seconds", fontsize=self._title_font_size)
        fig.savefig(figure_path)

    def standardEnergyView(self,time_step_divisions, time_axis="log", log_start_time=0.001, uncertainty=False,ending_time=-1):

        synced_data = self.syncResultsTiming(time_step_divisions, time_axis, log_start_time)

        time_list = synced_data["time"]

        # if we are in log time cut all times that are not in our log time axis view
        if time_axis == "log":

            time_list = [the_time for the_time in time_list if the_time >= log_start_time]

        [min_temperature, max_temperature] = self.getTemperatureExtremes(synced_data)

        flux_data = None

        for timestep_index in range(len(time_list)):

            current_time = time_list[timestep_index]


            fig = pyplot.figure(figsize=(19.2, 10.8))
            # Spectrum #################################################################################################
            #energy_ax = pyplot.subplot2grid((3, 2), (0, 0), colspan=1, rowspan=1)
            #self.graphEnergy(energy_ax, timestep_index, synced_data, marker="", uncertainty=uncertainty)
            #energy_ax.axis([10**-9, 10, 10**-1.5, 10])
            #pyplot.title("Center Fuel Flux Energy Shape", fontsize=self._title_font_size)


            #ax2 = self.plotResonanceEnergies(energy_ax, resonance_types=["capture", "fission"], isotopes=["U"])
            #y1, y2 = ax2.get_ylim()

            #ax2.set_ylim([y1 / 1000000, y2])

            #y1, y2 = energy_ax.get_ylim()

            #energy_ax.set_ylim([y1, y2 * 1.2])

            # Spectrum Shift ###########################################################################################
            #energy_ax = pyplot.subplot2grid((3, 2), (0, 1), colspan=1, rowspan=1)
            #self.graphEnergy(energy_ax, timestep_index, synced_data, initial_difference=True, marker="", uncertainty=uncertainty)
            #[min_diff, max_diff] = self.getMaxTallyDifferentialChange(synced_data)
            #energy_ax.axis([10 ** -9, 20, min_diff, max_diff])
            #pyplot.title("Center Fuel Flux Energy Shape Change", fontsize=self._title_font_size)
            # Fission Spectrum #########################################################################################
            energy_ax = pyplot.subplot2grid((3, 2), (0, 0), colspan=1, rowspan=1)
            [max_time, min_value, max_value] = self.graphAttribute(energy_ax, current_time, "k_eff", time_axis, "linear", plot_type="step", log_start_time=log_start_time,  ending_time=ending_time)
            pyplot.ylabel('k$_{eff*}$', fontsize=self._label_font_size + 3)
            energy_ax.grid(lw=1, which='minor', axis='x')

            #Legend
            legend_columns = 4
            legend_rows = math.ceil( float(len(self._results)) / legend_columns)
            legend_height = legend_rows * 0.08
            energy_ax.legend(bbox_to_anchor=(0, 1.08 + legend_height, 2.18, legend_height), loc=3, ncol=legend_columns,
                     mode="expand", borderaxespad=0., fontsize=self._label_font_size)

            energy_ax = pyplot.subplot2grid((3, 2), (0, 1), colspan=1, rowspan=1)
            self.graphEnergy(energy_ax, timestep_index, synced_data, type="Capture-Rate", marker="", uncertainty=uncertainty)
            pyplot.title("Capture Energy Distribution", fontsize=self._title_font_size)
            energy_ax.axis([10 ** -9, 10, 10 ** -2, 10])

            energy_ax = pyplot.subplot2grid((3, 2), (1, 0), colspan=1, rowspan=1)
            self.graphTemperatureAtPoint(energy_ax, synced_data, {75: "Matrix Temperature"}, time_axis, "linear",
                                         log_start_time=log_start_time, legend=False, timeline=current_time,
                                         ending_time=ending_time)
            pyplot.title("Mid-Matrix Temperature", fontsize=self._title_font_size)


            energy_ax = pyplot.subplot2grid((3, 2), (1, 1), colspan=1, rowspan=2)
            self.graphEnergy(energy_ax, timestep_index, synced_data, initial_difference=True, type="Capture-Rate", marker="", uncertainty=uncertainty)
            [min_diff, max_diff] = self.getMaxTallyDifferentialChange(synced_data,type="Capture-Rate")
            energy_ax.axis([10 ** -9, 10, min_diff, max_diff])
            pyplot.title("Capture Energy Shape Function Change", fontsize=self._title_font_size)

            # This plots cross sections over the plot
            # for item in ([energy_ax.title, energy_ax.xaxis.label, energy_ax.yaxis.label] + energy_ax.get_xticklabels() + energy_ax.get_yticklabels()):
            #    item.set_fontsize(20)
            ax2 = self.plotResonanceEnergies(energy_ax, resonance_types=["capture", 'fission'] , isotopes=["U"])
            y1, y2 = ax2.get_ylim()

            ax2.set_ylim([y1/1000000, y2])

            y1, y2 = energy_ax.get_ylim()

            energy_ax.set_ylim([y1, y2*1.5])

            # for item in ([ax2.title, energy_ax.xaxis.label, ax2.yaxis.label] + ax2.get_xticklabels() + ax2.get_yticklabels()):
            #   item.set_fontsize(20)

            #tally_ax = pyplot.subplot2grid((3, 2), (2, 0), colspan=1, rowspan=1)
            #flux_data = self.plotTallyZoneCellTallyData(tally_ax, time_list, timestep_index,  flux_data=flux_data, uncertainty=uncertainty)


            #pyplot.title("Flux Distribution", fontsize=self._title_font_size)

            temp_ax = pyplot.subplot2grid((3, 2), (2, 0), colspan=1, rowspan=1)
            self.graphTemperatureAtPoint(temp_ax, synced_data, { 15:"Fuel Temp" }, time_axis, "linear",
                                       log_start_time=log_start_time, legend=False, timeline=current_time, ending_time=ending_time)
            pyplot.title("Centerline Fuel Temperature", fontsize=self._title_font_size)



            fig.tight_layout()
            fig.subplots_adjust(top= (0.95 - legend_height) )

            fig.suptitle("Time = " + "%.3e s" % (current_time), fontsize=self._title_font_size)
            fig.savefig(self._output_directory + self._run_name + "-Energy-View-" + str(timestep_index).rjust(4, '0') + ".png")


            pyplot.close(fig)


        view_type = "Energy-View"
        animated_gif = self._run_name + "-" + view_type + ".gif"
        constituent_pngs = self._run_name + "-" + view_type + "-*.png"

        os.system("cd " + self._output_directory + ";convert -delay 40 -loop 0 " + constituent_pngs + " " + animated_gif)
        os.system("cd " + self._output_directory + ";rm " + constituent_pngs)

    def plotTallyZoneCellTallyDataAtPointVsTime(self,tally_ax, zone=1, cell=1, tally_type="Flux", time_axis = "log", yscale = "linear", legend = False, plot_type="line", log_start_time=0.001,  uncertainty=False, sigma_levels=[1],ending_time = -1):

        color_index = 0
        max_time = 0
        min_value = 100

        tally_ax.grid(lw=3)
        pyplot.xlabel('Time [s]', fontsize=self._label_font_size)
        pyplot.ylabel('Power Depression [%]', fontsize=self._label_font_size)

        tally_ax.set_xscale(time_axis)
        tally_ax.set_yscale(yscale)

        for result_index in range(len(self._results)):

            result = self._results[result_index]
            label = self._labels[result.getFolderName()]

            if result._tally_data:

                [ times, all_tally_values, all_tally_sigmas] = result._tally_data.getRelativeTallyTotals(type=tally_type)
                key = "%s-%g-%g" % (tally_type, zone, cell)

                if not key in all_tally_values:

                    key = " " + key

                all_tally_values[key] = [ 100*value for value in all_tally_values[key]]
                all_tally_sigmas[key] = [ 100*value for value in all_tally_sigmas[key]]



                if uncertainty:

                    [error_times, error_below, error_above] = self.getUncertainty(times, all_tally_values[key], all_tally_sigmas[key], plot_type, sigma_levels=sigma_levels)

                    for index in range(len(error_below)):
                        alpha = 0.3 - 0.2 * index / len(error_above)

                        tally_ax.fill_between(error_times, error_below[index], error_above[index],
                                                facecolor=self._colors[color_index % len(self._colors)],
                                                alpha=alpha, label=str(sigma_levels[index]) + " $\sigma$")

                        # some runs don't have tally energy data


                if plot_type == "step" :

                    tally_ax.step(times,all_tally_values[key], color=self._colors[color_index % len(self._colors)], lw=self._line_width,label=label, where="pre")

                else:

                    tally_ax.plot(times,all_tally_values[key], color=self._colors[color_index % len(self._colors)], lw=self._line_width,label=label )



                current_max_time = max(times)

                if(current_max_time > max_time):

                    max_time = current_max_time

                if plot_type == "step":

                    min_sigma_index = sigma_levels.index(max(sigma_levels))
                    current_min_value = min(error_below[min_sigma_index])

                else:

                    current_min_value = min(all_tally_values[key])

                if current_min_value < min_value:

                    min_value = current_min_value

            color_index += 1

        tally_ax.set_ylim([min_value, 100])

        upper_time_limit = max_time

        if ending_time > 0:

            upper_time_limit = ending_time

        tally_ax.set_xlim([log_start_time, upper_time_limit ])

    def plotTallyZoneCellTallyData(self,tally_ax, all_times, current_time_index, tally_type="Flux", flux_data = None, uncertainty=False, sigma_levels=[1,2]):

        color_index = 0
        global_min_tally = 1e100

        for result_index in range( len(self._results) ):

            result = self._results[result_index]
            tally_plot_sum_list = []
            tally_radaii = []
            tally_sigmas = []

            geometry = result.getInputFileData()

            if result._tally_data:

                #start_time = time.time()

                if flux_data is None:

                    flux_data = {}

                if not result_index in flux_data:

                    #create the keys for the flux fields we want only
                    desired_keys = []
                    for zone in range( 1, result._tally_data._number_zones + 1) :
                        for cell in range(1, result._tally_data._number_cells + 1):
                            desired_keys.append("%s-%g-%g" % (tally_type, zone, cell))


                    #Now grab the data
                    flux_data[result_index] = result._tally_data.getFixedTimeData(all_times,desired_keys)

                label = self._labels[result.getFolderName()]
                zone = 1

                last_radius = 0

                #print("A)  " + str(time.time() - start_time))
                #start_time = time.time()

                for radius in geometry["radaii"]:

                    for cell in range(1,result._tally_data._number_cells + 1):

                        key = "%s-%g-%g"%(tally_type,zone,cell)

                        if not key in flux_data[result_index]:
                            key = " " + key

                        if not key in flux_data[result_index]:
                            print("skipping " + key )
                            continue

                        tally_counts = flux_data[result_index][key ][1][current_time_index]
                        tally_uncertainties = flux_data[result_index][key][2][current_time_index]
                        tally_counts = [ float(datum) for datum in tally_counts ]

                        tally_sigma = sum([ (float(tally_uncertainty)*count)**2 for tally_uncertainty,count in zip(tally_uncertainties,tally_counts) ])**0.5

                        total_tally_counts = sum(tally_counts)
                        tally_radius = last_radius + ( radius - last_radius ) * (cell - 1) / result._tally_data._number_cells
                        tally_plot_sum_list.append(total_tally_counts)
                        tally_radaii.append(tally_radius)
                        tally_sigmas.append(tally_sigma)

                    zone += 1
                    last_radius = radius

                max_value = max(tally_plot_sum_list)
                tally_plot_sum_list = [ 100*value/max_value for value in tally_plot_sum_list]
                tally_sigmas = [100 * value / max_value for value in tally_sigmas]

                min_value = min(tally_plot_sum_list)

                if(min_value < global_min_tally):
                    global_min_tally = min_value

                max_radius = max(tally_radaii)

                if max_radius <= 0:
                    max_radius = 1

                tally_radaii = [ 100.0*radius/max_radius for radius in tally_radaii]


                if uncertainty:

                    [error_times, error_below, error_above] = self.getUncertainty(tally_radaii, tally_plot_sum_list,
                                                                                  tally_sigmas, "step",
                                                                                  sigma_levels=sigma_levels)

                    for index in range(len(error_below)):
                        alpha = 0.3 - 0.2 * index / len(error_above)

                        tally_ax.fill_between(error_times, error_below[index], error_above[index],
                                              facecolor=self._colors[color_index % len(self._colors)],
                                              alpha=alpha, label=str(sigma_levels[index]) + " $\sigma$")

                        # some runs don't have tally energy data




                tally_ax.step(tally_radaii, tally_plot_sum_list, color=self._colors[color_index % len(self._colors)], lw=self._line_width, label=label, where="pre")



            color_index += 1


        tally_ax.grid(lw=3, which='major')
        tally_ax.set_ylabel("%s Depression [%%]" % (tally_type), fontsize=self._label_font_size)
        tally_ax.set_xlabel("Radius [%]", fontsize=self._label_font_size)
        tally_ax.set_xlim([0, 100])
        y_range = (100 - global_min_tally)

        if y_range == 0:
           y_range = 10

        power = math.ceil(math.log(y_range,5))
        min_value = 100 - 5**power

        tally_ax.set_ylim([min_value,  100])

        return flux_data

    def plotDelayedPrecursors(self, time_axis="log", log_start_time=0.001,reposition=False,ending_time=-1):

        fig = pyplot.figure(figsize=(10, 7))
        delayed_ax = fig.add_subplot(111)

        actual_min = 1e100
        actual_max = 0

        for delayed_index in range(1, 7):
            color_override = self._colors[delayed_index]
            delayed_ax.plot([0,0],[0,0],color=color_override,label="Group " + str(delayed_index))

        pyplot.legend(loc=2, fontsize=self._legend_font_size)

        for delayed_index in range(1,7):



            color_override = self._colors[delayed_index]

            [max_time, min_value, max_value] = self.graphAttribute(delayed_ax, 0, "Group " + str(delayed_index), time_axis,
                                                                   'log', log_start_time=log_start_time,
                                                                    ending_time=ending_time, color_override=color_override, pattern=True)

            if min_value < actual_min:
                actual_min = min_value

            if max_value > actual_max:
                actual_max = max_value



        actual_min = 10**math.floor( math.log10(actual_min))
        actual_max = 10 ** math.ceil(math.log10(actual_max))
        delayed_ax.set_ylim([actual_min, actual_max])
        delayed_ax.set_ylabel("Delayed Precursors")
        if reposition:
            pyplot.show()

        figure_path = self._output_directory + self._run_name + "-Delayed-Precursors.png"
        fig.savefig(figure_path)
        pyplot.close(fig)

    def stillViewSingle(self, time_axis="log", log_start_time=0.001, temperature_graph_positions={ 0 : "Center Kernel" , 20 : "Outer Kernel", 100 : "Outer Matrix" }, reposition=False, power_scale="log", time_comparison = 1.9, ending_time=-1):

        fig = pyplot.figure(figsize=(15, 28))
        figure_rows = 4
        fig.subplots_adjust(hspace=0.3, wspace=3)

        power_ax = pyplot.subplot2grid((figure_rows, 1), (0, 0), colspan=1, rowspan=1)
        [max_time, min_value, max_value] = self.graphAttribute(power_ax, 0, "Power [W/m^3]", time_axis,
                                                               power_scale, log_start_time=log_start_time,  nominalized=True, ending_time=ending_time)
        power_ax.set_ylabel("Relative Power [W/W]")

        legend_columns = 4

        legend_height = (math.ceil(len(self._results) / legend_columns)) * 0.12
        power_ax.legend( bbox_to_anchor=(0., 1.12 + legend_height, 1., legend_height), loc=3,ncol=legend_columns, mode="expand", borderaxespad=0., fontsize=self._label_font_size )

        power_ax.grid(lw=1, which='minor', axis='both')

        reactivity_ax = pyplot.subplot2grid((figure_rows, 1), (1, 0), colspan=4, rowspan=1)
        [max_time, min_value, max_value] = self.graphAttribute(reactivity_ax, 0, "k_eff", time_axis,
                                                               "linear", plot_type="step",
                                                               log_start_time=log_start_time, ending_time=ending_time)
        pyplot.ylabel('k$_{eff*}$', fontsize=self._label_font_size + 3)
        reactivity_ax.grid(lw=1, which='minor', axis='x')

        integrated_ax = pyplot.subplot2grid((figure_rows, 1), (2, 0), colspan=4, rowspan=1)
        [max_time, min_value, max_value] = self.graphAttribute(integrated_ax, 0,
                                                               "Integrated Power [J/m^3]", time_axis, "log",
                                                               log_start_time=log_start_time, ending_time=ending_time)


        integrated_ax.set_ylim([2*10 ** 7, max_value])

        integrated_ax.grid(lw=1, which='minor', axis='x')

        temp_ax = pyplot.subplot2grid((figure_rows, 1), (3, 0), colspan=2, rowspan=4)

        temperature_synced_data = self.syncResultsTiming(100, time_axis, log_start_time, sync_tally=False)
        self.graphTemperatureAtPoint(temp_ax, temperature_synced_data, temperature_graph_positions, time_axis,"linear", log_start_time=log_start_time,legend=True, ending_time=ending_time )



        figure_path = self._output_directory + self._run_name + "-Still-View.png"
        fig.suptitle(self._run_name, fontsize=self._label_font_size)

        if reposition:
            pyplot.show()

        fig.tight_layout()
        fig.subplots_adjust(top=(0.90 - float(legend_height) / figure_rows))

        fig.savefig(figure_path)
        pyplot.close(fig)

    def stillViewMultipleGraphs(self, time_axis="log", log_start_time=0.001, temperature_graph_positions={ 0 : "Center Kernel" , 20 : "Outer Kernel", 100 : "Outer Matrix" }, reposition=False, time_base="seconds", power_scale="log", time_comparison = 1.9, ending_time=-1):

        width_graphs = 15
        height_graphs =  int(4 + ( math.floor( ( len(temperature_graph_positions) -1) /width_graphs)))

        fig = pyplot.figure(figsize=(14, 4 * height_graphs ))
        fig.subplots_adjust(hspace=0.3, wspace=3)

        power_ax = pyplot.subplot2grid((height_graphs, width_graphs), (0, 0), colspan=width_graphs, rowspan=1)
        [max_time, min_value, max_value] = self.graphAttribute(power_ax, 0, "Power [W/m^3]", time_axis,
                                                               power_scale, log_start_time=log_start_time, nominalized=True, time_base=time_base, ending_time=ending_time)
        power_ax.set_ylabel("Relative Power [W/W]")

        legend_columns = 4
        legend_height = ( math.ceil(len(self._results) / legend_columns)) * 0.08
        power_ax.legend( bbox_to_anchor=(0., 1.12 + legend_height , 1., legend_height), loc=3,ncol=legend_columns, mode="expand", borderaxespad=0., fontsize=self._label_font_size )

        power_ax.grid(lw=1, which='minor', axis='both')

        reactivity_ax = pyplot.subplot2grid((height_graphs, width_graphs), (1, 0), colspan=width_graphs, rowspan=1)
        [max_time, min_value, max_value] = self.graphAttribute(reactivity_ax, 0, "k_eff", time_axis,
                                                               "linear", plot_type="step",
                                                               log_start_time=log_start_time, time_base=time_base, ending_time=ending_time, uncertainty_column="k_eff sigma")

        pyplot.ylabel('k$_{eff*}$', fontsize=self._label_font_size + 3)
        reactivity_ax.grid(lw=1, which='minor', axis='x')

        integrated_ax = pyplot.subplot2grid((height_graphs, width_graphs), (2, 0), colspan=width_graphs, rowspan=1)
        [max_time, min_value, max_value] = self.graphAttribute(integrated_ax, 0,
                                                               "Integrated Power [J/m^3]", time_axis, "log",
                                                               log_start_time=log_start_time, time_base=time_base, ending_time=ending_time)

        integrated_ax.set_ylim([2*10 ** 7, max_value])

        integrated_ax.grid(lw=1, which='minor', axis='x')

        index = 0

        temperature_synced_data = self.syncResultsTiming(100, time_axis, log_start_time, sync_tally=False)

        keys = [float(key) for key in temperature_graph_positions.keys() ]

        keys = sorted(keys)

        for key in keys:

            width_increment = int(math.floor(width_graphs/3))
            xpos = index % width_graphs
            ypos =  3 + int(math.floor(index / width_graphs))
            temp_ax = pyplot.subplot2grid((height_graphs, width_graphs), ( ypos  , xpos ), colspan=width_increment, rowspan=1)
            self.graphTemperatureAtPoint(temp_ax, temperature_synced_data, { key : temperature_graph_positions[key] }, time_axis,"linear", log_start_time=log_start_time,legend=True, time_base=time_base, ending_time=ending_time )
            index += width_increment

        figure_path = self._output_directory + self._run_name + "-Still-View-Multiple.png"
        #fig.suptitle(self._run_name, fontsize=self._label_font_size)

        if reposition:
            pyplot.show()

        fig.tight_layout()
        fig.subplots_adjust(top=(0.94 - float(legend_height)) )
        fig.savefig(figure_path)
        pyplot.close(fig)

    def boundaryHeatFluxPlot(self, time_axis="log", log_start_time=0.001, reposition=False, ending_time=-1):


        fig = pyplot.figure(figsize=(15,15))
        ax = fig.add_subplot(311)

        [max_time, min_value, max_value] = self.graphAttribute(ax, 0, "Integrated Outward Power [W*s/m^3]", time_axis,
                                                               "linear", log_start_time=log_start_time, ending_time=ending_time)
        ax.grid(lw=1, which='minor', axis='both')

        legend_columns = 4
        legend_rows = math.ceil(float(len(self._results)) / legend_columns)
        legend_height = legend_rows * 0.08
        ax.legend(bbox_to_anchor=(0, 1.08 + legend_height, 1, legend_height), loc=3, ncol=legend_columns,
                         mode="expand", borderaxespad=0., fontsize=self._label_font_size)


        ax.set_ylabel('Integrated Power', fontsize=self._label_font_size)
        ax.grid(lw=3, which='major', axis="y")
        ax.grid(lw=1, which='minor', axis='y')
        pyplot.xticks(rotation=60)

        fig.suptitle("Heat Flux Study", fontsize=self._label_font_size + 3)


        ax = fig.add_subplot(312)


        ax.plot([0, 0], [0, 0], color='black', lw=3, label="Power Generated")
        ax.plot([0, 0], [0, 0], color='black', linestyle="--", lw=4, label="Power Escaping")

        ax.legend(loc=2)


        [max_time, min_value_power, max_value_power] = self.graphAttribute(ax, 0, "Power [W/m^3]", time_axis,
                                                               "linear", log_start_time=log_start_time, ending_time=ending_time)


        [max_time, min_value_power_out, max_value_power_out] = self.graphAttribute(ax, 0, "Current Power Out [W/m^3]", time_axis,
                                                               "linear", log_start_time=log_start_time,
                                                               ending_time=ending_time, linetype='--', linewidth="4")
        min_val =  min([min_value_power_out,min_value_power])
        max_val =  max([max_value_power, max_value_power_out])
        val_range = max_val - min_val

        ax.set_ylim([ min_val - 0.2 * val_range, max_val + 0.2 * val_range ])



        ax = fig.add_subplot(313)
        [max_time, min_value, max_value] = self.graphAttribute(ax, 0, "Power Difference [W/m^3]", time_axis,
                                                               "linear", log_start_time=log_start_time,
                                                               ending_time=ending_time, )


        fig.tight_layout()
        fig.subplots_adjust(top=(0.92 - float(legend_height) / 3))
        fig.savefig(self._output_directory + self._run_name + "-Boundary-Heat-Flux.png")

    '''def plotMicroCellAtTime(self, temp_ax, timestep_index, synced_data, legend = False):

        temp_ax.grid(lw=3)
        pyplot.xlabel('Radius[%]', fontsize=self._label_font_size)
        pyplot.ylabel('Temperature [K]', fontsize=self._label_font_size)

        [positions, temperatures] = self.getTemperatureGraphData(synced_data, timestep_index)

        color_index = 0

        for run in self._ordered_labels:


            temp_ax.plot(positions[run], temperatures[run], color=self._colors[color_index % len(self._colors)],
                         lw=self._line_width, label=self._labels[run])
        color_index += 1

        if legend:
            temp_ax.legend(loc=1, ncol=1, fontsize=self._legend_font_size)

    def getTemperatureGraphData(self, synced_data, time_index):

        positions = {}
        temperatures = {}

        for run_name in self._labels:

            if run_name == 'time':
                continue

            # A homogenous case with only one point
            if (len(synced_data[run_name]['positions']) == 1):
                positions[run_name] = [0, 100]
                temperature = synced_data[run_name]['temperatures'][time_index][0]
                temperatures[run_name] = [temperature, temperature]

            # Many points with temperatures
            else:
                max_position = max(synced_data[run_name]['positions'])
                relative_positions = [100.0 * position / max_position for position in
                                      synced_data[run_name]['positions']]

                positions[run_name] = relative_positions

                number_timesteps_in_run = len(synced_data[run_name]['time'])

                if number_timesteps_in_run > time_index + 1:

                    temperatures[run_name] = synced_data[run_name]['temperatures'][time_index]

                else:

                    temperatures[run_name] = (synced_data[run_name]['temperatures'][-1])

                    # This fixes the problem with homogenous plots

                return [positions, temperatures]



            index = 0

            time_data = run._microcell_temperature.getColumnData("Time [s]")
            position_key = 'Position-' + str(index) + " [m]"
            temperature_key = 'Temperature-' + str(index) + " [K]"
            integrated_power_key = 'Integrated-Power-' + str(index) + " [W-s]"
            current_power_key = 'Current-Power-' + str(index) + " [W]"

            while position_key in run._microcell_temperature.keys:

                position = run._microcell_temperature.getColumnData(position_key)
                temperature = run._microcell_temperature.getColumnData(temperature_key)
                current_power = run._microcell_temperature.getColumnData(current_power_key)
                integrated_power = run._microcell_temperature.getColumnData(integrated_power_key)


                ax.plot(time_data,temperature,label='Cell '+ str(index))



                index += 1

                time_data = run._microcell_temperature.getColumnData("Time [s]")
                position_key = 'Position-' + str(index) + " [m]"
                temperature_key = 'Temperature-' + str(index) + " [K]"
                integrated_power_key = 'Integrated-Power-' + str(index) + " [W-s]"
                current_power_key = 'Current-Power-' + str(index) + " [W]"

        '''

    def stillViewAbsorption(self,time_axis="log", log_start_time=0.001, reposition=False,prompt_neutron_lifetime_axis="linear", time_comparison = 1.9):

        fig = pyplot.figure(figsize=(14, 40))

        figure_rows = 8

        fig.subplots_adjust(hspace=0.3, wspace=0.4)

        synced_data = self.syncResultsTimingSingle(time_comparison)

        #flux and flux change
        synced_data = self.syncResultsTimingSingle(time_comparison)
        energy_ax = pyplot.subplot2grid((figure_rows, 2), (0, 0), colspan=2, rowspan=1)
        [min_bin_energy, max_bin_energy, min_bin_value, max_bin_value] = self.graphEnergy(energy_ax, 1, synced_data,
                                                                                          marker="", uncertainty=True)
        # energy_ax.set_ylim([10**-2, 10**-1])

        pyplot.title("Spectrum at time = " + str(time_comparison), fontsize=self._title_font_size)
        energy_ax.grid(lw=1, which='minor', axis='both')

        legend_columns = 4
        legend_height = (math.ceil(len(self._results) / legend_columns)) * 0.4
        energy_ax.legend(bbox_to_anchor=(0., 1.12 + legend_height, 1., legend_height), loc=3, ncol=legend_columns,
                         mode="expand",
                         borderaxespad=0., fontsize=self._label_font_size)

        energy_ax = pyplot.subplot2grid((figure_rows, 2), (1, 0), colspan=2, rowspan=1)
        self.graphEnergy(energy_ax, 1, synced_data, initial_difference=True, marker="", uncertainty=True)
        [min_diff, max_diff] = self.getMaxTallyDifferentialChange(synced_data)
        energy_ax.set_xlim([10 ** -9, 10])
        [min_val, max_val] = energy_ax.get_ylim()
        energy_ax.set_ylim([min_val, max_val * 5])

        self.plotResonanceEnergies(energy_ax, resonance_types=["absorption"], isotopes=["U"])
        # self.plotResonanceEnergies(energy_ax, isotopes = [ "U-238"])
        pyplot.title("Flux Shape Shift in Kernel from time = 0 to " + str(time_comparison) + " seconds",
                     fontsize=self._title_font_size)
        energy_ax.grid(lw=1, which='minor', axis='both')



        # Capture and Capture Change
        energy_ax = pyplot.subplot2grid((figure_rows, 2), (2, 0), colspan=2, rowspan=1)
        [min_bin_energy, max_bin_energy, min_bin_value, max_bin_value] = self.graphEnergy(energy_ax, 1, synced_data,
                                                                                          marker="", uncertainty=True, type="Absorption-Rate")
        energy_ax.set_ylim([10**-2.5, 10**2])

        pyplot.title("Absorption Spectrum at time = " + str(time_comparison), fontsize=self._title_font_size)
        energy_ax.grid(lw=1, which='minor', axis='both')


        energy_ax = pyplot.subplot2grid((figure_rows, 2), (3, 0), colspan=2, rowspan=1)
        self.graphEnergy(energy_ax, 1, synced_data, initial_difference=True, marker="", uncertainty=True, type="Absorption-Rate")
        [min_diff, max_diff] = self.getMaxTallyDifferentialChange(synced_data)
        energy_ax.set_xlim([10 ** -9, 10])
        [min_val, max_val] = energy_ax.get_ylim()
        energy_ax.set_ylim([min_val, 1.3 ])

        self.plotResonanceEnergies(energy_ax, resonance_types = [ "absorption" ], isotopes = ["U"])
        pyplot.title("Absorption Shape Shift in Kernel from time = 0 to " + str(time_comparison) + " seconds",
                     fontsize=self._title_font_size)
        energy_ax.grid(lw=1, which='minor', axis='both')



        # Fission and Fission Change ###################################################################################
        energy_ax = pyplot.subplot2grid((figure_rows, 2), (4, 0), colspan=2, rowspan=1)
        [min_bin_energy, max_bin_energy, min_bin_value, max_bin_value] = self.graphEnergy(energy_ax, 1, synced_data,
                                                                                          marker="", uncertainty=True,
                                                                                          type="Fission")
        energy_ax.set_ylim([10 ** -2, 10 ** 1])
        pyplot.title("Fission Neutron Spectrum at time = " + str(time_comparison) + " Seconds",
                     fontsize=self._title_font_size)
        energy_ax.grid(lw=1, which='minor', axis='both')

        energy_ax = pyplot.subplot2grid((figure_rows, 2), (5, 0), colspan=2, rowspan=1)
        ax2 = self.plotResonanceEnergies(energy_ax, isotopes=["U-235"], resonance_types=["fission"])
        y1, y2 = ax2.get_ylim()
        ax2.set_ylim([y1 / 100, y2])

        self.graphEnergy(energy_ax, 1, synced_data, initial_difference=True, marker="", uncertainty=True,
                         type="Fission")
        # [min_diff, max_diff] = self.getMaxTallyDifferentialChange(synced_data)
        energy_ax.set_xlim([10 ** -9, 10])
        [min_val, max_val] =energy_ax.get_ylim()
        energy_ax.set_ylim([min_val, max_val*1.2])

        pyplot.title("Fission Energy Shape Function Shift from time = 0 to " + str(time_comparison) + " seconds",
                     fontsize=self._title_font_size)
        energy_ax.grid(lw=1, which='minor', axis='both')


        # Capture and Capture Change ###################################################################################
        energy_ax = pyplot.subplot2grid((figure_rows, 2), (6, 0), colspan=2, rowspan=1)


        [min_bin_energy, max_bin_energy, min_bin_value, max_bin_value] = self.graphEnergy(energy_ax, 1, synced_data,
                                                                                          marker="", uncertainty=True,
                                                                                          type="Capture-Rate")
        energy_ax.set_ylim([10 ** -2, 10 ** 2])
        pyplot.title("Capture Neutron Spectrum at time = " + str(time_comparison) + " Seconds",
                     fontsize=self._title_font_size)
        energy_ax.grid(lw=1, which='minor', axis='both')

        y1, y2 = energy_ax.get_ylim()

        energy_ax.set_ylim([y1, 20])


        energy_ax = pyplot.subplot2grid((figure_rows, 2), (7, 0), colspan=2, rowspan=1)

        ax2 = self.plotResonanceEnergies(energy_ax, isotopes=["U"], resonance_types=["capture"])

        self.graphEnergy(energy_ax, 1, synced_data, initial_difference=True, marker="", uncertainty=True,
                         type="Capture-Rate")
        energy_ax.set_xlim([10 ** -9, 10])
        [min_val, max_val] = energy_ax.get_ylim()
        energy_ax.set_ylim([min_val, max_val * 2])

        pyplot.title("Capture Energy Shape Function Shift from time = 0 to " + str(time_comparison) + " seconds",
                     fontsize=self._title_font_size)
        energy_ax.grid(lw=1, which='minor', axis='both')


        y1, y2 = ax2.get_ylim()

        ax2.set_ylim([y1/100, y2])

        y1, y2 = energy_ax.get_ylim()

        energy_ax.set_ylim([y1, 1.2])



        ################################################################################################################

        figure_path = self._output_directory + self._run_name + "-Still-View-Capture-Spectrum.png"
        fig.suptitle("Spectrum", fontsize=self._title_font_size + 2)

        if reposition:
            pyplot.show()

        fig.tight_layout()
        fig.subplots_adjust(top=(0.92 - float(legend_height)/figure_rows))

        fig.savefig(figure_path)
        pyplot.close(fig)

    def logShiftView(self, synced_data, reposition=False,time_comparison = 1.9,tally_type="Flux", tally_types = []):

        fig = pyplot.figure(figsize=(15, 7))

        figure_rows = 4
        #synced_data = self.syncResultsTimingSingle(time_comparison)
        fig.subplots_adjust(hspace=0, wspace=0, top=0.9)


        #########################################################################
        energy_ax = pyplot.subplot2grid((figure_rows, 2), (1, 0), colspan=2, rowspan=2)

        if tally_type == "Flux":
            ax_twin = self.plotResonanceEnergies(energy_ax, isotopes=["U"], resonance_types=['fission', 'capture'])

        elif tally_type == "Fission" or tally_type == "Fission-Rate":
            ax_twin = self.plotResonanceEnergies(energy_ax, isotopes=["U"], resonance_types=['fission', 'capture'])

        elif tally_type == "Capture-Rate":
            ax_twin = self.plotResonanceEnergies(energy_ax, isotopes=["U"], resonance_types=['capture'])

        elif tally_type == "Absorption-Rate":
            ax_twin = self.plotResonanceEnergies(energy_ax, isotopes=["U"], resonance_types=['absorption'])

        #elif tally_type == "Absorption-Rate":
        #    ax_twin = self.plotResonanceEnergies(energy_ax, isotopes=["U"], resonance_types=['absorption'])

        else:
            ax_twin =self.plotResonanceEnergies(energy_ax, isotopes=["U"], resonance_types=['fission', 'capture'])

        ax_twin.set_xticklabels([])

        if not tally_type=="Multiple":

            self.graphEnergy(energy_ax, 1, synced_data, initial_difference=True, initial_difference_log=True, marker="",
                         uncertainty=False, type=tally_type)

        else:

            for tally in tally_types:

                self.graphEnergy(energy_ax, 1, synced_data, initial_difference=True, initial_difference_log=True, marker="",
                     uncertainty=False, type=tally)

        energy_ax.set_xlim([10 ** -9, 10])
        energy_ax.set_ylim([10 ** -4, 10**3.5])
        pyplot.title("Log " + tally_type + " Shape Shift in Kernel from time = 0 to " + str(time_comparison) + " seconds",
                     fontsize=self._title_font_size)
        energy_ax.set_xticklabels([])
        ax_twin.set_ylabel("Cross Section [b]")

        legend_columns = 4
        legend_height = (math.ceil(len(self._results) / legend_columns)) * 0.12
        energy_ax.legend(bbox_to_anchor=(0., 1.18 + legend_height, 1., legend_height), loc=3, ncol=legend_columns,
                         mode="expand",
                         borderaxespad=0., fontsize=self._label_font_size)

        #########################################################################
        energy_ax = pyplot.subplot2grid((figure_rows, 2), (3, 0), colspan=2, rowspan=1)

        if not tally_type == "Multiple":

            self.graphEnergy(energy_ax, 1, synced_data, initial_difference=True, initial_difference_log=True, marker="",
                         uncertainty=False, initial_difference_log_sign="-", type=tally_type)

        else:

            for tally in tally_types:

                self.graphEnergy(energy_ax, 1, synced_data, initial_difference=True, initial_difference_log=True,
                                 marker="",
                                 uncertainty=False, initial_difference_log_sign="-", type=tally)
        energy_ax.set_ylim([10, 10 ** -4])
        energy_ax.set_xlim([10 ** -9, 10])






        if reposition:
            pyplot.show()

        figure_path = self._output_directory + self._run_name + "-Spectrum-Difference-" + tally_type + "-Log.png"
        fig.savefig(figure_path)
        pyplot.close(fig)

    def stillViewSpectrumSingle(self, time_axis="log", log_start_time=0.001, reposition=False,prompt_neutron_lifetime_axis="linear", time_comparison = 1.9, ending_time=-1):

        synced_data = self.syncResultsTimingSingle(time_comparison)

        self.logShiftView(synced_data, reposition=reposition, time_comparison=time_comparison, tally_type="Flux")
        self.logShiftView(synced_data, reposition=reposition, time_comparison=time_comparison, tally_type="Fission")
        self.logShiftView(synced_data, reposition=reposition, time_comparison=time_comparison, tally_type="Fission-Rate")
        self.logShiftView(synced_data, reposition=reposition, time_comparison=time_comparison, tally_type="Capture-Rate")
        self.logShiftView(synced_data, reposition=reposition, time_comparison=time_comparison, tally_type="Absorption-Rate")
        self.logShiftView(synced_data, reposition=reposition, time_comparison=time_comparison, tally_type="Multiple", tally_types=["Absorption-Rate", "Fission-Rate", "Capture-Rate"])

        fig = pyplot.figure(figsize=(18, 40))


        figure_rows = 7*2

        fig.subplots_adjust(hspace=0.3, wspace=0.4)



        #########################################################################
        energy_ax = pyplot.subplot2grid((figure_rows, 2), (0, 0), colspan=2, rowspan=2)
        [min_bin_energy, max_bin_energy, min_bin_value, max_bin_value] = self.graphEnergy(energy_ax, 1, synced_data,
                                                                                          marker="",uncertainty=True)
        #This plots cross sections over the plot
        #for item in ([energy_ax.title, energy_ax.xaxis.label, energy_ax.yaxis.label] + energy_ax.get_xticklabels() + energy_ax.get_yticklabels()):
        #    item.set_fontsize(20)
        ax2 = self.plotResonanceEnergies(energy_ax, resonance_types=["absorption"], isotopes=["U"])
        y1, y2 = ax2.get_ylim()

        ax2.set_ylim([y1/100, y2])

        #y1, y2 = energy_ax.get_ylim()

        energy_ax.set_ylim([0.08, 5])

        #for item in ([ax2.title, energy_ax.xaxis.label, ax2.yaxis.label] + ax2.get_xticklabels() + ax2.get_yticklabels()):
        #   item.set_fontsize(20)

        pyplot.title("Spectrum at time = " + str(time_comparison), fontsize=self._title_font_size)
        energy_ax.grid(lw=1, which='minor', axis='both')

        legend_columns = 4
        legend_height = (math.ceil(len(self._results) / legend_columns)) * 0.12
        energy_ax.legend(bbox_to_anchor=(0., 1.18 + legend_height, 1., legend_height), loc=3, ncol=legend_columns, mode="expand",
                       borderaxespad=0., fontsize=self._label_font_size)



        #########################################################################
        energy_ax = pyplot.subplot2grid((figure_rows, 2), (2, 0), colspan=2, rowspan=2)
        self.graphEnergy(energy_ax, 1, synced_data, initial_difference=True, marker="", uncertainty=True)
        [min_diff, max_diff] = self.getMaxTallyDifferentialChange(synced_data)
        energy_ax.set_xlim([10 ** -9, 10])
        pyplot.title("Flux Shape Shift in Kernel from time = 0 to " + str(time_comparison) + " seconds",
                     fontsize=self._title_font_size)
        energy_ax.grid(lw=1, which='minor', axis='both')

        ############################################################################
        beta_ax = pyplot.subplot2grid((figure_rows, 2), (4, 0), colspan=1, rowspan=2)
        [max_time, min_value, max_value] = self.graphAttribute(beta_ax, 0, "Beta_eff", time_axis,
                                                               "linear", log_start_time=log_start_time, uncertainty_column="Beta_eff sigma", sigma_levels=[1,2], ending_time=ending_time)

        beta_ax.set_ylabel("$\\beta_{eff}$ [unitless]", fontsize=self._label_font_size + 3)
        pyplot.title("Beta Effective", fontsize=self._title_font_size)

        ######################################################################################
        neutron_lifetime_ax = pyplot.subplot2grid((figure_rows,2), (4, 1), colspan=1, rowspan=2)
        [max_time, min_value, max_value] = self.graphAttribute(neutron_lifetime_ax, 0, "neutron lifetime [s]", time_axis,
                                                               prompt_neutron_lifetime_axis, plot_type="step",sigma_levels=[1,2],
                                                               log_start_time=log_start_time, uncertainty_column="Neutron Lifetime sigma [s]", yfactor=1e6,  ending_time=ending_time)
        #neutron_lifetime_ax.set_ylim([10, 1000])

        neutron_lifetime_ax.set_ylabel("Lifetime [$\mu$s]", fontsize=self._label_font_size)
        #neutron_lifetime_ax.grid(lw=1, which='minor', axis='x')
        #neutron_lifetime_ax.axis([log_start_time, max_time, 10**math.floor(math.log10(min_value)), 10**math.ceil(math.log10(max_value)) ])
        pyplot.title("Prompt Neutron Lifetime", fontsize=self._title_font_size)

        ####################################################################################
        flux_peaking = pyplot.subplot2grid((figure_rows, 2), (6, 0), colspan=1, rowspan=2)
        self.plotTallyZoneCellTallyDataAtPointVsTime(flux_peaking, zone=1, cell=1, tally_type="Flux", uncertainty=True, sigma_levels=[1,2], plot_type="step", log_start_time=log_start_time,  ending_time=ending_time)
        pyplot.title("Flux Depression in Fuel vs. Time", fontsize=self._title_font_size)

        ####################################################################################
        power_peaking_ax = pyplot.subplot2grid((figure_rows, 2), (6, 1), colspan=1, rowspan=2)
        self.plotTallyZoneCellTallyDataAtPointVsTime(power_peaking_ax, zone=1, cell=1, tally_type="Fission", uncertainty=True, sigma_levels=[1,2], plot_type="step", log_start_time=log_start_time,  ending_time=ending_time)
        pyplot.title("Power Depression in Fuel vs. Time", fontsize=self._title_font_size)
        power_peaking_ax.set_ylim([98, 100])

        ####################################################################################
        tally_ax = pyplot.subplot2grid((figure_rows, 2), (8, 0), colspan=1, rowspan=2)
        self.plotTallyZoneCellTallyData(tally_ax, [2], 0, uncertainty=True)
        pyplot.title("Flux Spatial Distribution Time = " + str(time_comparison) +" s", fontsize=self._title_font_size)
        tally_ax.set_ylim([99.85, 100])

        ######################################################################################
        tally_ax = pyplot.subplot2grid((figure_rows, 2), (8, 1), colspan=1, rowspan=2)
        self.plotTallyZoneCellTallyData(tally_ax, [2], 0, uncertainty=True, tally_type="Fission")
        pyplot.title("Fission Spatial Distribution Time = " + str(time_comparison) +" s", fontsize=self._title_font_size)
        tally_ax.set_ylim([97.5,100])
        #tally_ax.set_xlim([0, 30])

        ###################################################################################
        energy_ax = pyplot.subplot2grid((figure_rows, 2), (10, 0), colspan=2, rowspan=2)
        [min_bin_energy, max_bin_energy, min_bin_value, max_bin_value] = self.graphEnergy(energy_ax, 1, synced_data,
                                                                                          marker="", uncertainty=True,type="Fission")
        energy_ax.set_ylim([10 ** -2, 10 ** 2])
        pyplot.title("Fission Neutron Spectrum at time = " + str(time_comparison) + " Seconds", fontsize=self._title_font_size)
        energy_ax.grid(lw=1, which='minor', axis='both')

        ######################################################################################
        energy_ax = pyplot.subplot2grid((figure_rows, 2), (12, 0), colspan=2, rowspan=2)
        self.graphEnergy(energy_ax, 1, synced_data, initial_difference=True, marker="", uncertainty=True, type="Fission")
        #[min_diff, max_diff] = self.getMaxTallyDifferentialChange(synced_data)
        energy_ax.set_xlim([10 ** -9, 10])
        pyplot.title("Fission Energy Shape Function Shift from time = 0 to " + str(time_comparison) + " seconds", fontsize=self._title_font_size)
        energy_ax.grid(lw=1, which='minor', axis='both')

        #self.plotResonanceEnergies(energy_ax, isotopes=["U-235"], resonance_types=["fission"])

        figure_path = self._output_directory + self._run_name + "-Still-View-Spectrum.png"
        fig.suptitle("Spectrum", fontsize=self._title_font_size + 2)

        if reposition:
            pyplot.show()

        fig.tight_layout()
        fig.subplots_adjust(top=(0.90 - float(legend_height)/figure_rows))

        #pyplot.show()
        fig.savefig(figure_path)
        pyplot.close(fig)

    def standardVideoView(self, time_step_divisions, time_axis="log", log_start_time=0.001, ending_time=-1):

        synced_data = self.syncResultsTiming(time_step_divisions,time_axis, log_start_time, sync_tally=False)

        time_list = synced_data["time"]

        #cut all times that are not in our log time axis view
        if time_axis == "log":

            time_list = [ time for time in time_list if time >= log_start_time ]


        [min_temperature, max_temperature] = self.getTemperatureExtremes(synced_data)

        for timestep_index in range(0, len(time_list)):

            current_time = time_list[timestep_index]

            fig = pyplot.figure(figsize=(19.2, 10.8))
            fig.subplots_adjust(hspace=0.3, wspace=3)
            # Temperature #############################################################################################
            temp_ax = pyplot.subplot2grid((3, 6), (0, 0), colspan=2, rowspan=4)
            self.graphTemperature(temp_ax, timestep_index, synced_data, legend=True)
            temp_ax.axis([0, 100, min_temperature, max_temperature])

            # Power ###################################################################################################
            power_ax = pyplot.subplot2grid((3, 6), (0, 2), colspan=4, rowspan=1)
            [max_time, min_value, max_value] = self.graphAttribute(power_ax, current_time, "Power [W/m^3]", time_axis, "log", log_start_time=log_start_time, ending_time=ending_time)
            power_ax.grid(lw=1, which='minor', axis='both')

            # Reactivity ##############################################################################################
            reactivity_ax = pyplot.subplot2grid((3, 6), (1, 2), colspan=4, rowspan=1)
            [max_time, min_value, max_value] = self.graphAttribute(reactivity_ax, current_time, "k_eff", time_axis, "linear", plot_type="step", log_start_time=log_start_time,  ending_time=ending_time, uncertainty_column="k_eff sigma")
            pyplot.ylabel('k$_{eff*}$', fontsize=self._label_font_size + 3)
            reactivity_ax.grid(lw=1, which='minor', axis='x')

            # Integrated Power ########################################################################################
            integrated_ax = pyplot.subplot2grid((3, 6), (2, 2), colspan=4, rowspan=1)
            [max_time, min_value, max_value] = self.graphAttribute(integrated_ax, current_time, "Integrated Power [J/m^3]", time_axis, "log",log_start_time=log_start_time,  ending_time=ending_time)

            integrated_ax.set_ylim([ 10 ** 7, max_value])

            integrated_ax.grid(lw=1, which='minor', axis='x')

            string_index = str(timestep_index)
            figure_path = self._output_directory + self._run_name + "-Standard-View-" + string_index.rjust(4,'0') + ".png"  # + "-" + str(time_list[timestep_index]) + ".png"

            fig.suptitle("Time = " + "%.3e " % (current_time), fontsize=self._label_font_size)
            fig.savefig( figure_path )
            pyplot.close(fig)

        view_type = "Standard-View"
        animated_gif = self._run_name + "-" + view_type + ".gif"
        constituent_pngs = self._run_name + "-" + view_type + "-*.png"

        os.system("cd " + self._output_directory + ";convert -delay 40 -loop 0 " + constituent_pngs + " " + animated_gif)
        os.system("cd " + self._output_directory + ";rm " + constituent_pngs)

    def multiscaleVideoView(self, time_step_divisions, time_axis="log", log_start_time=0.001, ending_time=-1):

        synced_data = self.syncResultsTiming(time_step_divisions,time_axis, log_start_time, sync_tally=False)

        time_list = synced_data["time"]

        #cut all times that are not in our log time axis view
        if time_axis == "log":

            time_list = [ time for time in time_list if time >= log_start_time ]


        [min_temperature, max_temperature] = self.getTemperatureExtremes(synced_data)

        for timestep_index in range(0, len(time_list)):

            current_time = time_list[timestep_index]

            fig = pyplot.figure(figsize=(19.2, 10.8))
            fig.subplots_adjust(hspace=0.3, wspace=3)
            # Moderator Temperature #############################################################################################
            temp_ax = pyplot.subplot2grid((2, 6), (0, 0), colspan=2, rowspan=1)
            self.graphTemperature(temp_ax, timestep_index, synced_data, legend=True)
            temp_ax.axis([0, 100, min_temperature, max_temperature])
            temp_ax.set_ylabel('Meso Temperature [K]')

            # Fuel Temperature #############################################################################################
            temp_ax = pyplot.subplot2grid((2, 6), (1, 0), colspan=2, rowspan=1)
            self.graphTemperature(temp_ax, timestep_index, synced_data, legend=True, type="fuel")
            temp_ax.axis([0, 100, 975, 1500])
            temp_ax.set_ylabel('Micro Temperature [K]')

            # Power ###################################################################################################
            power_ax = pyplot.subplot2grid((3, 6), (0, 2), colspan=4, rowspan=1)
            [max_time, min_value, max_value] = self.graphAttribute(power_ax, current_time, "Power [W/m^3]", time_axis, "log", log_start_time=log_start_time, ending_time=ending_time)
            power_ax.grid(lw=1, which='minor', axis='both')

            # Reactivity ##############################################################################################
            reactivity_ax = pyplot.subplot2grid((3, 6), (1, 2), colspan=4, rowspan=1)
            [max_time, min_value, max_value] = self.graphAttribute(reactivity_ax, current_time, "k_eff", time_axis, "linear", plot_type="step", log_start_time=log_start_time,  ending_time=ending_time, uncertainty_column="k_eff sigma")
            pyplot.ylabel('k$_{eff*}$', fontsize=self._label_font_size + 3)
            reactivity_ax.grid(lw=1, which='minor', axis='x')

            # Integrated Power ########################################################################################
            integrated_ax = pyplot.subplot2grid((3, 6), (2, 2), colspan=4, rowspan=1)
            [max_time, min_value, max_value] = self.graphAttribute(integrated_ax, current_time, "Integrated Power [J/m^3]", time_axis, "log",log_start_time=log_start_time,  ending_time=ending_time)

            integrated_ax.set_ylim([ 10 ** 7, max_value])

            integrated_ax.grid(lw=1, which='minor', axis='x')

            string_index = str(timestep_index)
            figure_path = self._output_directory + self._run_name + "-Standard-View-" + string_index.rjust(4,'0') + ".png"  # + "-" + str(time_list[timestep_index]) + ".png"

            fig.suptitle("Time = " + "%.3e " % (current_time), fontsize=self._label_font_size)
            fig.savefig( figure_path )
            pyplot.close(fig)

        view_type = "Standard-View"
        animated_gif = self._run_name + "-" + view_type + ".gif"
        constituent_pngs = self._run_name + "-" + view_type + "-*.png"

        os.system("cd " + self._output_directory + ";convert -delay 40 -loop 0 " + constituent_pngs + " " + animated_gif)
        os.system("cd " + self._output_directory + ";rm " + constituent_pngs)



    def worthGraphs(self, line_worth=False):

        fig = pyplot.figure(figsize=(16, 25))
        figure_height = 15
        figure_width = 2
        ax = pyplot.subplot2grid((figure_height, figure_width), (0, 0), colspan=figure_width, rowspan=4)
        color_index = 0
        '''
        :type result Result.Results
        '''
        for result in self._results:

            worth_data = result._worth_data

            #sometime there isn't worth data
            if worth_data:

                label=self._labels[result.getFolderName()]
                color = self._colors[color_index % len(self._colors)]
                self.graphResultWorth(ax, worth_data, color, label, color_index)
            color_index += 1

        legend_columns = 3
        legend_height = (math.ceil(len(self._results) / legend_columns)) * 0.02
        ax.legend(bbox_to_anchor=(0., 1.04 + legend_height, 1., legend_height), loc=3, ncol=legend_columns,
                        mode="expand", borderaxespad=0., fontsize=self._label_font_size)

        ax.grid(lw=1, which='minor', axis='x')
        ax.grid(lw=3, which='major', axis="x")

        ax.set_xlim([0,3000])
        y1, y2 = ax.get_ylim()
        ax.set_ylim(y1, 0)

        ax = pyplot.subplot2grid((figure_height, figure_width), (5, 0), colspan=1, rowspan=3)

        total_worth_data = []
        total_worth_labels = []
        indicies = [ ]

        index_counter = 0.5
        run_counter = 0
        bar_colors = []

        for result in self._results:

            worth_data = result._worth_data

            #sometime there isn't worth data
            if worth_data:

                label=self._labels[result.getFolderName()]
                total_worth_value = worth_data._best_regression['intercept'] + worth_data._best_regression['slope'] * 3000 ** worth_data._best_regression['power']
                total_worth_data.append(-total_worth_value)
                total_worth_labels.append(label)
                indicies.append(index_counter)
                index_counter +=1
                bar_colors.append( self._colors[run_counter % len(self._colors)])

            run_counter += 1

        bar = ax.bar(indicies,total_worth_data, align='center')

        for index in range( len(bar_colors)):
            bar[index].set_color( bar_colors[index])

        ax.set_ylabel('300 to 3000 K Worth [pcm]', fontsize=self._label_font_size)
        pyplot.xticks( numpy.arange(0.5, max(indicies) + 1, 1.0))
        ax.set_xticklabels( total_worth_labels)
        ax.grid(lw=3, which='major', axis="y")
        ax.grid(lw=1, which='minor', axis='y')
        pyplot.xticks(rotation=60)

        if line_worth:
            identified_data = [ float(data) for data in self._data]
            ax = pyplot.subplot2grid((figure_height, figure_width), (8, 0), colspan=2, rowspan=3)
            ax.plot(identified_data, total_worth_data, "-o", lw=3, markersize=20, marker="v")

        ax.set_ylabel('300 to 3000 K Worth [pcm]', fontsize=self._label_font_size)
        ax.grid(lw=3, which='major', axis="both")
        ax.grid(lw=1, which='minor', axis='both')

        ax = pyplot.subplot2grid((figure_height, figure_width), (5, 1), colspan=1, rowspan=3)

        k_inf_data = []
        k_inf_labels = []
        indicies = []
        index_counter = 0.5
        run_counter = 0
        bar_colors = []

        for result in self._results:

            worth_data = result._worth_data

            # sometime there isn't worth data
            if worth_data:
                label = self._labels[result.getFolderName()]
                k_inf = float(worth_data.csv_data[0]["K-eigenvalue"])
                k_inf_data.append(k_inf) #10**5*(k_inf - 1)/k_inf)
                k_inf_labels.append(label)
                indicies.append(index_counter)
                index_counter += 1
                bar_colors.append(self._colors[run_counter % len(self._colors)])

            run_counter += 1




        bar = ax.bar(indicies, k_inf_data, align='center')

        for index in range( len(bar_colors)):
            bar[index].set_color( bar_colors[index])

        ax.set_ylabel('$k_{\infty}$  at 300 K', fontsize=self._label_font_size)
        pyplot.xticks(numpy.arange(0.5, max(indicies) + 1, 1.0))
        ax.set_xticklabels( k_inf_labels)
        ax.grid(lw=3, which='major', axis="y")
        ax.grid(lw=1, which='minor', axis='y')
        pyplot.xticks(rotation=60)

        y1, y2 = ax.get_ylim()
        ax.set_ylim(1.0, y2)

        ax = pyplot.subplot2grid((figure_height, figure_width), (9, 0), colspan=figure_width, rowspan=4)
        color_index = 0
        '''
        :type result Result.Results
        '''
        for result in self._results:

            worth_data = result._moderator_worth_data

            # sometime there isn't worth data
            if worth_data:
                label = self._labels[result.getFolderName()]
                color = self._colors[color_index % len(self._colors)]
                self.graphResultWorth(ax, worth_data, color, label, color_index)
            color_index += 1


        fig.tight_layout()
        fig.subplots_adjust(top=(0.92 - 2  *float(legend_height)))


        fig.suptitle("Worth Study", fontsize=self._label_font_size + 3)
        fig.savefig(self._output_directory + self._run_name + "-Worth.png")

    def multiWorthGraphs(self, line_worth=False):

        fig = pyplot.figure(figsize=(12, 8))
        figure_height = 15
        figure_width = 2

        # Line graph worth vs. temperature #############################################################################
        ax = pyplot.subplot2grid((figure_height, figure_width), (0, 0), colspan=figure_width, rowspan=10)
        ax.plot([0,0],[0,0],':',color=self._colors[1], label="Fuel Worth")
        ax.plot([0, 0], [0, 0], '--', color=self._colors[2], label="Matrix Worth")
        ax.plot([0, 0], [0, 0], '-', color=self._colors[0],label="Total Worth")
        ax.grid(lw=1, which='minor', axis='x')
        ax.grid(lw=3, which='major', axis="x")

        legend_columns = 4
        legend_height = (math.ceil(len(self._results) / legend_columns)) * 0.02
        ax.legend(bbox_to_anchor=(0., 1.04 + legend_height, 1., legend_height), loc=3, ncol=legend_columns,
                  mode="expand", borderaxespad=0., fontsize=self._label_font_size)


        color_index = 0

        for result in self._results:

            moderator_worth_data = result._moderator_worth_data
            fuel_worth_data = result._fuel_worth_data
            worth_data = result._worth_data
            color = self._colors[color_index % len(self._colors)]
            #sometime there isn't worth data
            # sometime there isn't worth data
            if worth_data:
                label = self._labels[result.getFolderName()]
                self.graphResultWorth(ax, worth_data, self._colors[0], label, color_index, label_offset=(len(self._results) * 2 + 2) )

            if moderator_worth_data:

                label=self._labels[result.getFolderName()]
                self.graphResultWorth(ax, moderator_worth_data, self._colors[2], label, color_index, linestyle="--", marker_points='x')

            if fuel_worth_data:

                label=self._labels[result.getFolderName()]
                self.graphResultWorth(ax, fuel_worth_data, self._colors[1], label, color_index,label_offset=(len(self._results) + 1) , marker_points='v', linestyle=":")



            color_index += 1





        ax.set_xlim([0,3000])
        y1, y2 = ax.get_ylim()
        ax.set_ylim(y1, 10)

        # Bar Plot -- Fuel Worth #######################################################################################
        ax = pyplot.subplot2grid((figure_height, figure_width), (11, 0), colspan=1, rowspan=3)
        total_worth_data = []
        total_worth_labels = []
        indicies = [ ]

        index_counter = 0.5
        run_counter = 0
        bar_colors = []

        for result in self._results:

            moderator_worth_data = result._moderator_worth_data
            fuel_worth_data = result._fuel_worth_data

            #sometime there isn't worth data
            if fuel_worth_data and moderator_worth_data:

                label=self._labels[result.getFolderName()] + " Fuel"
                total_worth_value = fuel_worth_data._best_regression['intercept'] + fuel_worth_data._best_regression['slope'] * 3000 ** fuel_worth_data._best_regression['power']
                total_worth_data.append(-total_worth_value)
                total_worth_labels.append(label)
                indicies.append(index_counter)
                index_counter +=1
                bar_colors.append( self._colors[run_counter % len(self._colors)])


                label=self._labels[result.getFolderName()] + "Moderator"
                total_worth_value = moderator_worth_data._best_regression['intercept'] + moderator_worth_data._best_regression['slope'] * 3000 ** moderator_worth_data._best_regression['power']
                total_worth_data.append(-total_worth_value)
                total_worth_labels.append(label)
                indicies.append(index_counter)
                index_counter +=1
                bar_colors.append( self._colors[run_counter % len(self._colors)])

                index_counter +=1

            run_counter += 1

        bar = ax.bar(indicies,total_worth_data, align='center')

        for index in range( len(bar_colors)):
            bar[index].set_color( bar_colors[index])

        ax.set_ylabel('300 to 3000 K Worth [pcm]', fontsize=self._label_font_size)
        pyplot.xticks( numpy.arange(0.5, max(indicies) + 1, 1.0))
        ax.set_xticklabels( total_worth_labels)
        ax.grid(lw=3, which='major', axis="y")
        ax.grid(lw=1, which='minor', axis='y')
        pyplot.xticks(rotation=60)

        if line_worth:
            identified_data = [ float(data) for data in self._data]
            ax = pyplot.subplot2grid((figure_height, figure_width), (8, 0), colspan=2, rowspan=3)
            ax.plot(identified_data, total_worth_data, "-o", lw=3, markersize=20, marker="v")

        ax.set_ylabel('300 to 3000 K Worth [pcm]', fontsize=self._label_font_size)
        ax.grid(lw=3, which='major', axis="both")
        ax.grid(lw=1, which='minor', axis='both')




        fig.tight_layout()
        fig.subplots_adjust(top=(0.92 - 2  *float(legend_height)))

        #pyplot.show()
        #fig.suptitle("Worth Study", fontsize=self._label_font_size + 3)
        fig.savefig(self._output_directory + self._run_name + "-Multi-Worth.png")

    def graphResultWorth(self, ax1, worth_data, color, label, index, linestyle="-", marker_points="o", label_offset=0):

        import numpy as np
        eps = np.finfo(np.double).eps

        def dollars(pcm): return pcm / (10**5 * 0.0065)

        def update_ax2(ax1):
            y1, y2 = ax1.get_ylim()
            ax2.set_ylim(dollars(y1), dollars(y2))



        regression_points = numpy.linspace(worth_data._ordered_temperatures[0],worth_data._ordered_temperatures[-1],100)
        y_best_regression = [worth_data._best_regression['intercept'] + worth_data._best_regression['slope'] * temp ** worth_data._best_regression['power'] for temp in regression_points]

        [slope, intercept, r_value, p_value, std_err] = worth_data.regression(0.5, worth_data._ordered_temperatures, worth_data._ordered_reactivity)
        y_sqrt_regression = [intercept + slope * temp ** 0.5 for temp in worth_data._ordered_temperatures]

        ax2 = ax1.twinx()

        # automatically update ylim of ax2 when ylim of ax1 changes.
        ax1.callbacks.connect("ylim_changed", update_ax2)

        ax2.plot(worth_data._ordered_temperatures, worth_data._ordered_dollars, marker_points,color=color, markersize=12)
        ax1.plot(worth_data._ordered_temperatures, worth_data._ordered_reactivity, marker_points, color=color, markersize=12)

        best_match_label = label
        ax1.plot(regression_points, y_best_regression, linestyle, label=best_match_label, color=color, lw=4)

        if worth_data._best_regression['power'] > 0.010:

            power_str = "%0.3f" % worth_data._best_regression['power']

        else:

            power_str = "%0.1e" % worth_data._best_regression['power']
            exp = power_str.find('e-')
            power_str = power_str[:exp] + 'e-' + str(int(power_str[exp + 2:]))

        if abs(worth_data._best_regression['slope']) < 1000:

            slope_str = "%0.1f" % worth_data._best_regression['slope']

        else:

            slope_str = "%0.1e" % worth_data._best_regression['slope']
            exp = slope_str.find('e+')
            slope_str = slope_str[:exp] + 'e' + str(int(slope_str[exp + 2:]))

        if abs(worth_data._best_regression['intercept']) < 1000:

            intercept_str = "%0.1f" % worth_data._best_regression['intercept']

        else:

            intercept_str = "%0.1e" % worth_data._best_regression['intercept']

            exp = intercept_str.find('e+')
            intercept_str = intercept_str[:exp] + 'e' + str(int(intercept_str[exp + 2:]))

        #pyplot.annotate('$\\rho$ = %s T$^{%s}$ + %s pcm R$^{2}$ = %0.5f' % (
        #    slope_str, power_str, intercept_str, worth_data._best_regression['r2']), color=color, fontsize=self._label_font_size , xy=(0.03, 0.03 + 0.06 * (index + label_offset)),
        #            xycoords='axes fraction' )




        #sqrt_match_label = 'T$^{0.5}$    R$^{2}$ = %0.5f' % (r_value ** 2)
        #ax1.plot(worth_data._order_temperatures, y_sqrt_regression, '-', label=sqrt_match_label, color='green', lw=2)
        #pyplot.annotate('$\\rho$ = %0.4f$\sqrt{T}$ + %0.4f pcm' % (slope, intercept), color='green', fontsize=20,
        #                xy=(0.05, 0.15), xycoords='axes fraction')


        pyplot.grid()
        ax1.set_xlabel("Temperature [K]", fontsize=18)
        ax1.set_ylabel("Reactivity [pcm]", fontsize=18)
        ax2.set_ylabel("Reactivity [$]", fontsize=18)

    def graphTemperatureAtPoint(self, ax, synced_data, desired_positions={ 0:"Centerline", 100 : "End" }, time_axis = "linear", yscale = "linear", legend = False, log_start_time=0.001, timeline= -1, time_base="seconds", ending_time = -1 ):

        max_value = 0
        min_value = 1e100
        max_time = 0

        if timeline >= log_start_time:
            ax.plot([float(timeline), float(timeline)], [float(100.0), float(10000.0)])

        positions = sorted(desired_positions)

        time_list = synced_data["time"]

        # if we are in log time cut all times that are not in our log time axis view
        if time_axis == "log":

            time_list = [single_time for single_time in time_list if single_time >= log_start_time]

        run_index = 0

        for run in self._results:

            [times, temperatures] = run.getTemperatureVsTime(positions)

            for index in range(0, len(times)):

                if times[index] < log_start_time and time_axis == "log":

                    time_index = log_start_time;

            color_index = 0
            full_data = run.getSimulationData()

            for temperature_set,position in zip(temperatures,positions):


                label = desired_positions[position]

                if(len(self._results) == 1):
                    color = self._colors[(run_index + color_index ) % len(self._colors)]
                    line_style = self._line_styles[0]

                else:
                    color = self._colors[run_index % len(self._colors)]
                    line_style = self._line_styles[color_index % len(self._line_styles)]

                if time_base == "Prompt Neutron Lifetime":

                    prompt_neutron_lifetimes = full_data.getColumnData("neutron lifetime [s]")
                    prompt_neutron_lifetime = float(prompt_neutron_lifetimes[0])

                    times = [ time/prompt_neutron_lifetime for time in times]

                if run_index == 0:

                    ax.plot(times, temperature_set["temperature"],linestyle=line_style, color=color, lw=self._line_width,label=label)

                else:

                    ax.plot(times, temperature_set["temperature"], linestyle=line_style, color=color,lw=self._line_width)


                color_index = color_index + 1

                current_max_value = max(temperature_set["temperature"])
                current_min_value = min(temperature_set["temperature"])
                current_max_time = max(times)

                if (current_max_value > max_value):
                    max_value = current_max_value

                if (current_max_time > max_time):
                    max_time = current_max_time

                if (current_min_value < min_value or min_value == 0):
                    min_value = current_min_value


            run_index += 1


        ax.set_xscale(time_axis)
        ax.set_yscale(yscale)

        axis_bounds = []

        if (time_axis == "log"):

            if time_base == "Prompt Neutron Lifetime":

                axis_bounds.append(10)

            else:

                axis_bounds.append(log_start_time)


        else:

            axis_bounds.append(0.0)

        if ending_time > 0:

            axis_bounds.append(ending_time)

        else:

            axis_bounds.append(max_time)

        if (yscale == "log"):

            if(min_value <= 0):

                min_value = 1e-100

            total_range = max_value - min_value
            axis_bounds.append(10*math.floor( (min_value - total_range * 0.05)/10))
            axis_bounds.append(10*math.ceil( (max_value + total_range * 0.20)/10 ))

        else:

            value_range = max_value - min_value
            axis_bounds.append(min_value - 0.04* value_range)
            axis_bounds.append(max_value + 0.20 * value_range)

        ax.axis(axis_bounds)

        ax.grid(lw=3, which='major')

        if time_base == "Prompt Neutron Lifetime":
            pyplot.xlabel('Prompt Neutron Lifetimes', fontsize=self._label_font_size)

        else:
            pyplot.xlabel('Time [s]', fontsize=self._label_font_size)

        pyplot.ylabel('Temperature [K]', fontsize=self._label_font_size)

        if(legend):

            ax.legend(loc=2, ncol=1, fontsize=self._legend_font_size)



        return [max_time, min_value, max_value]

    def graphAttribute(self, ax, current_time, column, xscale = "linear", yscale = "linear", legend = False, plot_type="line",
                       log_start_time=0.001, nominalized = False, uncertainty_column = None, sigma_levels=[1], yfactor=1,time_base = "seconds",
                       ending_time=-1, linetype=False, linewidth=False, color_override = None, pattern=False):

        color_index = 0
        max_value = 0
        min_value = 0
        max_time = 0

        run_index = 0

        for run in self._results:


            if pattern:

                linetype=self._line_styles[run_index%len(self._line_styles)]

            run_index += 1
            label = self._labels[run.getFolderName()]

            full_data = run.getSimulationData()

            try:

                values = [float(value) for value in full_data.getColumnData(column)]

            except:

                print("column " + column + " not in " + label)
                color_index = color_index + 1
                continue

            times = []

            if color_override is None:
                run_color = self._colors[color_index % len(self._colors)]
            else:
                run_color= color_override

            for time in full_data.getColumnData("Time [s]"):

                if float(time) == 0.0 and xscale == "log":

                    times.append(log_start_time/2.0)

                else:

                    times.append(float(time))

            if nominalized:
                values = [ value/values[0] for value in values]

            if not yfactor == 1:
                values = [value*yfactor for value in values]

            if time_base == "Prompt Neutron Lifetime":
                prompt_neutron_lifetimes = full_data.getColumnData("neutron lifetime [s]")
                prompt_neutron_lifetime = float(prompt_neutron_lifetimes[0])

                times = [ float(time) / prompt_neutron_lifetime for time in times]

            if not uncertainty_column is None:

                values_error = [float(error) for error in full_data.getColumnData(uncertainty_column)]

                if nominalized:
                    values_error = [ error/values[0] for error in values_error]

                if not yfactor == 1:
                    values_error = [error * yfactor for error in values_error]

                [error_bins, error_below, error_above] = self.getUncertainty(times, values, values_error, plot_type=plot_type,sigma_levels=sigma_levels)

                for index in range(len(error_below)):
                    alpha = 0.3 - 0.2 * index / len(error_above)

                    ax.fill_between(error_bins, error_below[index], error_above[index],
                                           facecolor=run_color, alpha=alpha,
                                           label=str(sigma_levels[index]) + " $\sigma$")


            if linetype == False:

                linetype = self._line_styles[0]

            if linewidth == False:

                linewidth = self._line_width

            if plot_type == "step":

                ax.step(times, values, color=run_color, lw=linewidth,label=label, where="pre", linestyle=linetype)

            else:

                ax.plot(times, values, color=run_color, lw=linewidth,label=label, linestyle=linetype )

            color_index = color_index + 1


            current_max_time = max(times)



            if (current_max_time > max_time):
                max_time = current_max_time


            #set the bounds
            if uncertainty_column is None:

                current_max_value = max(values)
                current_min_value = min(values)

            else:

                max_sigma_index = sigma_levels.index(max(sigma_levels))
                current_max_value = max(error_above[max_sigma_index])
                current_min_value = min(error_below[max_sigma_index])

            if (current_max_value > max_value):
                max_value = current_max_value

            if (current_min_value < min_value or min_value == 0):
                min_value = current_min_value

        ax.set_xscale(xscale)
        ax.set_yscale(yscale)

        ax.plot([current_time, current_time], [1e-100, 1e100], lw=5, color='black')

        axis_bounds = []

        if (xscale == "log"):

            if time_base == "Prompt Neutron Lifetime":
                axis_bounds.append(10)
            else:
                axis_bounds.append(log_start_time)

        else:

            axis_bounds.append(0.0)

        if ending_time  > 0:
            axis_bounds.append(ending_time)

        else:
            axis_bounds.append(max_time)

        if (yscale == "log"):

            if(min_value <= 0):

                min_value = 1e-100

            value_range = max_value - min_value
            axis_bounds.append(5**math.floor( math.log(min_value,5) ))
            axis_bounds.append(10*math.ceil( (max_value + value_range * 0.20)/10 ))

        else:

            value_range = max_value - min_value
            axis_bounds.append(min_value - 0.04* value_range)
            axis_bounds.append(max_value + 0.04 * value_range)

        ax.axis(axis_bounds)

        ax.grid(lw=3, which='major')
        axis_bounds.append(log_start_time)

        if time_base == "Prompt Neutron Lifetime":
            pyplot.xlabel('Prompt Neutron Lifetimes', fontsize=self._label_font_size)

        else:
            pyplot.xlabel('Time [s]', fontsize=self._label_font_size)

        pyplot.ylabel(column, fontsize=self._label_font_size)

        if(legend):

            ax.legend(loc=1, ncol=2, fontsize=self._legend_font_size)

        return [max_time, min_value, max_value]

    def graphTemperature(self, temp_ax, timestep_index, synced_data, legend=False, type="normal"):

        temp_ax.grid(lw=3)
        pyplot.xlabel('Radius[%]', fontsize=self._label_font_size)
        pyplot.ylabel('Temperature [K]', fontsize=self._label_font_size)

        if type == "normal":
            [positions, temperatures] = self.getTemperatureGraphData(synced_data, timestep_index)
        else:
            [positions, temperatures] = self.getMicrocellTemperatureGraphData(synced_data, timestep_index)

        color_index = 0

        for run in self._ordered_labels:
            temp_ax.plot(positions[run], temperatures[run], color=self._colors[color_index % len(self._colors)], lw=self._line_width, label=self._labels[run])
            color_index += 1

        if legend:

            temp_ax.legend(loc=1, ncol=1, fontsize=self._legend_font_size)

    def getMicrocellTemperatureGraphData(self,synced_data, time_index):

        positions = {}
        temperatures = {}

        for run_name in self._labels:

            if run_name == 'time':
                continue

            if not "microcell-temperature" in synced_data[run_name] or len(synced_data[run_name]["microcell-temperature"]) == 0:
                positions[run_name] = [0]
                temperatures[run_name] = [0]
                continue

            microcell_data = synced_data[run_name]["microcell-temperature"]
            index = 0

            position_key = 'Position-' + str(index) + " [m]"
            temperature_key = 'Temperature-' + str(index) + " [K]"
            integrated_power_key = 'Integrated-Power-' + str(index) + " [W-s]"
            current_power_key = 'Current-Power-' + str(index) + " [W]"

            temperatures[run_name] = []
            positions[run_name] = []

            while position_key in microcell_data:

                positions[run_name].append(microcell_data[position_key][time_index])
                temperatures[run_name].append(microcell_data[temperature_key][time_index])
                #current_power = run._microcell_temperature.getColumnData(current_power_key)
                #integrated_power = run._microcell_temperature.getColumnData(integrated_power_key)

                index += 1

                position_key = 'Position-' + str(index) + " [m]"
                temperature_key = 'Temperature-' + str(index) + " [K]"
                integrated_power_key = 'Integrated-Power-' + str(index) + " [W-s]"
                current_power_key = 'Current-Power-' + str(index) + " [W]"

            max_position = max(positions[run_name])
            relative_positions = [100.0 * position / max_position for position in positions[run_name]]

            positions[run_name] = relative_positions



        return [positions, temperatures]

    def getTemperatureGraphData(self, synced_data, time_index):

        positions = {}
        temperatures = {}

        for run_name in self._labels:

            if run_name == 'time':
                continue

            #A homogenous case with only one point
            if (len(synced_data[run_name]['positions']) == 1):
                positions[run_name] = [0, 100]
                temperature = synced_data[run_name]['temperatures'][time_index][0]
                temperatures[run_name] = [ temperature, temperature ]

            # Many points with temperatures
            else:
                max_position = max(synced_data[run_name]['positions'])
                relative_positions = [100.0 * position / max_position for position in synced_data[run_name]['positions']]

                positions[run_name] = relative_positions

                number_timesteps_in_run = len(synced_data[run_name]['time'])

                if number_timesteps_in_run > time_index + 1:

                    temperatures[run_name] = synced_data[run_name]['temperatures'][time_index]

                else:

                    temperatures[run_name] = (synced_data[run_name]['temperatures'][-1])

            #This fixes the problem with homogenous plots


        return [positions, temperatures]

    def getUncertainty(self, times, values,values_error,plot_type="line", sigma_levels = [ 1 ]):

        error_above = []
        error_below = []

        #for each sigma
        for sigma_index in range( len(sigma_levels) ):

            sigma = sigma_levels[sigma_index]

            error_above.append([value + sigma*value_error for value, value_error in zip(values, values_error)])
            error_below.append([value - sigma*value_error for value, value_error in zip(values, values_error)])

            if plot_type == "step":

                temp_error_above = []
                temp_error_below = []



                #all but the last
                for index in range(len(error_above[sigma_index]) - 1):

                    temp_error_above.append(error_above[sigma_index][index])
                    temp_error_above.append(error_above[sigma_index][index+1])

                    temp_error_below.append(error_below[sigma_index][index])
                    temp_error_below.append(error_below[sigma_index][index+1])

                #temp_error_above.append(error_above[sigma_index][-1])
                #temp_error_below.append(error_below[sigma_index][-1])

                error_above[sigma_index] = temp_error_above
                error_below[sigma_index] = temp_error_below

        if plot_type == "step":

            error_times = []


            # all but the last
            for index in range(len(times) - 1):
                error_times.append(times[index])
                error_times.append(times[index])



        else:

            error_times = times

        return [ error_times, error_below, error_above]

    def graphEnergy(self, energy_ax, timestep_index, synced_data, legend=False,type="Flux",zone=1, cell=-1, initial_difference=False, initial_difference_log = False,
                    marker="", uncertainty=False, sigma_levels=[1, 2, 3],uncertainty_label = False, initial_difference_log_sign="+"):

        max_value = 0
        min_value = 0
        max_energy = 0
        min_energy = 0


        energy_ax.grid(lw=3)
        pyplot.xlabel('Energy [MeV]', fontsize=self._label_font_size)
        pyplot.ylabel('Magnitude [unitless]', fontsize=self._label_font_size)

        energy_ax.set_xscale('log')

        if not initial_difference:

            energy_ax.set_yscale('log')

        [energies, values, uncertainty_values ] = self.getEnergyData(synced_data, timestep_index,type,zone,cell,initial_difference, initial_difference_log, initial_difference_log_sign)

        color_index = 0

        for run in self._ordered_labels:

            if not run in values:
                color_index += 1
                continue

            if uncertainty :

                [error_bins, error_below, error_above] = self.getUncertainty( energies[run], values[run],uncertainty_values[run],plot_type="step", sigma_levels = sigma_levels)


                for index in range(len(error_below)):

                    alpha = 0.4 - 0.3 * index / len(error_above)

                    if uncertainty_label:
                        energy_ax.fill_between(error_bins, error_below[index], error_above[index],facecolor=self._colors[color_index % len(self._colors)], alpha=alpha, label=str(sigma_levels[index]) + " $\sigma$")

                    else:
                        energy_ax.fill_between(error_bins, error_below[index], error_above[index],facecolor=self._colors[color_index % len(self._colors)], alpha=alpha)


            #some runs don't have tally energy data
            if run in energies and run in values:

                energy_ax.step(energies[run], values[run], color=self._colors[color_index % len(self._colors)], lw=self._line_width, label=self._labels[run], marker=marker, where="pre")

                if not uncertainty:

                    current_max_value = max(values[run])
                    current_min_value = min(values[run])

                else:

                    max_sigma_index = sigma_levels.index(max(sigma_levels))
                    current_max_value = max(error_above[max_sigma_index])
                    current_min_value = min(error_below[max_sigma_index])


                if (current_max_value > max_value):
                    max_value = current_max_value

                if (current_min_value < min_value or min_value == 0):
                    min_value = current_min_value

                current_max_energy = max(energies[run])
                current_min_energy = min(energies[run])

                if (current_max_energy > max_energy):
                    max_energy = current_max_energy

                if (current_min_energy < min_energy or min_energy == 0):
                    min_energy = current_min_energy

            color_index += 1

        if legend:
            energy_ax.legend(loc=1, ncol=1, fontsize=self._legend_font_size)

        if not initial_difference:

            if max_value > 0:

                min_allowable_axis_value = 10 ** math.floor(math.log10(max_value / 8))
                energy_ax.axis([min_energy, max_energy, min_allowable_axis_value, max_value])

        if initial_difference_log:
            energy_ax.set_yscale("log")


        return [ min_energy, max_energy, min_value, max_value]

    def getEnergyData(self, synced_data, time_index, type="Flux",zone=1, cell=1, initial_difference=False, initial_difference_log = False, initial_difference_log_sign="+"):

        energy_bins = {}
        energy_values = {}
        energy_uncertainty = {}

        tally_key_space = ""

        #for each run
        for run_name in self._labels:

            if cell > 1:

                # create the tally key
                tally_key = tally_key_space + type + "-" + str(zone) + "-" + str(cell)

                #ignore the time key
                if run_name == 'time':
                    continue

                if not tally_key in synced_data[run_name]['tallies']:

                    # in older builds there were spaces in the tally key index
                    tally_key = " " + tally_key

                    if not tally_key in synced_data[run_name]['tallies']:
                        continue

                    else:
                       tally_key_space = " "

                tally_data = synced_data[run_name]['tallies'][tally_key]

            else:


                # create the tally key
                tally_key = type + "-" + str(zone) + "-" + str(1)

                # ignore the time key
                if run_name == 'time':
                    continue

                if not tally_key in synced_data[run_name]['tallies']:

                    #in older builds there were spaces in the tally key index
                    tally_key = " " + tally_key

                    if not tally_key in synced_data[run_name]['tallies']:
                        continue

                    else:
                        tally_key_space = " "

                tally_data = synced_data[run_name]['tallies'][tally_key]

                current_cell = 2

                # create the tally key
                tally_key = tally_key_space + type + "-" + str(zone) + "-" + str(current_cell)

                while tally_key in synced_data[run_name]['tallies']:

                    zipped_tallies = zip(tally_data[2], synced_data[run_name]['tallies'][tally_key][2], tally_data[1], synced_data[run_name]['tallies'][tally_key][1])

                    zip_index = 0
                    for zip_tally in zipped_tallies:

                        [ current_sigma, additional_tally_sigma, current_value, additional_tally ] = zip_tally

                        for energy_index in range( len(current_value) ):

                            try:

                                tally_data[2][zip_index][energy_index] =  ((current_value[energy_index] * current_sigma[energy_index]) ** 2 + ( additional_tally[energy_index] * additional_tally_sigma[energy_index] )** 2) ** 0.5/(current_value[energy_index] + additional_tally[energy_index] )
                                tally_data[1][zip_index][energy_index] =  current_value[energy_index] + additional_tally[energy_index]
                            except:

                                pass

                        zip_index += 1
                    current_cell += 1
                    tally_key = tally_key_space + type + "-" + str(zone) + "-" + str(current_cell)

            times = synced_data[run_name]['time']
            number_timesteps_in_run = len(times)

            starting_total = sum(tally_data[1][0])
            current_total =  0
            number_tallies = len(tally_data[0][0])

            #if we are in the current run time range
            if number_timesteps_in_run - 1 >= time_index :

                current_total = sum(tally_data[1][time_index])
                energy_bins[run_name] = tally_data[0][time_index]
                energy_values[run_name] = [number_tallies * value / current_total for value in tally_data[1][time_index]]
                uncertainty_percent = tally_data[2][time_index]
                energy_uncertainty[run_name] = [ value*uncertainty for value, uncertainty in zip(energy_values[run_name], uncertainty_percent) ]

            #if not use the last value available
            else:


                current_total = sum(tally_data[1][-1])
                energy_bins[run_name] = tally_data[0][-1]
                energy_values[run_name] = [ number_tallies * value/current_total for value in tally_data[1][-1] ]
                uncertainty_percent = tally_data[2][-1]
                energy_uncertainty[run_name] = [ value * uncertainty for value, uncertainty in zip(energy_values[run_name], uncertainty_percent)]

            if initial_difference:

                for bin_index in range(0, len(energy_values[run_name]) ):

                    starting_value = number_tallies*tally_data[1][0][bin_index]/starting_total
                    current_value = energy_values[run_name][bin_index]
                    energy_values[run_name][bin_index] = (current_value - starting_value)

                    starting_sigma = tally_data[2][0][bin_index]*starting_value
                    current_sigma = energy_uncertainty[run_name][bin_index]
                    combined_sigma = (starting_sigma**2 + current_sigma**2)**0.5

                    energy_uncertainty[run_name][bin_index] = combined_sigma

                if initial_difference_log:

                    # zero out anything that is negative
                    if initial_difference_log_sign == "+":

                        for index in  range( len(energy_values[run_name])):


                            if energy_values[run_name][index] < 0:
                                energy_values[run_name][index] = 0
                                energy_uncertainty[run_name][index] = 0

                    # zero out anything positive and absolute value
                    else:

                        for index in range(len(energy_values[run_name])):

                            if energy_values[run_name][index] > 0:
                                energy_values[run_name][index] = 0
                                energy_uncertainty[run_name][index] = 0
                            else:
                                energy_values[run_name][index] *= -1


                else:
                    energy_values[run_name] = [float(value) for value in energy_values[run_name] ]
                    energy_uncertainty[run_name] = [float(value) for value in energy_uncertainty[run_name] ]

            #This is here because sometimes the last tally value happened to be recoreded as the sum of all tally values
            #This bit of code "resets" the last value to the second to last value
            if( abs(energy_values[run_name][-1]) > abs(10 * energy_values[run_name][-2] )):
                energy_values[run_name][-1] = energy_values[run_name][-2]

        return [energy_bins, energy_values, energy_uncertainty]

    '''def barGraphAttribute(self,ax, current_time, column, yscale = "linear", legend = False, snapshot_time=2 ):

        data = []
        labels = []
        indicies = []

        index_counter = 1
        run_counter = 0
        bar_colors = []



        for run_name in self._labels:

            data_value = float(synced_data)

            label = self._labels[result.getFolderName()]
            data.append(values[time_index])
            labels.append(label)
            indicies.append(index_counter)
            index_counter += 1
            bar_colors.append(self._colors[run_counter % len(self._colors)])
            run_counter += 1

        bar = ax.bar(indicies, data, align='center')

        for index in range(len(bar_colors)):
            bar[index].set_color(bar_colors[index])

        ax.set_ylabel('300 to 3000 K Worth [pcm]', fontsize=self._label_font_size)
        ax.set_xticklabels([""] + labels)
        ax.grid(lw=3, which='major', axis="y")
        ax.grid(lw=1, which='minor', axis='y')
        pyplot.xticks(rotation=40)'''

    def getMaxTallyDifferentialChange(self, synced_data, type="Flux",zone=1, cell=1 ):

        max_differential = 0
        min_differential = 1e100

        for run_name in self._labels:

            tally_key = type + "-" + str(zone) + "-" + str(cell)

            #some runds don't have tallies taken
            if run_name == 'time':
                continue

            if not tally_key in synced_data[run_name]['tallies']:

                #older runs have a space in the tally key
                tally_key = " " + tally_key

                if not tally_key in synced_data[run_name]['tallies']:

                    continue

            tally_values = synced_data[run_name]['tallies'][tally_key][1]
            starting_total = sum(tally_values[0])

            for time_index in range(0, len(tally_values) ):

                current_total = sum(tally_values[time_index])

                for bin_index in range(len(tally_values[time_index]) -1):  #skip the last value for the screwed up tally total at end

                    number_energies = len(tally_values[0])
                    starting_value = number_energies * tally_values[0][bin_index]  / starting_total
                    current_value = number_energies * tally_values[time_index][bin_index]  / current_total
                    differential = (current_value - starting_value)

                    if(differential > max_differential):

                        max_differential = differential

                    if (differential < min_differential):

                        min_differential = differential

        return [min_differential, max_differential]

