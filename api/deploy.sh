#!/bin/bash -e

sam build --use-container
sam deploy --config-file sam.toml