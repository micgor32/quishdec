# Edge cases (example)
This directory contains samples of QR codes, 3 of which are benign, and 6 of which are modified by either adding noise, or removing pad codewords. The results of scanning these QR codes using [website](https://quishing.gorlas.dev) with deployed model, are given in the [spreadsheet](edge_cases.xlsx).

## Disclaimer
Please note that the QR codes modified using noise method, may redirect to (at the time) non-existing URL. Authors can not guarantee that these URL addresses will not be aquired by (potentially) malicious actors. Use these QR codes at your own risk!
QR codes generated using pad codewords method do NOT redirect to any different URL addresses than the benign ones. Consequently, these do not pose any danger to the user, and they only demonstrate introducing the feature (modified pad codewords) that will be spotted by the model, without introducing an actual attack.