# Getting Started

### Creating a virtual environment
```bash
python -m venv .[venv name]
```

### Activating the virtual environment
Windows:
```bash
.[venv name]\Scripts\activate
```

Unix or MacOS:
```bash
source .[venv name]/bin/activate
```

### Dependencies
After creating and activating the virtual environment, you have to install the required packages, running:
```bash
pip install -r requirements.txt
```

### Generating the dataset
Generating the dataset consist of 3 steps:
- First generate the benign QR codes:
    - Move to the 'benign\_dataset' directory, and follow the instructions from the README 
- Generate malicious QR codes:
    - Move to the 'malicious\_dataset' directory, and follow the instructions from the README
- Now generate csv files using generate_csv.py.

### Training the model(s)
This can be done by running comparison.ipynb notebook, once the dataset is present. Make sure you adjusted the names of csv files used by notebook!

### Running the PoC "app"
There are two ways of running, the app:
- Using graphical interface by running gui.py
- Using command line by running backend\_poc.py and providing path to QR code that shall be scanned

