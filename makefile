unit-test:
	pytests tests/unit --cov=zombie_nomnom --cov-report=term --cov-report=xml --cov-report=html
int-test:
	pytests tests/integration --cov=zombie_nomnom --cov-report=term --cov-report=xml --cov-report=html
all-test:
	pytest tests --cov=zombie_nomnom --cov-report=term --cov-report=xml --cov-report=html
docs:
	pdoc ./zombie_nomnom
build-docs:
	make cov-all
	pdoc ./zombie_nomnom -o ./docs
cov-all:
	pytest tests --cov=zombie_nomnom --cov-report=html:docs/coverage --html=docs/coverage/report.html
format:
	black .