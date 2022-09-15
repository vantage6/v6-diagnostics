all:
	make build
	make publish

build:
	docker build -t harbor2.vantage6.ai/infrastructure/hello-vantage6 .

publish:
	docker push harbor2.vantage6.ai/infrastructure/hello-vantage6