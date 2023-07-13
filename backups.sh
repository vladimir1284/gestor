#!/bin/bash

# make a local archive
tar -zcvf /home/vladimir/gestor/backups/db.backup-$(date +%F).tar.gz \
 /home/vladimir/gestor/db.sqlite3

# backup to drive
sleep 1
rclone sync /home/vladimir/gestor/backups remote:towit/backups/db


# delete archives older than 14 days from disk
sleep 1
find /home/vladimir/gestor/backups/ -type f -name "*.tar.gz" -mtime +14 -exec rm {} \;

# Save all the images and documents to drive
sleep 1
rclone copy /home/vladimir/gestor/static remote:towit/backups/static