#!/bin/bash
# Backup everything - schema + data
pg_dump -Fc distillyzer > backup.dump
echo "Done: backup.dump"
