build:
	docker build -t attestation_generator .

run:
	docker run -it --rm attestation_generator ./app.py -c toto_config.yml

all: build run
