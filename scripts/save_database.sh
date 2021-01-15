#! /usr/bin/env bash
#

#

bkdir="/var/gecloud/mysqlbak"

if [ ! -d $bkdir ];then
    mkdir -p $bkdir
    chmod a+w $bkdir
fi

filename="$bkdir/db_gecloud_$(date "+%F_%T").sql.gz"

mysqldump -uroot1 -p123456 --databases gecloud --lock-all-tables | gzip > "$filename"
if [ $? -eq 0 ];then
    echo "success: backup database gecloud to $filename"
else
    echo "error: backup database gecloud to $filename"
fi
