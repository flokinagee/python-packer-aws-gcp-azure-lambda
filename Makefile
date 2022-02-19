
PYTHON = /usr/local/bin/python3
PIP = /usr/local/bin/pip
PACKAGE_PATH=build.zip

clean: 
	find . -name __pycache__ -exec rm -r {} \;
	find . -name *.pyc -exec rm -r {} \;
	rm package.zip

run: 
	$(PYTHON) main.py
 
build: 
	>/dev/null zip -9 -r ${PACKAGE_PATH} * -x \*.pyc \*.md \*.zip \*.log \*__pycache__\* \*.so lib/botocore\*

test:
	pytest -v
