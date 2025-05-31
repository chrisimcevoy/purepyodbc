FROM ghcr.io/astral-sh/uv:0.7.9-bookworm

# Install necessary system dependencies and tools
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git curl gnupg unixodbc unixodbc-dev freetds-bin freetds-dev tdsodbc odbc-postgresql \
    && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    && curl https://packages.microsoft.com/config/debian/12/prod.list | tee /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update -y && \
    ACCEPT_EULA=Y apt-get install msodbcsql17 -y \
    && curl -L -o mysql-connector-odbc.deb https://dev.mysql.com/get/Downloads/Connector-ODBC/9.3/mysql-connector-odbc_9.3.0-1debian12_amd64.deb \
    && dpkg -i mysql-connector-odbc.deb \
    && rm mysql-connector-odbc.deb

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy just dependency files early to leverage caching
COPY pyproject.toml uv.lock ./

ARG UV_PYTHON=python3.9
ENV UV_PYTHON=${UV_PYTHON}
RUN uv sync --locked

COPY . .
