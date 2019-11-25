PROJ=pukhlya

all: setup

venv/bin/activate:
	@python3 -m venv venv

setup: venv/bin/activate dev.txt
	@. venv/bin/activate; pip install -U pip
	@. venv/bin/activate; pip install -Ur dev.txt

t: venv/bin/activate
	. venv/bin/activate; python -V
	. venv/bin/activate; pytest -vv --cov=pukhlya tests/

freeze:
	rm -rf venvdeploy
	python3 -m venv venvdeploy
	. venvdeploy/bin/activate; pip install -U pip
	. venvdeploy/bin/activate; pip install -r dev-req.txt
	. venvdeploy/bin/activate; pip freeze > requirements.txt 
	rm -rf venvdeploy
