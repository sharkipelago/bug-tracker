DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS issues;
DROP TABLE IF EXISTS assignments;

CREATE TABLE registrants (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  firstname TEXT NOT NULL,
  lastname TEXT NOT NULL
)

CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  firstname TEXT NOT NULL,
  lastname TEXT NOT NULL,
  admin_level INTEGER NOT NULL 
  -- 2 is admin (can accept/delete users, promote/demote users) 
  -- 1 is supervisor (can assign issues)
  -- 0 is regular user (can close/view issues)
);

CREATE TABLE issues (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  closer_id INTEGER, --user who closes issue
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user (id)
  FOREIGN KEY (closer_id) REFERENCES user (id)
);

CREATE TABLE assignments (
  issue_id INTEGER NOT NULL,
  assignee_id INTEGER NOT NULL,
  FOREIGN KEY (issue_id) REFERENCES issue (id),
  FOREIGN KEY (assignee_id) REFERENCES user (id)
)