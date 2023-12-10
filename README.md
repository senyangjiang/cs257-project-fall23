# Optimizing SAT Solvers by Machine Learning

## Files
This repo contains the source code for experiments in "Optimizing SAT Solvers by Machine Learning". It includes:
- Linux binary for 4 different solvers: 
    - z3
    - kissat
    - cryptominisat
    - cadical
- scripts for running the solvers on benchmarks and collect results in a `.csv` file: `run.py`
- scripts for extracting features from benchmarks: `SATfeatPy/generate_bulk_features.py`
- jupyter notebook for preparing train data: `data.ipynb`
- jupyter notebook for training a 2-layer network for prediction : `model.ipynb`
We actually ran the jupyter notebook on google colab, but we copied the notebook here for convenience

Our experiement are carried out on the SAT 2022 Competition Anniversary Track Benchmarks
https://satcompetition.github.io/2022/downloads.html

The whole dataset is over 100GB after unzipping, you can download the dataset using
~~~
wget --content-disposition -i track_anni_2022.uri
~~~

## Required Python3 packages
We are using Python 3.10. Running the experiments requires the following packages
- Performing benchmark, Prepare train data
    - `pandas`
- Train model
    - `keras`
    - `tensorflow`
    - `scikeras`
    - `sklearn`
    - `matplotlib`
    
We recommend running the jupyer notebook on Google Colab so you don't have to install these packages yourself (except `scikeras`)

## Usage
### Perform Benchmark
Use `run.py` to run solvers on the `anni_2022` dataset, you can see available options using `python3 run.py -h`.

For example, to run z3 solver
- on the first 300 benchmarks,
- with timeout of 60 seconds,
- with default configuration 

use the following commmand:
~~~
python3 run.py --count=300 --solver_kind=z3 --timeout=60
~~~

Results are written to `output.csv`

### Extract features
Use `/SATfeatPy/generate_bulk_features.py` to extract features from formulas in the `anni_2022` benchmark. If you want to change the set of features or run on another benchmark, you need to manually adjust the code in the file.

Results are written to `features.csv`

### Prepare Train Data
Follow the steps in `data.ipynb` to prepare the dataset where
- input: features of each formula
- output: best configuration that leads to fastest run time
Train data are written to `result_normalized.csv`

## Train Model
Follow the steps in `data.ipynb` to train the model