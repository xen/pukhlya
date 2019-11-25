PROJ=pukhlya

all: setup

venv/bin/activate:
	python3 -m venv venv

setup: venv/bin/activate dev-req.txt
	# createdb postline
	. venv/bin/activate; pip install -U pip
	. venv/bin/activate; pip install -Ur dev-req.txt

t: venv/bin/activate
	. venv/bin/activate; python -V
	. venv/bin/activate; pytest -vv --cov=pukhlya tests/

freeze:
	. venv/bin/activate; pip pip freeze > requirements.txt 
