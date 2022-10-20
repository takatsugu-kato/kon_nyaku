```
sqlite3 db.sqlite3
UPDATE django_content_type SET app_label='mt' WHERE app_label='translate';
ALTER TABLE translate_file RENAME TO mt_file;
ALTER TABLE translate_glossary RENAME TO mt_glossary;
ALTER TABLE translate_text RENAME TO mt_text;
```
