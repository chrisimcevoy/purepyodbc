ARG BASE_IMAGE=python:3.9-bookworm
FROM ${BASE_IMAGE}

# Install necessary system dependencies and tools
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git curl unixodbc unixodbc-dev freetds-bin freetds-dev tdsodbc odbc-postgresql \
    && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    && curl https://packages.microsoft.com/config/debian/12/prod.list | tee /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update -y && \
    ACCEPT_EULA=Y apt-get install msodbcsql17 -y

# Configure Git to consider the directory safe
RUN git config --global --add safe.directory /usr/src/app

# Install Poetry
ENV POETRY_HOME=/opt/poetry
ENV PATH="$POETRY_HOME/bin:$PATH"
RUN curl -sSL https://install.python-poetry.org | python -

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the application files into the container
COPY . .

# Register drivers with the driver manager.
RUN odbcinst -i -d -f driver_templates/tds.driver.template && \
    odbcinst -i -d -f driver_templates/pgsql.driver.template && \
    odbcinst -i -d -f driver_templates/msodbc.driver.template

# Install Python dependencies
RUN poetry install
