IMAGE_NAME = embedding-index-service
PORT = 8000


build:
	docker build -t $(IMAGE_NAME) .

exec:
	docker run -it -p 8000:8000 embedding-index-service bash

dev:
	docker run -it --rm \
		-v $(PWD):/app \
		--network=sb-network \
		-p 8000:8000 \
		--name embedding-index-service \
		$(IMAGE_NAME) uvicorn app:app --host 0.0.0.0 --port $(PORT) --reload

run:
	docker run -p 8000:8000 embedding-index-service


wm:
	watchmedo shell-command \
	--patterns="*.py" \
	--recursive \
	--command="mypy app.py --check-untyped-defs"
