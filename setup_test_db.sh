#!/bin/bash
echo "Dumping the database from the remote server..."
echo "Password for the prod db"
pg_dump -U appez -h db.appez.cafe -p 54321 -F c -d dofresstrack -f dofresstrack_backup.dump
echo "Restoring the database to the local server..."
echo "Password for the local db"
pg_restore -U appez -h localhost -p 5432 -O -x -c -d dofresstrack -1 dofresstrack_backup.dump
