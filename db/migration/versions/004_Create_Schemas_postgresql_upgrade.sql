CREATE SCHEMA meta
  AUTHORIZATION fanlens;

GRANT ALL ON SCHEMA meta TO fanlens;
GRANT USAGE ON SCHEMA meta TO "write.meta";
GRANT USAGE ON SCHEMA meta TO "read.meta";

CREATE SCHEMA data
  AUTHORIZATION fanlens;

GRANT ALL ON SCHEMA data TO fanlens;
GRANT USAGE ON SCHEMA data TO "read.data";
GRANT USAGE ON SCHEMA data TO "write.data";