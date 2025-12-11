# Data Model FAIRness Evaluator (User Guide)

## Table of Contents
- Overview
- Functionality
- Requirements
- How it works
- Setting up the Docker
- Future Improvements
- Acknowledgments

## Overview
The Data Model FAIRness Evaluator is a validation tool designed to assess NGSI-LD datasets for WATERVERSE FAIR compliance through geolocation-based validation. It operates as an API endpoint that receives Data Model JSON and returns evaluation results, supporting improved data quality and consistency across the WATERVERSE platform.

## Functionality
* Accepts POST requests containing NGSI-LD Data Model JSON.
* Validates the structure and content of the incoming data.
* Applies geolocation validation checks.
* Computes FAIRness evaluation results and returns them as JSON.
* Supports WATERVERSE services that require automated FAIR compliance assessment.

## Requirements
### Input
* Data Model JSON-LD submitted to the API via POST request.

### Output
* JSON response containing the FAIRness evaluation results.

### System Requirements
* Python installed (for running outside Docker).
* Docker for containerized deployment (optional but recommended).
* Network access to the server hosting the API.

## How it works
When a POST request is sent to the API endpoint, the tool processes the incoming NGSI-LD Data Model JSON, performs structural validation, and applies geolocation-based checks to determine the dataset’s FAIRness compliance level. It then returns the computed evaluation results in JSON format.

## Setting up the Docker
1. Build the docker:
sudo docker build -t fairness .

2. Run the docker:
sudo docker run -d -p 5000:5000 fairness

### To make sure the docker is running:
1. List running containers:
sudo docker ps

2. Show container logs:
sudo docker logs <container_id>

## Future Improvements
Extend FAIRness checks with additional validation criteria as required by the WATERVERSE project.

## Acknowledgments

This project has been funded by the [WATERVERSE project](https://waterverse.eu/) of the European Union’s Horizon Europe programme under Grant Agreement no 101070262.

WATERVERSE is a project that promotes the use of FAIR (Findable, Accessible, Interoperable, and Reusable) data principles to improve water sector data management and sharing.

