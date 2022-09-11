# Scripts

This folder contains some useful scripts. 

## Dump 

The `dump.py` script dumps the database content, generating a a file called `dump_sqlite3.sql` by default. 
By default the data is dumped to the `./src/scripts/dump/data` folder.  
The `mysql` and `sqlite3` schema can be found at `./src/scripts/dump/schema` and these
are not regenerated by the script.

:warning: Some configurations are in the `config.ini` file, but you must not change the data. This will affect the makefile. 
### Usage
```bash
docker-compose run scrapper make dump 
# or
cd ./src make dump
```
## sqlite3-to-mysql.sh

As mentioned before, the `dump.py` script only creates a `sql` file for `sqlite3`.  
The `sqlite3-to-mysql` script can easily translate the `dump_sqlite3.sql` to `mysql`. 

### Usage 
```
docker-compose run scrapper make convert_mysql
# or 
cd ./src make convert_mysql
```
### Source
The script was obtained from [tengla/sqlite3-to-mysql](https://github.com/tengla/sqlite3-to-mysql) respository

## Upload

The data generated by the `dump.py` and `sqlite3-to-mysql.sh` now can be uploaded to an online temporary storage. 

### Usage 
```bash 
docker-compose run scrapper make upload
# or
cd ./src make upload
```

The output should be like this:

```json
{"status":"success","data":{"url":"https://tmpfiles.org/39381/dump_mysql.sql"}}
{"status":"success","data":{"url":"https://tmpfiles.org/39382/dump_sqlite3.sql"}}
```

- The output give us where the files can be downloaded in the `data.url` section. 
- **After one hour the files will be deleted** from the online storage.  
- Anyone can download the files, once they have the url. 
- To download the files using `curl` add `dl` to the url address.

Example: 
```bash 
curl https://tmpfiles.org/dl/39381/dump_mysql.sql > my_file.sql
```


