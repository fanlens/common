-- Table: meta.tags

CREATE TABLE meta.tags
(
  tag character varying(64) NOT NULL,
  CONSTRAINT tags_pkey PRIMARY KEY (tag)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE meta.tags
  OWNER TO fanlens;
GRANT ALL ON TABLE meta.tags TO fanlens;
GRANT SELECT ON TABLE meta.tags TO "read.meta";
GRANT UPDATE, INSERT, DELETE ON TABLE meta.tags TO "write.meta";


-- Table: meta.tagsets

CREATE TABLE meta.tagsets
(
  id serial NOT NULL,
  title character varying(128) NOT NULL,
  CONSTRAINT tagsets_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE meta.tagsets
  OWNER TO fanlens;
GRANT ALL ON TABLE meta.tagsets TO fanlens;
GRANT SELECT ON TABLE meta.tagsets TO "read.meta";
GRANT UPDATE, INSERT, DELETE ON TABLE meta.tagsets TO "write.meta";


-- Table: meta.tag_tagset

CREATE TABLE meta.tag_tagset
(
  tag character varying NOT NULL,
  tagset_id integer NOT NULL,
  CONSTRAINT tag_tagset_pkey PRIMARY KEY (tag, tagset_id),
  CONSTRAINT tag_tagset_tag_fkey FOREIGN KEY (tag)
      REFERENCES meta.tags (tag) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE CASCADE,
  CONSTRAINT tag_tagset_tagset_id_fkey FOREIGN KEY (tagset_id)
      REFERENCES meta.tagsets (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE CASCADE
)
WITH (
  OIDS=FALSE
);
ALTER TABLE meta.tag_tagset
  OWNER TO fanlens;
GRANT ALL ON TABLE meta.tag_tagset TO fanlens;
GRANT SELECT ON TABLE meta.tag_tagset TO "read.meta";
GRANT UPDATE, INSERT, DELETE ON TABLE meta.tag_tagset TO "write.meta";

