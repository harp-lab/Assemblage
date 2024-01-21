# Assemblage

Assemblage is a distributed binary corpus discovery, generation, and archival tool built to provide high-quality labeled metadata for the purposes of building training data for machine learning applications of binary analysis and other applications (static / dynamic analysis, reverse engineering, etc...).

## Cloud infrastructure support

We have run Assemblage over the course of several months within the research computing cluster at (a) Syracuse University and (b) on Amazon Web Services EC2. This branch is a general template.

## Worker Requirement

Assemblage provides Dockerfile and build script to construct Docker images for Linux worker, and the Docker compose file can be used to specify the resource each worker can access. Due to the commercial license nature of the Wiundows platform, we only provide the boot script and environment specification for workers.

## Dataset Availability

Currently, public datasets are on Windows. 

Windows dataset can be accessed via following links

https://assemblage-dataset.s3.us-west-1.amazonaws.com/latest/sept25.sqlite.zip
https://assemblage-dataset.s3.us-west-1.amazonaws.com/latest/dataset_sept25.zip

