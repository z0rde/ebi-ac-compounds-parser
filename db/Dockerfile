FROM postgres:alpine
ENV PGUSER=postgres
ENV PGPASSWORD=secrekt
ENV POSTGRES_PASSWORD=secrekt
ENV POSTGRES_USER=postgres
ENV POSTGRES_DB=compounds
COPY create_fixtures.sql /docker-entrypoint-initdb.d/create_fixtures.sql
