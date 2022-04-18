FROM postgres:14.2
LABEL author="Erick Brunoro"

EXPOSE "${POSTGRES_PORT}"

RUN localedef -i pt_BR -c -f UTF-8 -A /usr/share/locale/locale.alias pt_BR.UTF-8
ENV LANG pt_BR.utf8

COPY ./db-init-scripts/ /docker-entrypoint-initdb.d/
RUN ["chmod", "755", "/docker-entrypoint-initdb.d", "-R"]