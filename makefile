.PHONY: unit-test
unit-test:
	pytest tests/unit --cov=zombie_nomnom --cov-report=term --cov-report=xml --cov-report=html
.PHONY: int-test
int-test:
	pytest tests/integration --cov=zombie_nomnom --cov-report=term --cov-report=xml --cov-report=html
.PHONY: all-test
all-test:
	pytest tests --cov=zombie_nomnom --cov-report=term --cov-report=xml --cov-report=html
.PHONY: docs
docs:
	pdoc ./zombie_nomnom
.PHONY: build-docs
build-docs:
	make cov-all
	pdoc ./zombie_nomnom -o ./docs
.PHONY: cov-all
cov-all:
	pytest tests --cov=zombie_nomnom --cov-report=html:docs/coverage --html=docs/coverage/report.html
.PHONY: render-cov
render-cov:
	python -m http.server -d htmlcov 8081
.PHONY: format
format:
	black .