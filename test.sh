#!/usr/bin/env bash

export CM_API_TESTING=TRUE

python -m pytest

export CM_API_TESTING=FALSE