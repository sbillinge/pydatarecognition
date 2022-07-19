# pyDataRecognition

For a thorough description of the project, please see the paper by
Özer *et al.*

Code available at https://github.com/Billingegroup/pydatarecognition.

## Setup and installation
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
### Install package
- Install the package by navigating to the main **pydatarecognition** 
  directory and run:
  ```shell
  python setup.py install
  ```

## Running the program for the example files

### Example files
  Three files with user data examples are located within
  ```docs/examples/powder_data```:
- 01_Mg-free-whitlockite_wl=1.540598.txt
- 02_BaTiO3_wl=0.1665.txt
- 03_(KNaLi)NbMnO3_perovskite_wl=1.5482.txt

### Running the program
To get information on how to run the program:  
  ```shell
      python -m pydatarecognition.main --help
  ```
or
  ```shell
    python -m pydatarecognition.main -h
  ```
The program expects a syntax somewhat similar to (for a full desription,
      please run the program with the help flag as shown above):
```shell
  python pydatarecognition.main -i INPUTFILE --xquantity XQUANTITY --xunit XUNIT -w WAVELENGTH
  ```
#### Running the program the first example file
From the directory, where the example files reside 
(```docs/examples/powder_data```):
  ```shell
  python -m pydatarecognition.main -i 01_Mg-free-whitlockite_wl=1.540598.txt --xquantity twotheta --xunit deg -w 1.540598.txt
  ```
#### Running the program for the second example file
  ```shell
  python -m pydatarecognition.main -i 02_BaTiO3_wl=0.1665.txt --xquantity twotheta --xunit deg -w 0.1665
  ```
#### Running the program for the third example file
  ```shell
  python -m pydatarecognition.main -i 03_(KNaLi)NbMnO3_perovskite_wl=1.5482.txt --xquantity "twotheta" --xunit "deg" -w 1.5482
  ```
