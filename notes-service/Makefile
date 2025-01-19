IMAGE_NAME = notes-service
PORT = 8002

wm:
	watchmedo shell-command \
	--patterns="*.py" \
	--recursive \
	--command="mypy app.py"


build:
	docker build -t $(IMAGE_NAME) .


dev:
	docker run -it --rm \
		-p $(PORT):8002 \
		--network=sb-network \
		--name notes-service \
		-v $(PWD):/app \
		-v /Users/leo/notes:/notes \
		$(IMAGE_NAME) uvicorn app:app --host 0.0.0.0 --port $(PORT) --reload
