from sqlalchemy import text

SCHEMA = 'activity'

recreate_job_table_sql = text('''
DROP TABLE IF EXISTS activity.modelfile;

CREATE TABLE activity.modelfile
(
    model_id UUID NOT NULL,
    file BYTEA NOT NULL,
    CONSTRAINT modelfile_pkey PRIMARY KEY (model_id),
    CONSTRAINT modelfile_model_id_fkey FOREIGN KEY (model_id)
        REFERENCES activity.model (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE activity.modelfile
    OWNER TO fanlens;

GRANT ALL ON TABLE activity.modelfile TO fanlens;

GRANT SELECT ON TABLE activity.modelfile TO "read.data";

GRANT INSERT, UPDATE, DELETE ON TABLE activity.modelfile TO "write.data";
''')


def upgrade(migrate_engine):
    with migrate_engine.begin() as transaction:
        transaction.execute(text('''DROP TABLE IF EXISTS activity.modelfile'''))


def downgrade(migrate_engine):
    with migrate_engine.begin() as transaction:
        transaction.execute(recreate_job_table_sql)
