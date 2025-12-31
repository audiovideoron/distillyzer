#!/bin/bash
# Restore everything to a fresh database
createdb distillyzer 2>/dev/null
pg_restore -d distillyzer --clean --if-exists backup.dump
echo "Done"
