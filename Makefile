EMBEDDING_INDEX_SERVICE_URL = http://localhost:8000
TRANSCRIPT_SERVICE_URL = http://localhost:8001
NOTES_SERVICE_URL = http://localhost:8002
EMBEDDING_GEN_SERVICE_URL = http://192.168.1.51:5000
OLLAMA_SERVICE_URL = http://192.168.1.51:11434


service-client-gen:
	openapi-generator-cli generate \
		-i $(TRANSCRIPT_SERVICE_URL)/openapi.json \
		-g python \
		-o clients/python/transcript_service \
		--additional-properties=packageName=transcript_service_client
	openapi-generator-cli generate \
		-i $(EMBEDDING_GEN_SERVICE_URL)/openapi.json \
		-g python \
		-o clients/python/embedding_service \
		--additional-properties=packageName=embedding_gen_service_client
	openapi-generator-cli generate \
		-i $(EMBEDDING_INDEX_SERVICE_URL)/openapi.json \
		-g python \
		-o clients/python/embedding_index_service \
		--additional-properties=packageName=embedding_index_service_client
	openapi-generator-cli generate \
		-i $(NOTES_SERVICE_URL)/openapi.json \
		-g python \
		-o clients/python/notes_service \
		--additional-properties=packageName=notes_service_client
