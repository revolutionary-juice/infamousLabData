SELECT 'CREATE DATABASE redash'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'redash')\gexec
