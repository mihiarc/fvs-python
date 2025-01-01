.PHONY: clean data lint requirements sync_data_to_s3 sync_data_from_s3

#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
PYTHON_INTERPRETER = python3

#################################################################################
# COMMANDS                                                                      #
#################################################################################

## Install Python Dependencies
requirements:
	$(PYTHON_INTERPRETER) -m pip install -r requirements.txt

## Make Dataset
data:
	$(PYTHON_INTERPRETER) fvs_python/dataset.py

## Delete all compiled Python files
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

## Lint using flake8
lint:
	flake8 fvs_python

## Upload Data to S3
sync_data_to_s3:
	aws s3 sync data/ s3://[BUCKET_NAME]/data/

## Download Data from S3
sync_data_from_s3:
	aws s3 sync s3://[BUCKET_NAME]/data/ data/

#################################################################################
# PROJECT RULES                                                                 #
################################################################################# 