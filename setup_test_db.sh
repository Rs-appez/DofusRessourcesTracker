#!/bin/bash
pg_dump -U appez -h db.appez.cafe -p 54321 -F c -d dofresstrack -f dofresstrack_backup.dump
pg_restore -U appez -h localhost -p 5432 -O -x -c -d dofresstrack -1 dofresstrack_backup.dump
