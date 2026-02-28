#!/bin/bash

mkdir -p ~/.streamlit/

echo "\
[general]\n\
email = \"user@example.com\"\n\
" > ~/.streamlit/credentials.toml

echo "\
[server]\n\
headless = true\n\
port = \$PORT\n\
enableCORS = false\n\
" > ~/.streamlit/config.toml
