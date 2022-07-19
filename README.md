# pyDataRecognition

For a thourough description of the project, please see the paper by
Özer *et al.*

Code available at https://github.com/Billingegroup/pydatarecognition.

## Setup and installation
### Create/activate conda environment
- Wherever you run **conda**, create/activate new conda env by running:
  ```shell
  conda create -n pydatarecognition python=3
  conda activate pydatarecognition
  ```
### Install dependencies
- Navigate to the main **pydatarecognition** directory and run:
  ```shell
  conda install --file requirements/run.tx
  pip install -r requirements/pip_requirements.txt
  conda install --file requirements/test.txt
  ```
### Install package
- Install the package by navigating to the main **pydatarecognition** 
  directory and run:
  ```shell
  python setup.py install
  ```

## Running the program for the example files
### Navigate to the directory of the ```main.py``` file
- First, navigate to the main **pydatarecognition** directory.
- Change to the subdirectory called **pydatarecognition**, i.e.
  ```pydatarecognition/pydatarecognition```:
  ```shell
  cd pydatarecognition
  ```
### Running the program for the example files
  The program will look for input files within ```docs/examples```,
  where the ```docs``` folder is within the **pydatarecognition** 
  main directory. The example files are present within the 
  ```powder_data``` subdirectory, i.e. ```docs/examples/powder_data```.
- To get information on how to run the program, being within
  ```pydatarecognition/pydatarecognition```, run:
    ```shell
    python main.py --help
    ```
    or
    ```shell
    python main.py -h
    ```
    - The program expects a syntax somewhat similar to (for a full desription,
      please run the program with the help flag as shown above):
```shell
  python main.py -i powder_data/INPUTFILE --xquantity XQUANTITY --xunit XUNIT -w WAVELENGTH
  ```
#### Running the first example file
* To run the first example file, run:
  ```shell
  python main.py -i powder_data/03_(KNaLi)NbMnO3_perovskite_wl=1.5482.txt --xquantity twotheta --xunit deg -w 1.5482
  ```
#### Running the second example file
* To run the second example file, run:
  ```shell
  -i powder_data/02_BaTiO3_wl=0.1665.txt --xquantity twotheta --xunit deg -w 0.1665
  ```
#### Running the third example file
* To run the third example file, run:
  ```shell
  -i powder_data/03_(KNaLi)NbMnO3_perovskite_wl=1.5482.txt --xquantity "twotheta" --xunit "deg" -w 1.5482
  ```
