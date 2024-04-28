FROM semitechnologies/transformers-inference:custom
RUN MODEL_NAME=BAAI/bge-base-en-v1.5 ./download.py