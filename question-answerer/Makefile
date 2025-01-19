IMAGE_NAME = qa-service
PORT = 8003


wm:
	watchmedo shell-command \
	--patterns="*.py" \
	--recursive \
	--command="mypy app.py"


build:
	docker build -t $(IMAGE_NAME) .


dev:
	docker run -it --rm \
		-p $(PORT):8003 \
		--network=sb-network \
		--name qa-service \
		-v $(PWD):/app \
		$(IMAGE_NAME) uvicorn app:app --host 0.0.0.0 --port $(PORT) --reload
