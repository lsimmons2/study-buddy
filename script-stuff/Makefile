IMAGE_NAME = script-service
PORT = 8001


build:
	docker build -t $(IMAGE_NAME) .

exec:
	docker run -it -p $(PORT):8001 $(IMAGE_NAME) bash

dev:
	docker run -it --rm \
		-p $(PORT):8001 \
		--network=sb-network \
		--name transcript-service \
		-v $(PWD):/app \
		-v /Users/leo/ai_transcripts/:/ai_transcripts \
		$(IMAGE_NAME) uvicorn app:app --host 0.0.0.0 --port $(PORT) --reload

run:
	docker run -p $(PORT):8001 $(IMAGE_NAME)

wm:
	watchmedo shell-command \
	--patterns="*.py" \
	--recursive \
	--command="mypy app.py"
