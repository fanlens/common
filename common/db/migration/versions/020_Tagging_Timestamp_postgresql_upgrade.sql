ALTER TABLE activity.data ADD COLUMN IF NOT EXISTS crawled_ts timestamp with time zone;
UPDATE activity.data SET crawled_ts = now() WHERE crawled_ts IS NULL;
ALTER TABLE activity.data ALTER COLUMN crawled_ts SET NOT NULL;

ALTER TABLE activity.tagging ADD COLUMN IF NOT EXISTS tagging_ts timestamp with time zone;
UPDATE activity.tagging SET (tagging_ts) = (
  SELECT crawled_ts
  FROM activity.data
  WHERE activity.data.id = activity.tagging.data_id
  LIMIT 1
);
UPDATE activity.tagging SET tagging_ts = now() WHERE tagging_ts IS NULL;
ALTER TABLE activity.tagging ALTER COLUMN tagging_ts SET NOT NULL;
