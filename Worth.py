import CSVClasses
import matplotlib.pyplot  as pyplot
from scipy import stats
import numpy as np

class WorthResults(CSVClasses.CSVDataObject):

    _type  = None

    def __init__(self, csv_data, type="fuel"):

        super(WorthResults,self).__init__(csv_data)
        self._type = type
        self.findOptimalRegression()

    def regression(self, power, ordered_temperature, ordered_reactivity, type="fuel"):

            modified_temp = [ (temp)**power for temp in ordered_temperature ]
            [slope, intercept, r_value, p_value, std_err] = stats.linregress(modified_temp, ordered_reactivity)
            return [slope, intercept, r_value, p_value, std_err]

    def findOptimalRegression(self):

        if self._type == "fuel":
            temperature = self.getColumnData("Fuel Temperature [K]")
        else:
            temperature = self.getColumnData("Non Fissile Temperature [K]")

        eigenvalues = self.getColumnData("K-eigenvalue")

        temperature = [ float(value) for value in temperature ]
        eigenvalues = [ float(value) for value in eigenvalues ]

        max_eigenvalue = max(eigenvalues)
        data = sorted(zip(eigenvalues, temperature))
        #limit the maximum temperature to 3300 K
        data = [(y, x) for (y, x) in data if x < 3300]
        self._ordered_temperatures = [x for (y, x) in data]
        self._ordered_reactivity = [10**5 * (y - max_eigenvalue) / (max_eigenvalue) for (y, x) in data]
        self._ordered_dollars = [(y - max_eigenvalue) / (max_eigenvalue * 0.0065) for (y, x) in data]

        power_range = np.linspace(0, 0.5, 1200)
        regressions = []

        for power in power_range:

            [slope, intercept, r_value, p_value, std_err] = self.regression(power, self._ordered_temperatures, self._ordered_reactivity)
            regressions.append({'power':power, 'r2':r_value**2, 'slope' : slope, 'intercept' : intercept})


        regressions.sort(key=lambda x:x['r2'],reverse=True)
        self._best_regression = regressions[0]





