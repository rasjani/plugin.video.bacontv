# -*- coding: utf-8 -*-
# vi: set shiftwidth=4 tabstop=4 expandtab:
__author__ = 'rasjani'


commands = {}

commands['INITDB']="""
BEGIN TRANSACTION create_tables;
  CREATE TABLE IF NOT EXISTS 'dbformat' (
    'version'   INTEGER UNIQUE NOT NULL
  );
  CREATE TABLE IF NOT EXISTS 'subscriptions' (
    'id'          INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    'subreddit'   TEXT NOT NULL
  );
  CREATE TABLE IF NOT EXISTS 'blocklist' (
    'id'          INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    'subreddit'   TEXT NOT NULL
  );
INSERT INTO 'dbformat' VALUES( 1 );

INSERT INTO 'subscriptions' (id, subreddit) VALUES( 1, 'all');
INSERT INTO 'subscriptions' (id, subreddit) VALUES( 2, 'videos');
INSERT INTO 'subscriptions' (id, subreddit) VALUES( 3, 'suomirap');
COMMIT TRANSACTION create_tables;"""


commands['SUBREDDITS']="""
SELECT
    subreddit
FROM
    'subscriptions'
"""
