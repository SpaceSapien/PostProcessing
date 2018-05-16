import ResultsList
import Result
import os
import re
import math



def homogenousMultiScale(run_name):

    base_dir = "/home/chris/Desktop/Results/Multiscale/"
    folder_format = "^Multiscale-(.+)$"
    label_format = "$1"
    postProcessMultiple(run_name, base_dir, folder_format, label_format, energy_view=True, video_view = True, heat_flux=True, power_scale="linear",ending_time=0.45)


def thermalStudy(run_name):

    base_dir = "/home/chris/Desktop/Results/Thermal-Study/"
    folder_format = "^thermal-(.*)$"
    label_format = "Comparison"
    postProcessMultiple(run_name, base_dir, folder_format, label_format, energy_view=True, video_view=True, ending_time=5.0)

def superFuelStudy(run_name):

    base_dir = "/home/chris/Desktop/Results/Improved-Fuel-Study/"
    folder_format = "^Fuel-(.*)$"
    label_format = "$1"
    postProcessMultiple(run_name, base_dir, folder_format, label_format, energy_view=True, video_view=True, ending_time=2.0)

def boundaryStudy(run_name):

    base_dir = "/home/chris/Desktop/Results/Boundary-Study/"
    folder_format = "^Boundary-(.+)$"
    label_format = "$1"
    postProcessMultiple(run_name, base_dir, folder_format, label_format, energy_view=True, video_view = True, heat_flux=True, power_scale="linear",ending_time=1.0)

def spectrumStudy(run_name):

    def spectrum_label_format(data):

        total_size = (1.612e-3 * 2)**3
        kernel_size = ( (4.0/3.0) * math.pi *(float(data)/2000)**3 )
        fuel_to_moderator_percent = 100*(kernel_size / total_size)
        return "%0.2f%% Fuel" % fuel_to_moderator_percent

    base_dir = "/home/chris/Desktop/Results/New-Spectrum-Study/"
    folder_format = "^spectrum-([0-9]+(.[0-9]+)?)mm.*$"

    postProcessMultiple(run_name, base_dir, folder_format, spectrum_label_format, log_start_time=0.001, prompt_neutron_lifetime_axis="log")

def particleSizeStudy(run_name):

    base_dir = "/media/DoubleSpace/Results/Thesis/Unit-Cell/"
    folder_format = "^Unit-([0-9\.]+)mm.*$"
    label_format = "Unit Size $1 mm"
    postProcessMultiple(run_name, base_dir, folder_format, label_format, energy_view=True, video_view=True, ending_time=10.0)

def enrichmentStudy(run_name):

    base_dir = "/media/DoubleSpace/Results/Thesis/Enrichment/"
    folder_format = "^enr([0-9][0-9]?)$"
    label_format = "Enrichment $1%"
    postProcessMultiple(run_name, base_dir, folder_format, label_format, energy_view=True, video_view=True, ending_time=10.0)

def reactivityStudy(run_name):

    base_dir = "/home/chris/Desktop/Results/Reactivity-Study/"
    folder_format = "^rho-([0-9]+).*$"
    label_format = "Insertion $1 cents"
    postProcessMultiple(run_name,base_dir,folder_format,label_format)

def absorberStudy(run_name):

    base_dir = "/home/chris/Desktop/Results/Absorber-Study/"
    folder_format = "^Absorber-([0-9a-zA-Z\-]+)$"
    label_format = "$1"
    postProcessMultiple(run_name, base_dir, folder_format, label_format, power_scale="linear", time_comparison=2.1866 ) #, ending_time=1.0)

def rampStudy(run_name):

    base_dir = "/home/chris/Desktop/Results/Ramp-Study/"
    folder_format = "^ramp-([0-9]+)ms.*$"
    label_format = "Ramp $1 ms"
    postProcessMultiple(run_name,base_dir,folder_format,label_format, worth_view=False, power_scale="linear")

def baseCaseStudy(run_name):

    base_dir = "/home/chris/Desktop/Results/Reference-Case/"
    folder_format = "^(Reference)$"
    label_format = "$1 Fuel"
    postProcessMultiple(run_name, base_dir, folder_format, label_format,video_view=True)

def fuelsStudy(run_name):

    base_dir = "/home/chris/Desktop/Results/Fuels-Study/"
    folder_format = "^fuel-([A-Za-z0-9]+)$"
    label_format = "$1 MW/m^3"
    postProcessMultiple(run_name, base_dir, folder_format, label_format,power_scale="linear")

def moderatorStudy(run_name):

    base_dir = "/home/chris/Desktop/Results/Moderator-Study/"
    folder_format = "^moderator-([A-Za-z0-9\)\(\-]+)$"
    label_format = "$1"
    postProcessMultiple(run_name, base_dir, folder_format, label_format,power_scale="linear")

def powerStudy(run_name):

    base_dir = "/home/chris/Desktop/Results/Power-Study/"
    folder_format = "^power-([0-9]+)$"
    label_format = "$1 MW/m$^{3}$"
    postProcessMultiple(run_name, base_dir, folder_format, label_format,power_scale="linear")

def coatingStudy(run_name):

    base_dir = "/media/chris/DoubleSpace/Results/Thesis/Thickness/"
    folder_format = "^thickness-([0-9]+)um$"
    label_format = "$1 um Coating"
    postProcessMultiple(run_name, base_dir, folder_format, label_format,power_scale="linear")

def superBaseCaseStudy(run_name):

    base_dir = "/home/chris/Desktop/Results/Reference-Super/"
    folder_format = "^reference-([0-9]+)g$"
    label_format = "$1 Groups"
    postProcessMultiple(run_name, base_dir, folder_format, label_format,power_scale="linear", time_comparison=2.1866)

def homogenousCompare(run_name):

    base_dir = "/home/chris/Desktop/Results/New-Homogenous-Comparison/"
    folder_format = "^Reference-([0-9a-zA-Z\-]+)$"
    label_format = "$1"
    postProcessMultiple(run_name, base_dir, folder_format, label_format,power_scale="linear", time_comparison=2.0 )

def otfsabStudy(run_name):

    base_dir = "/home/chris/Desktop/Results/SAB-study/"
    folder_format = "^Reference-([0-9a-zA-Z\-]+)$"
    label_format = "$1"
    postProcessMultiple(run_name, base_dir, folder_format, label_format,power_scale="log", time_comparison=0.9, ending_time=10.0 )

def referenceWorthStudy(run_name):

    base_dir = "/home/chris/Desktop/Results/Reference-Worth/"
    folder_format = "^Reference-(Worth)$"
    label_format = "$1 Groups"
    postProcessMultiple(run_name, base_dir, folder_format, label_format, power_scale="linear", time_comparison=2.0)

def superWorth(run_name):

    base_dir = "/home/chris/Desktop/Results/super-worth/"
    folder_format = "^Pitch-(2.8)mm$"
    label_format = "$1mm Pitch"
    postProcessMultiple(run_name, base_dir, folder_format, label_format, power_scale="linear", time_comparison=2.0)

def superFuel(run_name):

    base_dir = "/home/chris/Desktop/Results/Improved-Fuel/"
    folder_format = "^Fuel-(.+)$"
    label_format = "$1"
    postProcessMultiple(run_name, base_dir, folder_format, label_format,power_scale="linear", time_comparison=2.0,ending_time=2.0)

def fuelBlock(run_name):

    base_dir = "/home/chris/Desktop/Results/Fuel-Block/"
    folder_format = "^Fuel-Block-(.+)$"
    label_format = "$1"
    postProcessMultiple(run_name, base_dir, folder_format, label_format,power_scale="linear", time_comparison=2.0,ending_time=2.0, multiscale=True)


def SiC_Comparison(run_name):

    base_dir = "/media/chris/DoubleSpace/Results/Thesis/SiC-Comparison/"
    folder_format = "^Coating-(.+)$"
    label_format = "$1"
    postProcessMultiple(run_name, base_dir, folder_format, label_format, power_scale="linear", time_comparison=2.0,
                        ending_time=10.0, multiscale=True)


def postProcessMultiple(run_name,base_dir,folder_format,label_format, output_directory="Working-Dir/", heat_flux=False,
                        energy_view = True, video_view = True, still_view=True, still_view_spectrum = True, worth_view = True,
                        log_start_time=0.004, reposition=False,line_worth=False, power_scale="log",
                        prompt_neutron_lifetime_axis="linear", time_comparison=1.9, ending_time = -1,plot_initial=True, multiscale=False):

    output_directory_path = base_dir + output_directory

    OrderedFolders = {}
    OrderedKeys = []
    Results = ResultsList.ResultsList(output_directory_path, run_name, folder_format, label_format)  # type: ResultsList.ResultsList


    folders = os.listdir(base_dir)

    if len(folders) == 0:
        print(base_dir + " has no folders")
        raise


    for folder in folders:

        matches = re.match(folder_format, folder)

        if matches:

            try:

                variable = float(matches.group(1))

            except:

                variable = matches.group(1)

            finally:

                OrderedFolders[variable] = folder
                OrderedKeys.append(variable)

    OrderedKeys.sort()

    for key in OrderedKeys:
        folder = OrderedFolders[key]
        result = Result.Result(base_dir, folder)
        Results.addResult(result)

    '''
    if plot_initial:
        Results.plotInitialTemperatures(multiscale=multiscale)

    '''


    '''
    if video_view:

       Results.standardVideoView(75,time_axis="linear", log_start_time=log_start_time, ending_time=ending_time)

    
    if multiscale:

        Results.multiscaleVideoView(100, time_axis="log", log_start_time=log_start_time, ending_time=ending_time)

    

    if energy_view:
        Results.standardEnergyView(100, time_axis="log", log_start_time=log_start_time, uncertainty=True, ending_time=ending_time)
    '''

    '''
    Results.plotDelayedPrecursors()


    if still_view:

       Results.stillViewMultipleGraphs( time_axis="log", log_start_time=log_start_time, reposition=reposition, power_scale=power_scale, time_comparison=time_comparison, ending_time=ending_time ) #, time_base="Prompt Neutron Lifetime")
       Results.stillViewSingle(time_axis="log", log_start_time=log_start_time, reposition=reposition, power_scale=power_scale, time_comparison=time_comparison, ending_time=ending_time)


    if heat_flux:
        Results.boundaryHeatFluxPlot(time_axis="log", log_start_time=log_start_time,reposition=reposition, ending_time=ending_time)


    if still_view_spectrum:

        Results.stillViewSpectrumSingle(time_axis="log", log_start_time=log_start_time, reposition=reposition, prompt_neutron_lifetime_axis=prompt_neutron_lifetime_axis, time_comparison=time_comparison)
        #Results.stillViewAbsorption(time_axis="log", log_start_time=log_start_time, reposition=reposition,     prompt_neutron_lifetime_axis=prompt_neutron_lifetime_axis,time_comparison=time_comparison)


    '''
    if worth_view :
        Results.worthGraphs(line_worth)
        #Results.multiWorthGraphs(line_worth)



    Results.plotBasicTemperatureAverages(time_axis="linear", log_start_time=log_start_time, ending_time=ending_time )

    '''if multiscale:

        Results.plotMicroCell(time_axis="log", log_start_time=log_start_time)'''




if __name__ == "__main__":


    #reference = "Reference-Study"
    #baseCaseStudy(reference)

    #run_name = "Spectrum-Study-2"
    #spectrumStudy(run_name)

    #run_name = "Enrichment-Study"
    #enrichmentStudy(run_name)

    run_name = "Unit-Size-Study"
    particleSizeStudy(run_name)

    #thermalStudy("Test")

    #run_name = "Boundary-Study"
    #boundaryStudy(run_name)

    #run_name = "Reactivity-Study"
    #reactivityStudy(run_name)

    #run_name = "Ramp-Study"
    #rampStudy(run_name)

    #run_name = "Fuels-Study"
    #fuelsStudy(run_name)

    #run_name = "Coating-Study"
    #coatingStudy(run_name)

    #run_name = "Power-Study"
    #powerStudy(run_name)

    #run_name = "Moderator-Study"
    #moderatorStudy(run_name)

    #run_name = "Super-Study"
    #superBaseCaseStudy(run_name)

    #run_name = "Reference-Heterogeneous"
    #homogenousCompare(run_name)

    #run_name = "Absorber-Study"
    #absorberStudy(run_name)

    #run_name = "Super-Worth"
    #superWorth(run_name)

    #run_name = "Reference-Worth"
    #referenceWorthStudy(run_name)

    #run_name = "Multiscale-Study"
    #homogenousMultiScale(run_name)

    #run_name = "super-fuel-2"
    #superFuel(run_name)

    #run_name = "fuel-block"
    #fuelBlock(run_name)

    #run_name = "otfsab"
    #otfsabStudy(run_name)

    #run_name = "SiC-Comparison"
    #SiC_Comparison(run_name)