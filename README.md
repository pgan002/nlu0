# nlu0
Toy natural language understanding system. It takes example user requests
(utterances) and tries to classify it into one of several classes (such as
intent) as defined in example data provided at startup time.

## Data format
The user provides example utterances in  text files. There is one file per class
(that is, per intention) and one line per example utterance (that is, per example
user request). The directory containing the data files is defined in file
utterance_classifier.py, the line starting with DATA_DIR.

## Usage
* Edit the file utterance_clasifier.py (see Data format)
* Run 
    ./utterance_classifier.py

