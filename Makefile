IMAGE_NAME := "harbor2.vantage6.ai/algorithms/diagnostic"

help:
	@echo "publish           -  build and push docker image to registry"
	@echo "image             -  build docker image"
	@echo "push              -  push docker image to registry"
	@echo "help              -  show this help message and exit"

publish: image push

image:
	docker build -t $(IMAGE_NAME) .

push:
	docker push $(IMAGE_NAME)