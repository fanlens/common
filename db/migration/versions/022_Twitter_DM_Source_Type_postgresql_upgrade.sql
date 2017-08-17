-- create the new table
CREATE TABLE activity.source_type
(
  "type" CHARACTER VARYING(32) NOT NULL,
  CONSTRAINT source_type_pkey PRIMARY KEY ("type")
)
WITH (
OIDS = FALSE
);

ALTER TABLE activity.source_type
  OWNER TO fanlens;

GRANT ALL ON TABLE activity.source_type TO fanlens;
GRANT SELECT ON TABLE activity.source_type TO "read.data";
GRANT INSERT, UPDATE, DELETE ON TABLE activity.source_type TO "write.data";

-- insert the values from the old enum
INSERT INTO activity.source_type (type)
  SELECT unnest(enum_range(NULL :: activity.TYPE)) AS type;

-- add the foreign type column to source
ALTER TABLE activity.source
  ADD COLUMN new_type CHARACTER VARYING(32) REFERENCES activity.source_type ON DELETE CASCADE;
UPDATE activity.source
SET "new_type" = "type";
ALTER TABLE activity.source
  DROP COLUMN "type";
ALTER TABLE activity.source
  RENAME COLUMN "new_type" TO "type";
ALTER TABLE activity.source
  ALTER COLUMN "type" SET NOT NULL;

-- drop the type
DROP TYPE activity."type";
