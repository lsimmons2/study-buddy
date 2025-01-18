IMAGE_NAME = embedding-index-service
PORT = 8000


build:
	docker build -t embedding-index-service .

exec:
	docker run -it -p 8000:8000 embedding-index-service bash

dev:
	docker run -it --rm \
		-p $(PORT):8000 \
		-v $(PWD):/app \
		$(IMAGE_NAME) uvicorn app:app --host 0.0.0.0 --port $(PORT) --reload

run:
	docker run -p 8000:8000 embedding-index-service

