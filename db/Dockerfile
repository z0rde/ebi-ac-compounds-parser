FROM postgres:alpine
ENV POSTGRES_PASSWORD=secrekt
ENV POSTGRES_USER=ebi-as
ENV POSTGRES_DB=compounds
COPY create_fixtures.sql /docker-entrypoint-initdb.d/create_fixtures.sql
