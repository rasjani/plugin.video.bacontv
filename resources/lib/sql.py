# -*- coding: utf-8 -*-
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
COMMIT TRANSACTION create_tables;"""


commands['SUBREDDITS']="""
SELECT
    'subreddit'
FROM
    'subscriptions'
"""
