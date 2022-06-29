DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS issue;
DROP TABLE IF EXISTS assignee;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  firstname TEXT NOT NULL,
  lastname TEXT NOT NULL
);

CREATE TABLE issue (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  closer_id INTEGER, --user who closes issue
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user (id)
  FOREIGN KEY (closer_id) REFERENCES user (id)
);

CREATE TABLE assignee (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    issue_id INTEGER NOT NULL,
    assignee_id INTEGER NOT NULL,
    FOREIGN KEY (issue_id) REFERENCES issue (id),
    FOREIGN KEY (assignee_id) REFERENCES user (id)
)