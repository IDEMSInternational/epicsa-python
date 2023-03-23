# epicsa-python

This module provides access to the [epicsawrap](https://github.com/IDEMSInternational/epicsawrap) R package.
It communicates with the R environment using the [rpy2](https://rpy2.github.io/) package.

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

## Pre-Requisites

The api requires Python and R runtimes installed. It has been tested with the versions listed below:

- Python (3.11)  
  [https://www.python.org/downloads](https://www.python.org/downloads)

- R and Rtools (4.2.3)  
  [https://cran.r-project.org/bin/windows/base](https://cran.r-project.org/bin/windows/base)
  [https://cran.r-project.org/bin/windows/Rtools/](https://cran.r-project.org/bin/windows/Rtools/)

Relevant documentation should also be followed to ensure runtimes can be executed from the PATH environment variable.

## Configuration

**Python**

The scripts below will create a python [virtual environment](https://docs.python.org/3/library/venv.html), activate, install required python and R dependencies and start local server

=== "Windows (powershell)"

    ``` ps1 linenums="1"
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    ```

=== "Linux (bash)"

    ```sh linenums="1"
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

**R**

Once installed you will need to call R from an elevated shell to install dependencies

Windows (run as administrator)

```
Rscript install_packages.R
```

Linux

```
sudo Rscript install_packages.R
```

**Authorization File**

In order to run the package, you will need to add the following service account file to the main repository folder (i.e. the folder where this `README.md` file is stored):

```
service-account.json
```

## Running Tests

```py
pytest
```

## Troubleshooting

**Pip won't install dependencies**
Depending on local versions of R and python (as well as operating system) there may be issues when installing certain packages. Recommend attempting install using the `requirements_dev.txt` file which pins exact versions of packages shown to be compatible with each other, i.e.

```sh
pip install -r requirements_dev.txt
```

Any other issues should be raised on GitHub

## License

This project is licensed under the terms of the MIT license.
