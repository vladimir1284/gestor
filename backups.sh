#!/bin/bash

# Change to the proyect directory
cd /home/vladimir/gestor/

# make a local archive
tar -zcvf backups/db.backup-$(date +%F).tar.gz db.sqlite3

# backup to drive
sleep 1
rclone sync backups remote:towit/backups/db


# delete archives older than 14 days from disk
sleep 1
find backups/ -type f -name "*.tar.gz" -mtime +14 -exec rm {} \;

# Save all the images and documents to drive
sleep 1
rclone copy media remote:towit/backups/media