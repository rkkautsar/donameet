#!/usr/bin/env bash
pm2 start serve.py
pm2 start Donameet/services/tweet_parser.py
