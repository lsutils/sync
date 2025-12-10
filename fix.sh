#!/usr/bin/env bash
rm -rf .github/workflow/*
python3 random-dup.py
python3 fixed-dup.py
