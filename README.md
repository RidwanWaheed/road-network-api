# Road Network API

A RESTful API for managing road networks with versioning support, built using FastAPI, PostgreSQL, and PostGIS.

## Features

- Create and manage road networks with GeoJSON data
- Version control for road networks
- Spatial queries for network edges and nodes
- Customer authentication via API keys
- Docker containerization for easy deployment

## Tech Stack

- **FastAPI**: Modern, high-performance web framework for building APIs
- **PostgreSQL**: Relational database
- **PostGIS**: Spatial database extension for PostgreSQL
- **SQLAlchemy**: ORM for database interactions
- **Alembic**: Database migration tool
- **Docker**: Containerization
- **Pytest**: Testing framework

## Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- PostgreSQL with PostGIS extension (for local development without Docker)

## Getting Started

### Using Docker (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/yourusername/road-network-api.git
cd road-network-api
```

2. Start the application with Docker Compose:
```bash
docker-compose up -d
```

3. Run database migrations:
```bash
docker-compose exec api alembic upgrade head
```

4. The API is now available at http://localhost:8000

### Local Development Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/road-network-api.git
cd road-network-api
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Set up PostgreSQL with PostGIS extension locally.

4. Create `.env` file with the following content (adjust as needed):
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/roadnetworkdb
API_TITLE=Road Network API
API_VERSION=0.1.0
DEBUG=True
```

5. Run database migrations:
```bash
alembic upgrade head
```

6. Start the development server:
```bash
uvicorn main:app --reload
```

7. The API is now available at http://localhost:8000

## Database Schema

![Database Schema](ERD.png)

- **customers**: API users with authentication keys
- **networks**: Road network metadata
- **network_versions**: Version control for networks
- **nodes**: Junction points in the network
- **edges**: Road segments connecting nodes

## API Endpoints

### Authentication

All API endpoints require authentication via the `X-API-Key` header.

### Customers

- `POST /api/customers/`: Create a new customer
- `GET /api/customers/me`: Get current customer info
- `GET /api/customers/{customer_id}`: Get customer by ID
- `PUT /api/customers/{customer_id}`: Update customer

### Networks

- `POST /api/networks/`: Create a new network
- `GET /api/networks/`: Get all networks for current customer
- `GET /api/networks/{network_id}`: Get network by ID
- `PUT /api/networks/{network_id}`: Update network
- `GET /api/networks/{network_id}/edges`: Get network edges with optional version or timestamp

## Creating a Network

To create a new network, send a POST request to `/api/networks/` with the following JSON:

```json
{
  "name": "Bayrischzell Road Network",
  "description": "Road network for Bayrischzell area",
  "data": {
    "type": "FeatureCollection",
    "features": [
      {
        "type": "Feature",
        "geometry": {
          "type": "LineString",
          "coordinates": [[10.0, 47.0], [10.1, 47.1], [10.2, 47.2]]
        },
        "properties": {
          "name": "Test Road",
          "highway": "residential",
          "length": 100.5
        }
      }
    ]
  }
}
```

## API Usage

For detailed information about API endpoints, request/response formats, and examples, please refer to the [API Documentation](api-documentation.md) file included in this repository.


## Running Tests

### With Docker:

```bash
docker-compose exec api pytest
```

### Locally:

```bash
# Set up test database
python tests/setup_test_db.py

# Run tests
pytest
```

## Development Environment

For a development setup with hot-reloading, use:

```bash
# Create development docker-compose.override.yml
cat > docker-compose.override.yml << EOL
services:
  api:
    volumes:
      - ./:/app
    environment:
      - DEBUG=True
    command: ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
EOL

# Start with Docker Compose
docker-compose up -d
```

## Future Improvements

- Add support for more complex geospatial queries
- Implement caching layer for frequently accessed networks
- Add authentication with JWT tokens
- Expand analytics capabilities for network usage

## License

[MIT License](LICENSE)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request