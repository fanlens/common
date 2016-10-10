-- Table: public.config

CREATE TABLE public.config
(
  key character varying NOT NULL,
  config jsonb NOT NULL,
  CONSTRAINT config_pkey PRIMARY KEY (key)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.config
  OWNER TO fanlens;
GRANT ALL ON TABLE public.config TO fanlens;
GRANT SELECT ON TABLE public.config TO "read.config";


-- Table: public.role

CREATE TABLE public.role
(
  id serial NOT NULL,
  name character varying(80),
  description character varying(255),
  CONSTRAINT role_pkey PRIMARY KEY (id),
  CONSTRAINT role_name_key UNIQUE (name)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.role
  OWNER TO fanlens;
GRANT ALL ON TABLE public.role TO fanlens;
GRANT SELECT ON TABLE public.role TO "read.users";
GRANT UPDATE, INSERT, DELETE ON TABLE public.role TO "write.users";


-- Table: public."user"

CREATE TABLE public."user"
(
  id serial NOT NULL,
  email character varying(255),
  password character varying(255),
  active boolean,
  confirmed_at timestamp without time zone,
  CONSTRAINT user_pkey PRIMARY KEY (id),
  CONSTRAINT user_email_key UNIQUE (email)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public."user"
  OWNER TO fanlens;
GRANT ALL ON TABLE public."user" TO fanlens;
GRANT SELECT ON TABLE public."user" TO "read.users";
GRANT UPDATE, INSERT, DELETE ON TABLE public."user" TO "write.users";


-- Table: public.roles_users

CREATE TABLE public.roles_users
(
  user_id integer,
  role_id integer,
  CONSTRAINT prim_key_roles_users PRIMARY KEY (user_id, role_id),
  CONSTRAINT roles_users_role_id_fkey FOREIGN KEY (role_id)
      REFERENCES public.role (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT roles_users_user_id_fkey FOREIGN KEY (user_id)
      REFERENCES public."user" (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.roles_users
  OWNER TO fanlens;
GRANT ALL ON TABLE public.roles_users TO fanlens;
GRANT SELECT ON TABLE public.roles_users TO "read.users";
GRANT UPDATE, INSERT, DELETE ON TABLE public.roles_users TO "write.users";


-- Table: public.user_tagset

CREATE TABLE public.user_tagset
(
  user_id integer NOT NULL,
  tagset_id integer NOT NULL,
  CONSTRAINT user_tagset_pkey PRIMARY KEY (user_id, tagset_id),
  CONSTRAINT user_tagset_tagset_id_fkey FOREIGN KEY (tagset_id)
      REFERENCES meta.tagsets (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE CASCADE,
  CONSTRAINT user_tagset_user_id_fkey FOREIGN KEY (user_id)
      REFERENCES public."user" (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE CASCADE
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.user_tagset
  OWNER TO fanlens;
GRANT ALL ON TABLE public.user_tagset TO fanlens;
GRANT SELECT ON TABLE public.user_tagset TO "read.users";
GRANT UPDATE, INSERT, DELETE ON TABLE public.roles_users TO "write.users";


-- Table: public.user_tag_comment

CREATE TABLE public.user_tag_comment
(
  user_id integer NOT NULL,
  tag character varying NOT NULL,
  comment_id character varying NOT NULL,
  CONSTRAINT user_tag_comment_pkey PRIMARY KEY (user_id, tag, comment_id),
  CONSTRAINT user_tag_comment_comment_id_fkey FOREIGN KEY (comment_id)
      REFERENCES data.facebook_comments (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE CASCADE,
  CONSTRAINT user_tag_comment_tag_fkey FOREIGN KEY (tag)
      REFERENCES meta.tags (tag) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE CASCADE,
  CONSTRAINT user_tag_comment_user_id_fkey FOREIGN KEY (user_id)
      REFERENCES public."user" (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE CASCADE
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.user_tag_comment
  OWNER TO fanlens;
GRANT ALL ON TABLE public.user_tag_comment TO fanlens;
GRANT SELECT ON TABLE public.user_tag_comment TO "read.users";
GRANT UPDATE, INSERT, DELETE ON TABLE public.user_tag_comment TO "write.users";

