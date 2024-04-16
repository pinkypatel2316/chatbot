Please open the master branch 




Clone repo and create a virtual environment
```
$ clone the repository
$ cd chatbot

create virtual environment
$ python3 -m venv venv
$ . venv/bin/activate
```
Install dependencies
```
$ (venv) pip install Flask torch torchvision nltk
```
Install nltk package
```
$ (venv) python
>>> import nltk
>>> nltk.download('punkt')
```

Run
```
$ (venv) python train.py
```
owing command to test it in the console.
```
$ (venv) python chat.py
```

