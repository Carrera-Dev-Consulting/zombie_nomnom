unit-test:
	pytests tests/unit --cov=zombie_dice --cov-report=term --cov-report=xml --cov-report=html
int-test:
	pytests tests/integration --cov=zombie_dice --cov-report=term --cov-report=xml --cov-report=html
all-test:
	pytest tests --cov=zombie_dice --cov-report=term --cov-report=xml --cov-report=html
docs:
	pdoc ./zombie_dice
build-docs:
	make cov-all
	pdoc zombie_dice -o ./docs
cov-all:
	pytest tests --cov=zombie_dice --cov-report=html:docs/coverage
format:
	black .