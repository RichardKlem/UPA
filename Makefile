# Makefile

all : run

.PHONY: all

run:
	python3 main.py

clean:
	rm -rf data src/__pycache__ __pycache__