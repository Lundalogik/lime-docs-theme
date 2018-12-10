IMAGE = lime-docs-theme

.PHONY: build
build:
	docker build --pull -t $(IMAGE) .

.PHONY: test
test: build
	docker run $(IMAGE) python3 manage.py test


.PHONY: publish
publish:
	@docker run $(IMAGE) python3 manage.py upload --username $(DEVPI_USERNAME) --password $(DEVPI_PASSWORD) --index https://pypi.lime.tech/lime/develop/+simple/


.PHONY: pytest
pytest:
	docker-compose run app py.test -s
