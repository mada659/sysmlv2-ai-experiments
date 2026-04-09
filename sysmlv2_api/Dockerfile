# Stage 1: The "Builder"
# We've changed the base image to one that uses Java 11
# FROM sbtscala/scala-sbt:eclipse-temurin-11.0.22_7_1.10.0_2.13.12 AS builder
FROM sbtscala/scala-sbt:eclipse-temurin-11.0.17_8_1.8.2_2.13.10 AS builder
 
WORKDIR /app
RUN git clone https://github.com/Systems-Modeling/SysML-v2-API-Services.git .
# This sbt command will now run in a compatible Java 11 environment
RUN sbt clean stage
 
# Stage 2: The "Final" Runtime Image
# We also change this to a Java 11 runtime for consistency
# This might need to be changed to match architecture?
FROM eclipse-temurin:11-jre
 
# Install bash, which is required by the sbt startup script
RUN apt-get update && apt-get install -y --no-install-recommends bash && rm -rf /var/lib/apt/lists/*
 
WORKDIR /app
# Copy the compiled application from the builder stage
COPY --from=builder /app/target/universal/stage .
 
# Fix hardcoded localhost and wrong DB name in persistence.xml at build time
RUN sed -i \
    's|jdbc:postgresql://localhost:5432/sysml2|jdbc:postgresql://postgres:5432/sysmlv2|g' \
    /app/conf/META-INF/persistence.xml

# Change Hibernate DDL mode from 'create-drop' (wipes DB on every start/stop)
# to 'update' (creates tables on first run, preserves data across restarts)
RUN sed -i \
    's|value="create-drop"|value="update"|g' \
    /app/conf/META-INF/persistence.xml

# Entrypoint injects POSTGRES_PASSWORD and PLAY_SECRET at runtime
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

EXPOSE 9000
ENTRYPOINT ["/app/entrypoint.sh"]