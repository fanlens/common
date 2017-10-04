-- recreate original type
CREATE TYPE activity."type" AS ENUM
('facebook', 'twitter', 'crunchbase', 'generic');

ALTER TYPE activity."type"
OWNER TO fanlens;

-- back up source
DROP TABLE IF EXISTS activity.source_backup_v22;
SELECT * INTO activity.source_backup_v22 from activity.source;

-- delete the sources using now inconsistent types
DELETE FROM activity.source
WHERE NOT "type" IN (SELECT unnest(enum_range(NULL :: activity."type") :: character varying[]));

-- add column to source
ALTER TABLE activity.source
  ADD COLUMN old_type activity."type";
UPDATE activity.source
SET "old_type" = "type"::activity."type";
ALTER TABLE activity.source
  DROP COLUMN "type";
ALTER TABLE activity.source
  RENAME COLUMN old_type TO "type";
ALTER TABLE activity.source
  ALTER COLUMN "type" SET NOT NULL;

-- delete the source_type table
DROP TABLE activity.source_type;
