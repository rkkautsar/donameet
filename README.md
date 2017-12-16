Donameet
=========

> Connecting donors with those in need

## How to Install
```bash
# Setup virtualenv
python3 -m venv env
source env/bin/activate

# Install
pip install -r requirements.txt

# Run locally
python serve.py
```

## Run service
```bash
python Donameet/services/tweet_parser.py
# or as daemon:
pm2 start Donameet/services/tweet_parser.py
```


## Technology :rocket:
- Python 3
- [Flask](http://flask.pocoo.org/)
- [SQLAlchemy](http://www.sqlalchemy.org/)
