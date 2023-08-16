#!/bin/bash

# --------------------- Backup gestor ---------------------------
# Change to the proyect directory
cd /home/vladimir/gestor/

# make a local archive
tar -zcvf backups/db.backup-$(date +%F).tar.gz db.sqlite3
tar -zcvf backups/media.backup-$(date +%F).tar.gz media

# backup to drive
sleep 1
rclone sync backups remote:towit/backups/db


# delete archives older than 14 days from disk
sleep 1
find backups/ -type f -name "*.tar.gz" -mtime +14 -exec rm {} \;

# --------------------- Backup wordpress ---------------------------
# Change to the proyect directory
cd /home/vladimir/puntoino/

# Export database
wp db export /home/vladimir/puntoino.sql --allow-root

# make a local archive
cd ..
tar -zcvf backups/db.backup-$(date +%F).tar.gz puntoino.sql
tar -zcvf backups/files.backup-$(date +%F).tar.gz puntoino

# backup to drive
sleep 1
rclone sync backups remote:wp

# delete archives older than 3 days from disk
sleep 1
find backups/ -type f -name "*.tar.gz" -mtime +3 -exec rm {} \;