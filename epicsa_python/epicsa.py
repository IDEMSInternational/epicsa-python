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
"""Provides a set of wrapper functions for the `epicsawrap` R package.

This module provides access to the `epicsawrap` R package
(https://github.com/IDEMSInternational/epicsawrap).
It communicates with the R environment using the `rpy2` package.
Access is provided through a set of wrapper functions. 
Each wrapper function:
  - Allows the equivalent R function to be called from Python, using Python 
    data types.
  - Has a parameter list that is as close as possible to the equivalent R 
    function's parameter list.
  - Returns its result as a platform independent object, typically a Python 
    pandas data frame.
  - Has a similar structure. First it converts the Python parameters (as 
    needed) into R equivalent data types used by `rpy2`. It calls the R 
    function. If needed, it converts the returned result into a Python data 
    type.
"""
import os
from typing import Dict, List
from pandas import DataFrame
from rpy2.robjects import NULL as r_NULL
from rpy2.robjects import (
    conversion,
    default_converter,
    globalenv,
    packages,
    pandas2ri,
    r,
)
from rpy2.robjects.vectors import DataFrame as RDataFrame
from rpy2.robjects.vectors import FloatVector, ListVector, StrVector

r_epicsawrap = packages.importr("epicsawrap")
r_epicsadata = packages.importr("epicsadata")


def annual_rainfall_summaries(
    country: str,
    station_id: str,
    summaries: List[str] = None,
) -> DataFrame:
    if summaries is None:
        summaries = [
            "annual_rain",
            "start_rains",
            "end_rains",
        ]

    __init_data_env()
    r_params: Dict = __get_r_params(locals())
    r_list_vector: ListVector = r_epicsawrap.annual_rainfall_summaries(
        country=r_params["country"],
        station_id=r_params["station_id"],
        summaries=r_params["summaries"],
    )
    r_data_frame = r_list_vector[1]
    return __get_data_frame(r_data_frame)


def __get_r_params(params: Dict) -> Dict:
    """Returns a dictionary of parameters in R format.

    Converts each Python parameter in 'params' and converts it into an R
    parameter suitable for passing to rpy2. Returns the R parameters as a
    dictionary.

    Args:
        params: A dictionary of Python parameters, normally populated by
          calling `locals()`.

    Returns:
        A dictionary of parameters. Each parameter is in an R format suitable
        for passing to rpy2.
    """
    r_params: Dict = params.copy()

    for key in r_params:
        if r_params[key] is None:
            r_params[key] = r_NULL
        elif isinstance(r_params[key], List):
            if len(r_params[key]) > 0:
                if isinstance(r_params[key][0], str):
                    r_params[key] = StrVector(r_params[key])
                elif isinstance(r_params[key][0], float):
                    r_params[key] = FloatVector(r_params[key])
        elif isinstance(r_params[key], DataFrame):
            # TODO
            # with ro.default_converter + pandas2ri.converter:
            #     r_from_pd_df = ro.conversion.get_conversion().py2rpy(pd_df)
            # with conversion.localconverter(default_converter + pandas2ri.converter):
            #     r_params[key] = conversion.py2rpy(r_params[key])
            with default_converter + pandas2ri.converter:
                r_params[key] = conversion.get_conversion().py2rpy(r_params[key])

    return r_params


def __get_data_frame(r_data_frame: RDataFrame) -> DataFrame:
    """Converts an R format data frame into a Python format data frame.

    Converts 'r_data_frame' into a Python data frame and returns it.

    Args:
        r_data_frame: A data frame in rpy2 R format.

    Returns:
        The data frame converted into Python format.
    """
    # convert R data frame to pandas data frame
    with conversion.localconverter(default_converter + pandas2ri.converter):
        data_frame: DataFrame = conversion.get_conversion().rpy2py(r_data_frame)
    return data_frame


def __convert_posixt_to_r_date(r_data_frame: RDataFrame) -> RDataFrame:
    """Converts all Posix dates in a data frame, to 'Date` format.

    Converts all Posix dates in 'r_data_frame' into R 'Date' format and returns the
    updated R data frame.

    Args:
        r_data_frame: A data frame in rpy2 R format.

    Returns:
        The R data frame with all Posix dates converted into 'Date' format.
    """
    globalenv["df"] = r_data_frame
    return r(
        'data.frame(lapply(df, function(x) { if (inherits(x, "POSIXt")) as.Date(x) else x }))'
    )


def __init_data_env():
    # ensure that this function is only called once per session
    # (because it relies on the current working folder when session started)
    if not hasattr(__init_data_env, "called"):
        __init_data_env.called = True
    else:
        return

    working_folder = os.getcwd()

    service_file: str = os.path.join(working_folder, "service-account.json")
    service_file = os.path.normpath(service_file).replace("\\", "/")
    r_epicsadata.gcs_auth_file(service_file)

    data_folder: str = os.path.join(working_folder, "working_data")
    data_folder = os.path.normpath(data_folder).replace("\\", "/")
    r_epicsawrap.setup(data_folder)
