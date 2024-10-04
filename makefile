unit-test:
	pytests tests/unit --cov=zombie_dice --cov-report=term --cov-report=xml --cov-report=html
int-test:
	pytests tests/integration --cov=zombie_dice --cov-report=term --cov-report=xml --cov-report=html
all-test:
	pytest tests --cov=zombie_dice --cov-report=term --cov-report=xml --cov-report=html
docs:
	pdoc ./zombie_dice
format:
	black .