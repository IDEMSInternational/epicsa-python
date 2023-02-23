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

import filecmp
import os

from pandas import DataFrame, read_csv

from epicsa_python import epicsa

# from opencdms_process.process.rinstat import epicsa

TEST_DIR = os.path.dirname(__file__)
output_path_actual: str = os.path.join(TEST_DIR, "results_actual")


def test_annual_rainfall_summaries():
    actual = epicsa.annual_rainfall_summaries("test1")

    assert __is_expected_dataframe(
        data=actual, file_name="annual_rainfall_summaries_actual010.csv"
    )


def test_climatic_extremes():
    data_file: str = os.path.join(TEST_DIR, "data", "niger50.csv")
    niger50 = read_csv(
        data_file,
        parse_dates=["date"],
        dayfirst=True,
        na_values="NA",
    )

    # test that max and min are correctly calculated
    actual = epicsa.climatic_extremes(
        data=niger50,
        date_time="date",
        year="year",
        month="month",
        to="monthly",
        station="station_name",
        elements=["tmax"],
        max_val=True,
        min_val=True,
    )
    assert __is_expected_dataframe(
        data=actual, file_name="climatic_extremes_actual010.csv"
    )

    # test that Date cols are correctly calculated
    actual = epicsa.climatic_extremes(
        data=niger50,
        date_time="date",
        year="year",
        month="month",
        to="monthly",
        station="station_name",
        elements=["tmax"],
        max_val=True,
        first_date=True,
        n_dates=True,
        last_date=True,
    )
    assert __is_expected_dataframe(
        data=actual, file_name="climatic_extremes_actual020.csv"
    )


def test_climatic_missing():
    data_file: str = os.path.join(TEST_DIR, "data", "daily_niger.csv")
    daily_niger = read_csv(
        data_file,
        parse_dates=["date"],
        dayfirst=True,
        na_values="NA",
    )

    # Summarising missing data in the rainfall, temperature, and sun columns
    # climatic_missing(data = daily_niger, date_time = "date",
    #                  elements = c("rain", "tmax", "tmin", "sunh"),
    #                  station_id = "station_name")
    actual = epicsa.climatic_missing(
        data=daily_niger,
        date_time="date",
        elements=["rain", "tmax", "tmin", "sunh"],
        station_id="station_name",
    )
    assert __is_expected_dataframe(
        data=actual, file_name="climatic_missing_actual010.csv"
    )


def test_climatic_summary():
    # test approx 29000 row dataframe with missing values
    data_file: str = os.path.join(TEST_DIR, "data", "dodoma.csv")
    dodoma = read_csv(
        data_file,
        parse_dates=["date"],
        dayfirst=True,
        na_values="NA",
    )

    actual = epicsa.climatic_summary(
        data=dodoma,
        date_time="date",
        elements=["rain", "tmax"],
        summaries={"mean": "mean", "sd": "sd"},
        na_rm=True,
        to="overall",
    )
    assert __is_expected_dataframe(
        data=actual, file_name="climatic_summary_actual005.csv"
    )

    actual = epicsa.climatic_summary(
        data=dodoma,
        date_time="date",
        elements=["rain", "tmax"],
        summaries={"mean": "mean", "sd": "sd", "n_na": "naflex::na_n"},
        na_rm=True,
        to="monthly",
    )
    assert __is_expected_dataframe(
        data=actual, file_name="climatic_summary_actual010.csv"
    )

    # test approx 55000 row dataframe with missing values

    data_file: str = os.path.join(TEST_DIR, "data", "rwanda.csv")
    rwanda = read_csv(
        data_file,
        parse_dates=["date"],
        dayfirst=True,
        na_values="NA",
    )

    actual = epicsa.climatic_summary(
        data=rwanda,
        date_time="date",
        elements=["precip", "tmp_min"],
        station="station_id",
        summaries={"mean": "mean", "sd": "sd"},
        na_prop=0,
        to="monthly",
    )
    assert __is_expected_dataframe(
        data=actual, file_name="climatic_summary_actual020.csv"
    )

    # run selection of package `testhat` tests

    data_file: str = os.path.join(TEST_DIR, "data", "niger50.csv")
    niger50 = read_csv(
        data_file,
        parse_dates=["date"],
        dayfirst=True,
        na_values="NA",
    )

    actual = epicsa.climatic_summary(
        data=niger50,
        date_time="date",
        year="year",
        month="month",
        by="station_name",
        elements=["rain"],
        station="station_name",
        to="monthly",
        summaries={"mean": "mean", "st_dv": "sd", "n_na": "naflex::na_n"},
    )
    assert __is_expected_dataframe(
        data=actual, file_name="climatic_summary_actual030.csv"
    )

    # test with data used in demo

    data_file: str = os.path.join(TEST_DIR, "data", "observationFinalMinimal.csv")
    observationFinalMinimal = read_csv(
        data_file,
        parse_dates=["obsDatetime"],
        dayfirst=True,
        na_values="NA",
    )
    # climatic_summary(data = obs, date_time = "obsDatetime", station = "ï..recordedFrom", elements = "obsValue",
    #       to = "annual", summaries = c(mean = "mean", max = "max", min = "min"))
    actual = epicsa.climatic_summary(
        data=observationFinalMinimal,
        date_time="obsDatetime",
        elements=["obsValue"],
        station="recordedFrom",
        to="annual",
        summaries={"mean": "mean", "max": "max", "min": "min"},
    )
    assert __is_expected_dataframe(
        data=actual, file_name="climatic_summary_actual040.csv"
    )

    # test summaries_params
    actual = epicsa.climatic_summary(
        data=dodoma,
        date_time="date",
        elements=["rain", "tmax"],
        summaries={"mean": "mean", "sd": "sd"},
        na_rm=True,
        to="overall",
        summaries_params={"mean": {"trim": 0.5}},
    )
    assert __is_expected_dataframe(
        data=actual, file_name="climatic_summary_actual050.csv"
    )


def test_export_cdt():
    data_file: str = os.path.join(TEST_DIR, "data", "daily_summary_data.csv")
    daily_summary_data = read_csv(
        data_file,
        parse_dates=["date"],
        na_values="NA",
    )

    data_file = os.path.join(TEST_DIR, "data", "stations_niger.csv")
    stations_niger = read_csv(
        data_file,
        dayfirst=True,
        na_values="NA",
    )

    # export_cdt(data = daily_summary_data, station = "station_name",
    #            element = "sum", latitude = "lat", longitude = "long",
    #            altitude = "alt", type =  "daily", date_time = "date",
    #            metadata = stations_niger,
    #            file_path = "C:\\Users\\steph\\OneDrive\\Desktop\\FirefoxDownloads\\export_cdt_expected010.csv")
    output_file_actual: str = os.path.join(
        TEST_DIR, "results_actual", "export_cdt_actual010.csv"
    )
    epicsa.export_cdt(
        data=daily_summary_data,
        station="station_name",
        element="sum",
        latitude="lat",
        longitude="long",
        altitude="alt",
        type="daily",
        date_time="date",
        metadata=stations_niger,
        file_path=output_file_actual,
    )
    assert __is_expected_file("export_cdt_actual010.csv")


def test_export_cdt_daily():
    data_file: str = os.path.join(TEST_DIR, "data", "daily_niger.csv")
    daily_niger = read_csv(
        data_file,
        parse_dates=["date"],
        dayfirst=True,
        na_values="NA",
    )

    data_file = os.path.join(TEST_DIR, "data", "stations_niger.csv")
    stations_niger = read_csv(
        data_file,
        dayfirst=True,
        na_values="NA",
    )

    # export_cdt_daily(data = daily_niger, station = "station_name", element = "rain", type = "daily",
    #              date_time = "date", latitude = "lat", longitude = "long", altitude = "alt",
    #              metadata = stations_niger,
    #              file_path = "C:\\Users\\steph\\OneDrive\\Desktop\\FirefoxDownloads\\export_cdt_daily_expected010.csv")
    output_file_actual: str = os.path.join(
        TEST_DIR, "results_actual", "export_cdt_daily_actual010.csv"
    )
    epicsa.export_cdt_daily(
        data=daily_niger,
        station="station_name",
        element="rain",
        latitude="lat",
        longitude="long",
        altitude="alt",
        type="daily",
        date_time="date",
        metadata=stations_niger,
        file_path=output_file_actual,
    )
    assert __is_expected_file("export_cdt_daily_actual010.csv")


def test_export_cdt_dekad():
    data_file: str = os.path.join(TEST_DIR, "data", "summary_data.csv")
    summary_data = read_csv(
        data_file,
        parse_dates=["date"],
        dayfirst=True,
        na_values="NA",
    )

    data_file = os.path.join(TEST_DIR, "data", "stations_niger.csv")
    stations_niger = read_csv(
        data_file,
        dayfirst=True,
        na_values="NA",
    )

    # export_cdt_dekad(data = summary_data, station = "station_name", element = "sum_tmax",
    #             date_time = "date", latitude = "lat", longitude = "long", altitude = "alt",
    #             dekad = "dekad_date", metadata = stations_niger,
    #             file_path = "C:\\Users\\steph\\OneDrive\\Desktop\\FirefoxDownloads\\export_cdt_dekad_expected010.csv")

    output_file_actual: str = os.path.join(
        TEST_DIR, "results_actual", "export_cdt_dekad_actual010.csv"
    )
    epicsa.export_cdt_dekad(
        data=summary_data,
        station="station_name",
        element="sum_tmax",
        latitude="lat",
        longitude="long",
        altitude="alt",
        dekad="dekad_date",
        date_time="date",
        metadata=stations_niger,
        file_path=output_file_actual,
    )
    assert __is_expected_file("export_cdt_dekad_actual010.csv")


def test_export_climat_messages():
    pass  # TODO test requested in https://github.com/IDEMSInternational/cdms.products/issues/86


def test_export_climdex():
    data_file: str = os.path.join(TEST_DIR, "data", "daily_niger.csv")
    daily_niger = read_csv(
        data_file,
        parse_dates=["date"],
        dayfirst=True,
        na_values="NA",
    )

    # export_climdex(data = daily_niger, date = "date", prcp = "rain", tmax = "tmax", tmin = "tmin",
    #       file_path = "C:\\Users\\steph\\OneDrive\\Desktop\\FirefoxDownloads\\export_climdex_expected010")
    output_file_actual: str = os.path.join(
        TEST_DIR, "results_actual", "export_climdex_actual010"
    )
    epicsa.export_climdex(
        data=daily_niger,
        date="date",
        prcp="rain",
        tmax="tmax",
        tmin="tmin",
        file_path=output_file_actual,
    )
    assert __is_expected_file("export_climdex_actual010.csv")


def test_export_geoclim():
    data_file: str = os.path.join(TEST_DIR, "data", "summary_data_dekad.csv")
    summary_data_dekad = read_csv(
        data_file,
        na_values="NA",
    )

    data_file = os.path.join(TEST_DIR, "data", "stations_niger.csv")
    stations_niger = read_csv(
        data_file,
        dayfirst=True,
        na_values="NA",
    )

    # export_geoclim(data = summary_data, year = "year",
    #    station_id = "station_name",
    #    type_col = "dekad",
    #    element = "mean_rain", metadata = stations_niger,
    #    join_by = "station_name",
    #    latitude = "lat", longitude = "long",
    #    file_path = "C:\\Users\\steph\\OneDrive\\Desktop\\FirefoxDownloads\\export_geoclim_expected010.csv")
    output_file_actual: str = os.path.join(
        TEST_DIR, "results_actual", "export_geoclim_actual010"
    )
    epicsa.export_geoclim(
        data=summary_data_dekad,
        year="year",
        station_id="station_name",
        type_col="dekad",
        element="mean_rain",
        metadata=stations_niger,
        join_by="station_name",
        latitude="lat",
        longitude="long",
        file_path=output_file_actual,
    )
    assert __is_expected_file("export_geoclim_actual010.csv")


def test_export_geoclim_dekad():
    # TODO This test can be added when https://github.com/IDEMSInternational/cdms.products/issues/87 is resolved
    pass


def test_export_geoclim_month():
    data_file: str = os.path.join(
        TEST_DIR, "data", "summary_data_export_geoclim_month.csv"
    )
    summary_data = read_csv(
        data_file,
        na_values="NA",
    )

    data_file = os.path.join(TEST_DIR, "data", "stations_niger.csv")
    stations_niger = read_csv(
        data_file,
        dayfirst=True,
        na_values="NA",
    )

    # export_geoclim_month(data = summary_data, year = "year", month = "month",
    #   station_id = "station_name",
    #   element = "mean_rain", metadata = stations_niger,
    #   join_by = "station_name",
    #   latitude = "lat", longitude = "long",
    #  file_path = "C:\\Users\\steph\\OneDrive\\Desktop\\FirefoxDownloads\\export_geoclim_month_expected010.csv")
    output_file_actual: str = os.path.join(
        TEST_DIR, "results_actual", "export_geoclim_month_actual010.csv"
    )
    epicsa.export_geoclim_month(
        data=summary_data,
        year="year",
        month="month",
        station_id="station_name",
        element="mean_rain",
        metadata=stations_niger,
        join_by="station_name",
        latitude="lat",
        longitude="long",
        file_path=output_file_actual,
    )
    assert __is_expected_file("export_geoclim_month_actual010.csv")


def test_export_geoclim_pentad():
    # TODO This test can be added when https://github.com/IDEMSInternational/cdms.products/issues/87 is resolved
    pass


def test_histogram_plot():
    data_file: str = os.path.join(TEST_DIR, "data", "niger50.csv")
    niger50 = read_csv(
        data_file,
        parse_dates=["date"],
        dayfirst=True,
        na_values="NA",
    )

    data_file: str = os.path.join(TEST_DIR, "data", "agades.csv")
    agades = read_csv(
        data_file,
        parse_dates=["date"],
        dayfirst=True,
        na_values="NA",
    )

    # test_that("single element facet by station graphs are correct", {
    #   t1 <- histogram_plot(data = niger50, date_time = "date", elements = "tmax",
    #                         station = "station_name", facet_by = "stations")
    file_name_actual: str = "histogram_plot_actual010.jpg"
    epicsa.histogram_plot(
        path=output_path_actual,
        file_name=file_name_actual,
        data=niger50,
        date_time="date",
        elements=["tmax"],
        station="station_name",
        facet_by="stations",
    )
    assert __is_expected_file(file_name_actual)

    # test_that("single element single station graphs are correct", {
    #   t1 <- histogram_plot(data = agades, date_time = "date", elements = "tmax",
    #                         facet_by = "none")
    file_name_actual: str = "histogram_plot_actual020.jpg"
    epicsa.histogram_plot(
        path=output_path_actual,
        file_name=file_name_actual,
        data=agades,
        date_time="date",
        elements=["tmax"],
        facet_by="none",
    )
    assert __is_expected_file(file_name_actual)

    # test_that("single element colour by station no facet graphs are correct", {
    #   t1 <- histogram_plot(data = niger50, date_time = "date", elements = "tmax",
    #                         station = "station_name", facet_by = "none")
    file_name_actual: str = "histogram_plot_actual030.jpg"
    epicsa.histogram_plot(
        path=output_path_actual,
        file_name=file_name_actual,
        data=niger50,
        date_time="date",
        elements=["tmax"],
        station="station_name",
        facet_by="none",
    )
    assert __is_expected_file(file_name_actual)

    # test_that("multiple element single station graphs are correct", {
    #   t1 <- histogram_plot(data = agades, date_time = "date",
    #                         elements = c("tmin", "tmax"),
    #                         facet_by = "none")
    file_name_actual: str = "histogram_plot_actual040.jpg"
    epicsa.histogram_plot(
        path=output_path_actual,
        file_name=file_name_actual,
        data=agades,
        date_time="date",
        elements=["tmin", "tmax"],
        facet_by="none",
    )
    assert __is_expected_file(file_name_actual)

    # test_that("multiple element single station facet by elements graphs are correct", {
    #   t1 <- histogram_plot(data = agades, date_time = "date",
    #                         elements = c("tmin", "tmax"),
    #                         facet_by = "elements")
    file_name_actual: str = "histogram_plot_actual050.jpg"
    epicsa.histogram_plot(
        path=output_path_actual,
        file_name=file_name_actual,
        data=agades,
        date_time="date",
        elements=["tmin", "tmax"],
        station="station_name",
        facet_by="elements",
    )
    assert __is_expected_file(file_name_actual)

    # test_that("multiple element & multiple stations with both as facet_by graphs are correct", {
    #   t1 <- histogram_plot(data = niger50, date_time = "date",
    #                         station = "station_name",
    #                         elements = c("tmin", "tmax"),
    #                         facet_by = "stations-elements")
    file_name_actual: str = "histogram_plot_actual060.jpg"
    epicsa.histogram_plot(
        path=output_path_actual,
        file_name=file_name_actual,
        data=niger50,
        date_time="date",
        station="station_name",
        elements=["tmin", "tmax"],
        facet_by="stations-elements",
    )
    assert __is_expected_file(file_name_actual)

    # test_that("multiple element & multiple stations facet by elements graphs are correct", {
    #   t1 <- histogram_plot(data = niger50, date_time = "date",
    #                         station = "station_name",
    #                         elements = c("tmin", "tmax"),
    #                         facet_by = "elements")
    file_name_actual: str = "histogram_plot_actual070.jpg"
    epicsa.histogram_plot(
        path=output_path_actual,
        file_name=file_name_actual,
        data=niger50,
        date_time="date",
        station="station_name",
        elements=["tmin", "tmax"],
        facet_by="elements",
    )
    assert __is_expected_file(file_name_actual)

    # test_that("multiple element & multiple stations facet by stations graphs are correct", {
    #   t1 <- histogram_plot(data = niger50, date_time = "date",
    #                         station = "station_name",
    #                         elements = c("tmin", "tmax"),
    #                         facet_by = "stations")
    file_name_actual: str = "histogram_plot_actual080.jpg"
    epicsa.histogram_plot(
        path=output_path_actual,
        file_name=file_name_actual,
        data=niger50,
        date_time="date",
        station="station_name",
        elements=["tmin", "tmax"],
        facet_by="stations",
    )
    assert __is_expected_file(file_name_actual)

    # test_that("multiple element & multiple stations no facet graphs are correct", {
    #   t1 <- histogram_plot(data = niger50, date_time = "date",
    #                         station = "station_name",
    #                         elements = c("tmin", "tmax"),
    #                         facet_by = "none")
    file_name_actual: str = "histogram_plot_actual090.jpg"
    epicsa.histogram_plot(
        path=output_path_actual,
        file_name=file_name_actual,
        data=niger50,
        date_time="date",
        station="station_name",
        elements=["tmin", "tmax"],
        facet_by="none",
    )
    assert __is_expected_file(file_name_actual)


def test_inventory_plot():
    data_file: str = os.path.join(TEST_DIR, "data", "daily_niger.csv")
    daily_niger = read_csv(
        data_file,
        parse_dates=["date"],
        dayfirst=True,
        na_values="NA",
    )

    # Create an inventory plot with two elements and by station
    file_name_actual: str = "inventory_plot_actual010.jpg"
    actual = epicsa.inventory_plot(
        path=output_path_actual,
        file_name=file_name_actual,
        data=daily_niger,
        station="station_name",
        elements=["tmax", "tmin"],
        date_time="date",
    )
    assert __is_expected_file(file_name_actual)

    # Create an inventory plot by year and day of year
    file_name_actual: str = "inventory_plot_actual020.jpg"
    actual = epicsa.inventory_plot(
        path=output_path_actual,
        file_name=file_name_actual,
        data=daily_niger,
        station="station_name",
        elements=["tmax", "tmin"],
        date_time="date",
        year_doy_plot=True,
    )
    assert __is_expected_file(file_name_actual)

    # Can add in rainy/dry days into the plot
    file_name_actual: str = "inventory_plot_actual030.jpg"
    actual = epicsa.inventory_plot(
        path=output_path_actual,
        file_name=file_name_actual,
        data=daily_niger,
        station="station_name",
        elements=["tmax", "tmin"],
        date_time="date",
        rain="rain",
        display_rain_days=True,
    )
    assert __is_expected_file(file_name_actual)


def test_inventory_table():
    data_file: str = os.path.join(TEST_DIR, "data", "daily_niger.csv")
    """
    Note: `inventory_table()` was updated to format the date column before the R function is called. 
          Therefore it is no longer possible to trigger the R exception. The test below is 
          commented out rather than deleted, because it provides an example of how to catch and test 
          for an exception raised in the R code. 

    # test with data that has invalid format for date column, should trigger exception
    daily_niger = read_csv(
        data_file,
        # parse_dates=["date"],
        dayfirst=True,
        na_values="NA",
    )

    try:
        actual = epicsa.inventory_table(
            data=daily_niger,
            date_time="date",
            elements=["rain"],
            station="station_name",
            year="year",
            month="month",
            day="day",
        )
        assert False  # exception should have been thrown
    except Exception as err:
        actual: str = err.args[0]
        expected: str = (
            "Error in (function (data, date_time, elements, station = NULL, "
            "year = NULL,  : \n  Assertion on 'data[[date_time]]' failed: Must be of class "
            "'Date', not 'character'.\n"
        )
        assert actual == expected
    """

    # read in correctly formatted data
    daily_niger = read_csv(
        data_file,
        parse_dates=["date"],
        dayfirst=True,
        na_values="NA",
    )

    # Functions output for one element (rain) for day
    actual = epicsa.inventory_table(
        data=daily_niger,
        date_time="date",
        elements=["rain"],
        station="station_name",
        year="year",
        month="month",
        day="day",
    )
    assert __is_expected_dataframe(
        data=actual, file_name="inventory_table_actual010.csv"
    )

    # Functions output for all elements for day
    actual = epicsa.inventory_table(
        data=daily_niger,
        date_time="date",
        elements=["tmax", "tmin", "rain", "hmax", "hmin", "sunh", "ws", "wd"],
        station="station_name",
        year="year",
        month="month",
        day="day",
    )
    assert __is_expected_dataframe(
        data=actual, file_name="inventory_table_actual020.csv"
    )

    # Functions output for one element (rain) for doy
    actual = epicsa.inventory_table(
        data=daily_niger,
        date_time="date",
        elements=["rain"],
        station="station_name",
        year="year",
        month="month",
        day="doy",
    )
    assert __is_expected_dataframe(
        data=actual, file_name="inventory_table_actual030.csv"
    )

    # Functions output for all elements for doy
    actual = epicsa.inventory_table(
        data=daily_niger,
        date_time="date",
        elements=["tmax", "tmin", "rain", "hmax", "hmin", "sunh", "ws", "wd"],
        station="station_name",
        year="year",
        month="month",
        day="doy",
    )
    assert __is_expected_dataframe(
        data=actual, file_name="inventory_table_actual040.csv"
    )


def test_output_CPT():
    data_file: str = os.path.join(TEST_DIR, "data", "yearly_niger.csv")
    yearly_niger = read_csv(
        data_file,
        dayfirst=True,
        na_values="NA",
    )

    data_file = os.path.join(TEST_DIR, "data", "stations_niger.csv")
    stations_niger = read_csv(
        data_file,
        dayfirst=True,
        na_values="NA",
    )

    # Create summary data
    # yearly_niger <- daily_niger %>% dplyr::group_by(station_name, year) %>%
    #     dplyr::summarise(mean_rain = mean(rain))
    # output_CPT(data = yearly_niger, lat_lon_data = stations_niger,
    #            station_latlondata = "station_name", latitude = "lat", longitude = "long",
    #            station = "station_name", year = "year", element = "mean_rain")
    actual = epicsa.output_CPT(
        data=yearly_niger,
        lat_lon_data=stations_niger,
        station_latlondata="station_name",
        latitude="lat",
        longitude="long",
        station="station_name",
        year="year",
        element="mean_rain",
    )
    assert __is_expected_dataframe(data=actual, file_name="output_CPT_actual010.csv")


def test_timeseries_plot():
    data_file: str = os.path.join(TEST_DIR, "data", "niger50.csv")
    niger50 = read_csv(
        data_file,
        parse_dates=["date"],
        dayfirst=True,
        na_values="NA",
    )

    data_file: str = os.path.join(TEST_DIR, "data", "agades.csv")
    agades = read_csv(
        data_file,
        parse_dates=["date"],
        dayfirst=True,
        na_values="NA",
    )

    # test_that("single element facet by station graphs are correct", {
    #   t1 <- timeseries_plot(data = niger50, date_time = "date", elements = "tmax",
    #                    station = "station_name", facet_by = "stations")
    file_name_actual: str = "timeseries_plot_actual010.jpg"
    actual = epicsa.timeseries_plot(
        path=output_path_actual,
        file_name=file_name_actual,
        data=niger50,
        date_time="date",
        elements=["tmax"],
        station="station_name",
        facet_by="stations",
    )
    assert __is_expected_file(file_name_actual)

    # test_that("single element single station graphs are correct", {
    #   t1 <- timeseries_plot(data = agades, date_time = "date", elements = "tmax",
    #                    facet_by = "none")
    file_name_actual: str = "timeseries_plot_actual020.jpg"
    actual = epicsa.timeseries_plot(
        path=output_path_actual,
        file_name=file_name_actual,
        data=agades,
        date_time="date",
        elements=["tmax"],
        facet_by="none",
    )
    assert __is_expected_file(file_name_actual)

    # test_that("single element single station bar graphs are correct", {
    #   t1 <- timeseries_plot(data = agades, date_time = "date", elements = "tmax",
    #                    facet_by = "none", type = "bar")
    file_name_actual: str = "timeseries_plot_actual030.jpg"
    actual = epicsa.timeseries_plot(
        path=output_path_actual,
        file_name=file_name_actual,
        data=agades,
        date_time="date",
        elements=["tmax"],
        facet_by="stations",
        type="bar",
    )
    assert __is_expected_file(file_name_actual)

    # test_that("single element colour by station no facet graphs are correct", {
    #   t1 <- timeseries_plot(data = niger50, date_time = "date", elements = "tmax",
    #                    station = "station_name", facet_by = "none")
    file_name_actual: str = "timeseries_plot_actual040.jpg"
    actual = epicsa.timeseries_plot(
        path=output_path_actual,
        file_name=file_name_actual,
        data=niger50,
        date_time="date",
        elements=["tmax"],
        station="station_name",
        facet_by="none",
    )
    assert __is_expected_file(file_name_actual)

    # test_that("multiple element single station graphs are correct", {
    #   t1 <- timeseries_plot(data = agades, date_time = "date",
    #                    elements = c("tmin", "tmax"),
    #                    facet_by = "none")
    file_name_actual: str = "timeseries_plot_actual050.jpg"
    actual = epicsa.timeseries_plot(
        path=output_path_actual,
        file_name=file_name_actual,
        data=agades,
        date_time="date",
        elements=["tmin", "tmax"],
        facet_by="none",
    )
    assert __is_expected_file(file_name_actual)

    # test_that("multiple element single station facet by elements graphs are correct", {
    #   t1 <- timeseries_plot(data = agades, date_time = "date",
    #                    elements = c("tmin", "tmax"),
    #                    facet_by = "elements")
    file_name_actual: str = "timeseries_plot_actual060.jpg"
    actual = epicsa.timeseries_plot(
        path=output_path_actual,
        file_name=file_name_actual,
        data=agades,
        date_time="date",
        elements=["tmin", "tmax"],
        facet_by="elements",
    )
    assert __is_expected_file(file_name_actual)

    # test_that("multiple element & multiple stations with both as facet_by graphs are correct", {
    #   t1 <- timeseries_plot(data = niger50, date_time = "date",
    #                    station = "station_name",
    #                    elements = c("tmin", "tmax"),
    #                    facet_by = "stations-elements")
    file_name_actual: str = "timeseries_plot_actual070.jpg"
    actual = epicsa.timeseries_plot(
        path=output_path_actual,
        file_name=file_name_actual,
        data=niger50,
        date_time="date",
        elements=["tmin", "tmax"],
        station="station_name",
        facet_by="stations-elements",
    )
    assert __is_expected_file(file_name_actual)

    # test_that("multiple element & multiple stations facet by elements graphs are correct", {
    #   t1 <- timeseries_plot(data = niger50, date_time = "date",
    #                    station = "station_name",
    #                    elements = c("tmin", "tmax"),
    #                    facet_by = "elements")
    file_name_actual: str = "timeseries_plot_actual080.jpg"
    actual = epicsa.timeseries_plot(
        path=output_path_actual,
        file_name=file_name_actual,
        data=niger50,
        date_time="date",
        elements=["tmin", "tmax"],
        station="station_name",
        facet_by="elements",
    )
    assert __is_expected_file(file_name_actual)

    # test_that("multiple element & multiple stations facet by stations graphs are correct", {
    #   t1 <- timeseries_plot(data = niger50, date_time = "date",
    #                    station = "station_name",
    #                    elements = c("tmin", "tmax"),
    #                    facet_by = "stations")
    file_name_actual: str = "timeseries_plot_actual090.jpg"
    actual = epicsa.timeseries_plot(
        path=output_path_actual,
        file_name=file_name_actual,
        data=niger50,
        date_time="date",
        elements=["tmin", "tmax"],
        station="station_name",
        facet_by="stations",
    )
    assert __is_expected_file(file_name_actual)

    # test_that("multiple element & multiple stations no facet graphs are correct", {
    #   t1 <- timeseries_plot(data = niger50, date_time = "date",
    #                    station = "station_name",
    #                    elements = c("tmin", "tmax"),
    #                    facet_by = "none")
    file_name_actual: str = "timeseries_plot_actual100.jpg"
    actual = epicsa.timeseries_plot(
        path=output_path_actual,
        file_name=file_name_actual,
        data=niger50,
        date_time="date",
        elements=["tmin", "tmax"],
        station="station_name",
        facet_by="none",
    )
    assert __is_expected_file(file_name_actual)

    # test_that("points, LOBF, path and step are correctly added", {
    #   t1_points <- timeseries_plot(data = agades, date_time = "date",
    #                                facet_by = "none",
    #                                elements = "tmin", add_points = TRUE)
    file_name_actual: str = "timeseries_plot_actual110.jpg"
    actual = epicsa.timeseries_plot(
        path=output_path_actual,
        file_name=file_name_actual,
        data=agades,
        date_time="date",
        elements=["tmin"],
        facet_by="none",
        add_points=True,
    )
    assert __is_expected_file(file_name_actual)

    #   t1_lobf <- timeseries_plot(data = agades, date_time = "date",
    #                              facet_by = "none",
    #                              elements = "tmin", add_line_of_best_fit = TRUE)
    file_name_actual: str = "timeseries_plot_actual120.jpg"
    actual = epicsa.timeseries_plot(
        path=output_path_actual,
        file_name=file_name_actual,
        data=agades,
        date_time="date",
        elements=["tmin"],
        facet_by="none",
        add_line_of_best_fit=True,
    )
    assert __is_expected_file(file_name_actual)

    #   t1_path <- timeseries_plot(data = agades, date_time = "date",
    #                              facet_by = "none",
    #                              elements = "tmin", add_path = TRUE)
    file_name_actual: str = "timeseries_plot_actual130.jpg"
    actual = epicsa.timeseries_plot(
        path=output_path_actual,
        file_name=file_name_actual,
        data=agades,
        date_time="date",
        elements=["tmin"],
        facet_by="none",
        add_path=True,
    )
    assert __is_expected_file(file_name_actual)

    #   t1_step <- timeseries_plot(data = agades, date_time = "date",
    #                              facet_by = "none",
    #                              elements = "tmin", add_step = TRUE)
    file_name_actual: str = "timeseries_plot_actual140.jpg"
    actual = epicsa.timeseries_plot(
        path=output_path_actual,
        file_name=file_name_actual,
        data=agades,
        date_time="date",
        elements=["tmin"],
        facet_by="none",
        add_step=True,
    )
    assert __is_expected_file(file_name_actual)

    # test_that("facet warning is displayed", {
    #   expect_warning(timeseries_plot(data = niger50, date_time = "date", elements = "tmax",
    #                  facet_by = "stations"))
    file_name_actual: str = "timeseries_plot_actual150.jpg"
    actual = epicsa.timeseries_plot(
        path=output_path_actual,
        file_name=file_name_actual,
        data=niger50,
        date_time="date",
        elements=["tmax"],
        facet_by="stations",
    )
    assert __is_expected_file(file_name_actual)


def test_windrose():
    data_file: str = os.path.join(TEST_DIR, "data", "daily_niger.csv")
    daily_niger = read_csv(
        data_file,
        parse_dates=["date"],
        dayfirst=True,
        na_values="NA",
    )

    # windrose_plot <- windrose(data = daily_niger, speed = "ws", direction = "wd",
    #                           facet_by = "station_name")
    file_name_actual: str = "windrose_actual010.jpg"
    actual = epicsa.windrose(
        path=output_path_actual,
        file_name=file_name_actual,
        data=daily_niger,
        speed="ws",
        direction="wd",
        facet_by="station_name",
    )
    assert __is_expected_file(file_name_actual)


def __is_expected_dataframe(data: DataFrame, file_name: str) -> bool:
    output_file_actual, output_file_expected = __get_output_file_paths(file_name)

    # write the actual results to csv file, and then read the results back in again
    # Note:We read the expected results from a csv file. Writing/reading this file may change the
    #      data frame's meta data. Therefore, we must also write/read the actual results to csv so
    #      that we are comparing like with like.
    data.to_csv(output_file_actual, index=False)
    actual_from_csv: DataFrame = read_csv(output_file_actual)

    # read the expected reults from csv file
    expected_from_csv: DataFrame = read_csv(output_file_expected)

    # return if actual equals expected
    diffs: DataFrame = actual_from_csv.compare(expected_from_csv)
    return diffs.empty


def __is_expected_file(file_name: str) -> bool:
    output_file_actual, output_file_expected = __get_output_file_paths(file_name)
    return filecmp.cmp(output_file_actual, output_file_expected)


def __get_output_file_paths(file_name: str):
    output_file_actual: str = os.path.join(TEST_DIR, "results_actual", file_name)
    output_file_expected: str = os.path.join(
        TEST_DIR, "results_expected", file_name.replace("actual", "expected")
    )
    return output_file_actual, output_file_expected
