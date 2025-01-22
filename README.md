This is an app/system is for experimenting with various usecases for language models in learning from/managing/searching sources and the user's personal notes.

My philosophy here is if I'm trying to learn about a topic, I am often reading/watching/listening to something and taking notes, and there are potentially various things LLMs/software could do to help me with this.

Currently the only usecase/product is a "question answerer" - it parses questions I have in my notes, then has a LLM try to answer them using RAG with a local corpus of video transcripts.

Other thoughts of usecases include:
- parse a model you have written in notes for how you understand something, and argue against it
- parse a model and try to improve the arguments/explanations found in it
- summarizing individual sources, coming up with summaries over a set of sources
- finding semantic gaps in your models, sources
- quizzing you on things that you just don't remember

It might be the case that working with ChatGPT in the browser might be the best way to use LLMs for this kinda thing... but maybe not! Also there's the potential for working with non-embedding-based technologies here.

The setup is a few services run with Docker. Currently running the language models (a simple embedding generation service, and an Ollama server) on a Razer laptop with a moderately powerful GPU, and everything else on my Macbook. Embedding search is done with Faiss. The UI is in Emacs.


