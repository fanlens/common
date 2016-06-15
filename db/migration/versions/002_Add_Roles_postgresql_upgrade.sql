CREATE ROLE "write.users"
  NOSUPERUSER NOINHERIT NOCREATEDB NOCREATEROLE NOREPLICATION;

CREATE ROLE "write.meta"
  NOSUPERUSER INHERIT NOCREATEDB NOCREATEROLE NOREPLICATION;

CREATE ROLE "write.data"
  NOSUPERUSER NOINHERIT NOCREATEDB NOCREATEROLE NOREPLICATION;

CREATE ROLE "write.config"
  NOSUPERUSER NOINHERIT NOCREATEDB NOCREATEROLE NOREPLICATION;

CREATE ROLE "read.users"
  NOSUPERUSER NOINHERIT NOCREATEDB NOCREATEROLE NOREPLICATION;

CREATE ROLE "read.meta"
  NOSUPERUSER INHERIT NOCREATEDB NOCREATEROLE NOREPLICATION;

CREATE ROLE "read.data"
  NOSUPERUSER NOINHERIT NOCREATEDB NOCREATEROLE NOREPLICATION;

CREATE ROLE "read.config"
  NOSUPERUSER NOINHERIT NOCREATEDB NOCREATEROLE NOREPLICATION;

CREATE ROLE "manage.users"
  NOSUPERUSER INHERIT NOCREATEDB NOCREATEROLE NOREPLICATION;
GRANT "read.users" TO "manage.users";
GRANT "write.users" TO "manage.users";

CREATE ROLE "manage.meta"
  NOSUPERUSER INHERIT NOCREATEDB NOCREATEROLE NOREPLICATION;
GRANT "read.meta" TO "manage.meta";
GRANT "write.meta" TO "manage.meta";

CREATE ROLE "manage.data"
  NOSUPERUSER INHERIT NOCREATEDB NOCREATEROLE NOREPLICATION;
GRANT "read.data" TO "manage.data";
GRANT "write.data" TO "manage.data";

CREATE ROLE "manage.config"
  NOSUPERUSER INHERIT NOCREATEDB NOCREATEROLE NOREPLICATION;
GRANT "read.config" TO "manage.data";
GRANT "write.config" TO "manage.config";