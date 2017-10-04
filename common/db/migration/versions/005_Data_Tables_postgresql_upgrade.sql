-- Table: data.facebook_posts

CREATE TABLE data.facebook_posts
(
  id character varying NOT NULL,
  data jsonb NOT NULL,
  meta jsonb NOT NULL,
  crawl_ts timestamp with time zone,
  CONSTRAINT facebook_posts_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE data.facebook_posts
  OWNER TO fanlens;
GRANT ALL ON TABLE data.facebook_posts TO fanlens;
GRANT SELECT ON TABLE data.facebook_posts TO "read.data";
GRANT UPDATE, INSERT, DELETE ON TABLE data.facebook_posts TO "write.data";

-- Index: data.facebook_posts_crawl_ts_index

CREATE INDEX facebook_posts_crawl_ts_index
  ON data.facebook_posts
  USING btree
  (crawl_ts);

-- Index: data.facebook_posts_date_index

CREATE INDEX facebook_posts_date_index
  ON data.facebook_posts
  USING btree
  ((data -> 'created_time'::text));

-- Index: data.facebook_posts_page_index

CREATE INDEX facebook_posts_page_index
  ON data.facebook_posts
  USING btree
  ((meta -> 'page'::text));


-- Table: data.facebook_comments

CREATE TABLE data.facebook_comments
(
  post_id character varying NOT NULL,
  id character varying NOT NULL,
  data jsonb NOT NULL,
  meta jsonb NOT NULL,
  crawl_ts timestamp with time zone,
  CONSTRAINT facebook_comments_pkey PRIMARY KEY (id),
  CONSTRAINT facebook_comments_post_id_fkey FOREIGN KEY (post_id)
      REFERENCES data.facebook_posts (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE CASCADE
)
WITH (
  OIDS=FALSE
);
ALTER TABLE data.facebook_comments
  OWNER TO fanlens;
GRANT ALL ON TABLE data.facebook_comments TO fanlens;
GRANT SELECT ON TABLE data.facebook_comments TO "read.data";
GRANT UPDATE, INSERT, DELETE ON TABLE data.facebook_comments TO "write.data";

-- Index: data.facebook_comments_crawl_ts_index

CREATE INDEX facebook_comments_crawl_ts_index
  ON data.facebook_comments
  USING btree
  (crawl_ts);

-- Index: data.facebook_comments_date_index

CREATE INDEX facebook_comments_date_index
  ON data.facebook_comments
  USING btree
  ((data -> 'created_time'::text));

-- Index: data.facebook_comments_lang_index

CREATE INDEX facebook_comments_lang_index
  ON data.facebook_comments
  USING btree
  ((meta -> 'lang'::text));

-- Index: data.facebook_comments_page_index

CREATE INDEX facebook_comments_page_index
  ON data.facebook_comments
  USING btree
  ((meta -> 'page'::text));

-- Index: data.facebook_comments_tags_index

CREATE INDEX facebook_comments_tags_index
  ON data.facebook_comments
  USING gin
  ((meta -> 'tags'::text));


-- Table: data.facebook_reactions

CREATE TABLE data.facebook_reactions
(
  post_id character varying NOT NULL,
  id character varying NOT NULL,
  data jsonb NOT NULL,
  meta jsonb NOT NULL,
  crawl_ts timestamp with time zone,
  CONSTRAINT facebook_reactions_pkey PRIMARY KEY (id),
  CONSTRAINT facebook_reactions_post_id_fkey FOREIGN KEY (post_id)
      REFERENCES data.facebook_posts (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE CASCADE
)
WITH (
  OIDS=FALSE
);
ALTER TABLE data.facebook_reactions
  OWNER TO fanlens;
GRANT ALL ON TABLE data.facebook_reactions TO fanlens;
GRANT SELECT ON TABLE data.facebook_reactions TO "read.data";
GRANT UPDATE, INSERT, DELETE ON TABLE data.facebook_reactions TO "write.data";

-- Index: data.facebook_reactions_crawl_ts_index

CREATE INDEX facebook_reactions_crawl_ts_index
  ON data.facebook_reactions
  USING btree
  (crawl_ts);

-- Index: data.facebook_reactions_date_index

CREATE INDEX facebook_reactions_date_index
  ON data.facebook_reactions
  USING btree
  ((data -> 'created_time'::text));

-- Index: data.facebook_reactions_page_index

CREATE INDEX facebook_reactions_page_index
  ON data.facebook_reactions
  USING btree
  ((meta -> 'page'::text));


