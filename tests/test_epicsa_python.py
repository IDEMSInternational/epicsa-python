# =================================================================
#
# Authors: IDEMS International, Stephen Lloyd
#
# Copyright (c) 2023, E-PICSA Project
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# =================================================================
"""Provides a set of tests for the `epicsa` module.

The tests in this module:
  - Aim to verify that the wrapper functions in the `epicsa` module 
    generate output that is equivalent to calling the R function directly.
  - Are based on the tests in the `epicsawrap` R package.
  - Do not try to validate the correctness of the R functions (this is the job 
    of the `epicsawrap` R package tests).

If we want to add extra tests, then we should call the equivalent R functions 
directly and verify that the output is equivalent to the wrapper function. 
We can then save the Python output as the expected output for future test runs.
Here are some R code examples: TODO
```
library('cdms.products')
niger50 <- daily_niger %>%
  dplyr::filter(year == 1950)

# climatic_extremes
climatic_extremes010 <- climatic_extremes(data=niger50,  date_time="date",  
        year="year",  month="month",  to="monthly",  station="station_name",  
        elements=c("tmax"),  max_val=TRUE,  min_val=TRUE)

# histogram_plot
agades <- niger50 %>%
  dplyr::filter(station_name == "Agades")
t1 <- histogram_plot(data = agades, date_time = "date", 
                     elements = c("tmin", "tmax"), facet_by = "elements")

#inventory_plot
mydata <- read.csv("C:\\Users\\steph\\OneDrive\\Desktop\\FirefoxDownloads\\observationFinalMinimal.csv")
df <- data.frame(mydata)
df$obsDatetime <- as.Date(df$obsDatetime,format="%d/%m/%Y %H:%M")
r_plot <- inventory_plot(data=df, station="ï..recordedFrom", 
        elements=c("obsValue"),date_time="obsDatetime")
ggplot2::ggsave(filename="inventory_plot01.jpg", plot=r_plot, device="jpeg", 
        path="C:\\Users\\steph\\OneDrive\\Desktop\\FirefoxDownloads", 
        width = 25,  height = 20,  units = "cm")

#export_cdt
yearly_niger <- daily_niger %>% dplyr::group_by(station_name, year) %>% 
        dplyr::summarise(mean_rain = mean(rain))
output_CPT(data = yearly_niger, lat_lon_data = stations_niger, 
        station_latlondata = "station_name", latitude = "lat", longitude = "long", 
        station = "station_name", year = "year", element = "mean_rain")
actual <- export_cdt(
  data=daily_niger,
  date_time="date",
  element="rain",
  station="station_name",
  latitude="lat",
  longitude="long",
  altitude="alt",
  metadata=stations_niger
)
```
"""
import json
import os
from collections import OrderedDict
from epicsa_python import epicsa

TEST_DIR = os.path.dirname(__file__)
output_path_actual: str = os.path.join(TEST_DIR, "results_actual")


def test_annual_rainfall_summaries():
    actual = epicsa.annual_rainfall_summaries(country="zm", station_id="01122")
    assert __is_expected_ordered_dict(
        actual, "annual_rainfall_summaries_actual010.json"
    )

    actual = epicsa.annual_rainfall_summaries(
        country="zm",
        station_id="01122",
        summaries=["annual_rain", "start_rains", "end_rains"],
    )
    assert __is_expected_ordered_dict(
        actual, "annual_rainfall_summaries_actual020.json"
    )

    actual = epicsa.annual_rainfall_summaries(
        country="zm", station_id="01122", summaries=["annual_rain"]
    )
    assert __is_expected_ordered_dict(
        actual, "annual_rainfall_summaries_actual030.json"
    )


def test_crop_success_probabilities():
    actual = epicsa.crop_success_probabilities(country="zm", station_id="16")
    assert __is_expected_ordered_dict(
        actual, "crop_success_probabilities_actual010.json"
    )


def test_annual_temperature_summaries():
    actual = epicsa.annual_temperature_summaries(country="zm", station_id="16")
    assert __is_expected_ordered_dict(
        actual, "annual_temperature_summaries_actual010.json"
    )


def test_monthly_temperature_summaries():
    actual = epicsa.monthly_temperature_summaries(country="zm", station_id="16", summaries=["mean_tmin"])
    assert __is_expected_ordered_dict(
        actual, "monthly_temperature_summaries_actual010.json"
    )


def __get_output_file_paths(file_name: str):
    output_file_actual: str = os.path.join(TEST_DIR, "results_actual", file_name)
    output_file_expected: str = os.path.join(
        TEST_DIR, "results_expected", file_name.replace("actual", "expected")
    )
    return output_file_actual, output_file_expected


def __is_expected_ordered_dict(actual: OrderedDict, file_name: str) -> bool:
    # integration of data frame into Json is based on example at
    # https://stackoverflow.com/questions/26244323/convert-pandas-dataframe-to-json-as-element-of-larger-data-structure
    actual_as_json = json.dumps(
        actual,
        default=lambda dataframe: json.loads(dataframe.to_json()),
        indent=4,
    )

    output_file_actual, output_file_expected = __get_output_file_paths(file_name)

    with open(output_file_actual, "w") as f:
        f.write(actual_as_json)

    with open(output_file_expected, "r") as f:
        expected = f.read()

    return actual_as_json == expected
