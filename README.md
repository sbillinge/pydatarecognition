# pyDataRecognition

## Manuscript describing the project 
For a thorough description of the project, please see the paper in Acta Crystallographica by Özer *et al.*: 
Özer, B., Karlsen, M.A., Thatcher, Z., Lan, L., McMahon, B., Strickland, P.R., Westrip, S.P., Sang, K.S., Billing, D.G., Ravnsbaek, D.B., Billinge, S.J.L., 2022. Towards a machine-readable literature: finding relevant papers based on an uploaded powder diffraction pattern. Acta Cryst A 78, 386–394. https://doi.org/10.1107/S2053273322007483

## Setup and installation

The following guidelines assume that the user runs a conda distribution, i.e. Anaconda or Miniconda.

### Create/activate conda environment
- Create/activate new conda env by running:
  ```shell
  conda create -n pydatarecognition python=3
  conda activate pydatarecognition
  ```
### Install dependencies
- Navigate to the main **pydatarecognition** directory and run:
  ```shell
  conda install --file requirements/run.txt
  ```
  This will install the dependencies needed to run the example that is described in the paper above.

The code is being further developed with different database backends.  For these developments there is a heavier set of dependencies and you will have to install a more complete set of requirements as below.
  ```shell
  conda install --file requirements/run.txt
  conda install --file requirements/run_ext.txt
  pip install -r requirements/pip_requirements.txt
  ```
### Install package
- Install the package by navigating to the main **pydatarecognition** 
  directory and run:
  ```shell
  python setup.py install
  ```

## Running the program

### Directory structure
Currently, the program should be run from a directory  containing the cif files.
Within `docs/examples`, example cifs are located in the `cifs/measured` and `cifs/calculated` subdirectory,  e.g., in `docs/examples/cifs/measured`.

### Example files
Within `docs/examples/powder_data`, three examples on input data files are available:
- 01_Mg-free-whitlockite_wl=1.540598.txt
- 02_BaTiO3_wl=0.1665.txt
- 03_KNaLi-NbMnO3_perovskite_wl=1.5482.txt

### How to run the program
With your `pydatarecognition` conda env activated, to get information on how to run the program type:  
  ```shell
      pydr --help
  ```
or
  ```shell
    pydatarecognition -h
  ```
The program expects a syntax somewhat similar to:
```shell
  python pydatarecognition.main -i INPUTFILE --xquantity XQUANTITY --xunit XUNIT -w WAVELENGTH
  ```
For a full description, please run the program with the help flag as shown above.

### Running the program for the measured data example files
Navigate to `docs/examples/cifs/measured`.

#### Running the program the first example measured data file
```shell
pydr -i ../../powder_data/01_Mg-free-whitlockite_wl=1.540598.txt --xquantity twotheta --xunit deg -w 1.540598
```
#### Running the program for the second example measured data file
```shell
pydr -i ../../powder_data/02_BaTiO3_wl=0.1665.txt --xquantity twotheta --xunit deg -w 0.1665
```
#### Running the program for the third example measured data file
```shell
pydr -i ../../powder_data/03_KNaLi-NbMnO3_perovskite_wl=1.5482.txt --xquantity twotheta --xunit deg -w 1.5482
```

### Running the program for the calculated cif example files
Navigate to `docs/examples/cifs/calculated` and rerun the commands above.


### Program output
Output files will be available in the `_output` folder created in the current working directory, i.e. 
`docs/examples/_output`.
