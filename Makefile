# Makefile

all : run

.PHONY: all

run:
	python3 main.py

clean:
	rm -rf data src/__pycache__