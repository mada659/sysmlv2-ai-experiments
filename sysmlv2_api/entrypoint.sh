#!/bin/bash
set -e

# Inject POSTGRES_PASSWORD into persistence.xml at runtime
sed -i "s|value=\"mysecretpassword\"|value=\"${POSTGRES_PASSWORD}\"|g" \
    /app/conf/META-INF/persistence.xml

exec /app/bin/sysml-v2-api-services -Dplay.http.secret.key="${PLAY_SECRET}"
