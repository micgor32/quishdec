# Generate benign part of the dataset
This subdirectory contains code for generating QR codes out of Top 500 most popular domains provided by [Cloudflare](https://radar.cloudflare.com/domains).

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
pip install -r dependencies.txt
```

### Running the script
```bash
python benign_gen.py
```
