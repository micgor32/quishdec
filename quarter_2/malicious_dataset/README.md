# Generate malicious part of the dataset
This subdirectory contains code for generating QR codes out of blacklist of malicious links provided by [NASK (Research and Academic Computer Network)](https://cert.pl/en/warning-list/).

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

### Running the script
```bash
python malicious_gen.py
```
