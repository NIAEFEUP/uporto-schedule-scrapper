#!/usr/bin/env sh
# https://github.com/tengla/sqlite3-to-mysql
if test -z "$VARCHAR"
then
	VARCHAR="255"
fi

sed \
-e '/PRAGMA.*;/ d' \
-e '/BEGIN TRANSACTION.*/ d' \
-e '/COMMIT;/ d' \
-e '/.*sqlite_sequence.*;/d' \
-e "s/ varchar/ varchar($VARCHAR)/g" \
-e 's/"/`/g' \
-e 's/CREATE TABLE \(`\w\+`\)/DROP TABLE IF EXISTS \1;\nCREATE TABLE \1/' \
-e 's/\(CREATE TABLE.*\)\(PRIMARY KEY\) \(AUTOINCREMENT\)\(.*\)\();\)/\1AUTO_INCREMENT\4, PRIMARY KEY(id)\5/' \
-e "s/'t'/1/g" \
-e "s/'f'/0/g" \
-e "s/'\([0-9]\+\),\([0-9]\+\)'/\1\.\2/g" \
$1 > tmp.sql

echo "BEGIN;" > ./scripts/dump/data/01_data.sql
echo "
	ALTER TABLE course_group ALTER COLUMN name TYPE varchar(255);
	DELETE FROM info;
	DELETE FROM slot_class;
	DELETE FROM slot_professor;
	DELETE FROM course_metadata;
	DELETE FROM class;
	DELETE FROM slot ;
	DELETE FROM professor;
	DELETE FROM course_unit;
	DELETE FROM course;
	DELETE FROM faculty;
	DELETE FROM course_group;
" >> ./scripts/dump/data/01_data.sql

cat tmp.sql >> ./scripts/dump/data/01_data.sql

rm tmp.sql

echo "COMMIT;" >> ./scripts/dump/data/01_data.sql
