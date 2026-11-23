# buywise-services container image. Used by the MCP integration tests (Testcontainers, ADR-064) and later by
# Kubernetes (phase 7). Build the jar first: make image (runs ./gradlew bootJar, then docker build).
# Runtime only: Java 25 JRE, no JDK or Gradle inside the image.
FROM eclipse-temurin:25-jre

# Run as a normal user, not root
RUN useradd --system --uid 10001 app
USER app
WORKDIR /app

COPY build/libs/buywise-services-0.1.0.jar app.jar

# Settings come from the environment, e.g. SPRING_DATASOURCE_URL, SPRING_DATASOURCE_USERNAME, SERVICES_DB_PASSWORD
EXPOSE 8081
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
