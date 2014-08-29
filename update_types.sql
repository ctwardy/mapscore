ALTER TABLE framework_case
RENAME TO mapscore_case;

ALTER TABLE framework_test
RENAME TO test;

ALTER TABLE framework_model
RENAME TO model;

ALTER TABLE framework_account
RENAME TO account;

ALTER TABLE framework_model_account_link
RENAME TO model_account_link;

ALTER TABLE framework_test_model_link
RENAME TO test_model_link;

ALTER TABLE framework_mainhits
RENAME TO mainhits;

ALTER TABLE framework_terminated_accounts
RENAME TO terminated_accounts;

UPDATE account
SET photosizex = '0'
WHERE photosizex = '';

ALTER TABLE account
ALTER COLUMN photosizex
TYPE integer USING photosizex::integer;

ALTER TABLE account
ALTER COLUMN photosizex
SET DEFAULT 0;

UPDATE account
SET photosizey = '0'
WHERE photosizey = '';

ALTER TABLE account
ALTER COLUMN photosizey
TYPE integer USING photosizey::integer;

ALTER TABLE account
ALTER COLUMN photosizey
SET DEFAULT 0;

ALTER TABLE account
ALTER COLUMN sessionticker
TYPE integer USING sessionticker::integer;

ALTER TABLE account
ALTER COLUMN sessionticker
SET DEFAULT 0;

ALTER TABLE account
ALTER COLUMN completedtests
TYPE integer USING completedtests::integer;

ALTER TABLE account
ALTER COLUMN completedtests
SET DEFAULT 0;

ALTER TABLE account
ALTER COLUMN deleted_models
TYPE integer USING deleted_models::integer;

ALTER TABLE account
ALTER COLUMN deleted_models
SET DEFAULT 0;

ALTER TABLE account
ALTER COLUMN profpicrefresh
TYPE integer USING profpicrefresh::integer;

ALTER TABLE account
ALTER COLUMN profpicrefresh
SET DEFAULT 0;

ALTER TABLE terminated_accounts
ALTER COLUMN sessionticker
TYPE integer USING sessionticker::integer;

ALTER TABLE terminated_accounts
ALTER COLUMN sessionticker
SET DEFAULT 0;

ALTER TABLE terminated_accounts
ALTER COLUMN deleted_models
TYPE integer USING deleted_models::integer;

ALTER TABLE terminated_accounts
ALTER COLUMN deleted_models
SET DEFAULT 0;

ALTER TABLE terminated_accounts
ALTER COLUMN completedtests
TYPE integer USING completedtests::integer;

ALTER TABLE terminated_accounts
ALTER COLUMN completedtests
SET DEFAULT 0;

ALTER TABLE mainhits
ALTER COLUMN hits
TYPE integer USING hits::integer;

ALTER TABLE mainhits
ALTER COLUMN hits
SET DEFAULT 0;

ALTER TABLE test
ALTER COLUMN grayrefresh
TYPE integer USING grayrefresh::integer;

ALTER TABLE test
ALTER COLUMN grayrefresh
SET DEFAULT 0;

ALTER TABLE model
RENAME "Completed_cases" TO completed_cases;

ALTER TABLE model
ALTER COLUMN completed_cases
TYPE integer USING completed_cases::integer;

ALTER TABLE model
ALTER COLUMN completed_cases
SET DEFAULT 0;

ALTER TABLE model
RENAME model_avgrating TO avgrating;

ALTER TABLE model
RENAME "model_nameID" TO name_id;

ALTER TABLE model
RENAME "Description" TO description;

ALTER TABLE test
ALTER COLUMN test_rating
SET DEFAULT 'unrated';

ALTER TABLE test
RENAME "Active" TO active;

ALTER TABLE test
ALTER COLUMN active
SET DEFAULT TRUE;

ALTER TABLE test
ALTER COLUMN nav
SET DEFAULT '0';

ALTER TABLE test
ALTER COLUMN show_instructions
SET DEFAULT TRUE;

ALTER TABLE model
ALTER COLUMN avgrating
SET DEFAULT 'unrated';

ALTER TABLE mainhits
ALTER COLUMN hits
SET DEFAULT 0;
