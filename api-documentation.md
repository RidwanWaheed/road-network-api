# Road Network API Documentation

This document provides detailed information about the Road Network API endpoints, request/response formats, and examples.

## Authentication

All API endpoints require authentication using the `X-API-Key` header.

Example:
```
X-API-Key: your_api_key_here
```

## API Endpoints

### Customers

#### Create Customer

Creates a new customer and generates an API key if not provided.

- **URL**: `/api/customers/`
- **Method**: `POST`
- **Auth Required**: No (This is the only endpoint that doesn't require authentication)

**Request Body**:
```json
{
  "name": "Example Customer",
  "api_key": "custom_api_key"  // Optional
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "name": "Example Customer",
  "api_key": "custom_api_key",
  "created_at": "2025-04-11T12:00:00.000Z"
}
```

#### Get Current Customer

Returns information about the authenticated customer.

- **URL**: `/api/customers/me`
- **Method**: `GET`
- **Auth Required**: Yes

**Response** (200 OK):
```json
{
  "id": 1,
  "name": "Example Customer",
  "api_key": "your_api_key",
  "created_at": "2025-04-11T12:00:00.000Z"
}
```

#### Get Customer by ID

Returns information about a specific customer.

- **URL**: `/api/customers/{customer_id}`
- **Method**: `GET`
- **Auth Required**: Yes
- **Access Control**: Customers can only access their own information

**Response** (200 OK):
```json
{
  "id": 1,
  "name": "Example Customer",
  "api_key": "your_api_key",
  "created_at": "2025-04-11T12:00:00.000Z"
}
```

#### Update Customer

Updates customer information.

- **URL**: `/api/customers/{customer_id}`
- **Method**: `PUT`
- **Auth Required**: Yes
- **Access Control**: Customers can only update their own information

**Request Body**:
```json
{
  "name": "Updated Customer Name"
}
```

**Response** (200 OK):
```json
{
  "id": 1,
  "name": "Updated Customer Name",
  "api_key": "your_api_key",
  "created_at": "2025-04-11T12:00:00.000Z"
}
```

### Networks

#### Create Network

Creates a new road network from GeoJSON data. 

- **URL**: `/api/networks/`
- **Method**: `POST`
- **Auth Required**: Yes

**Request Body**:
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

**Response** (201 Created):
```json
{
  "id": 1,
  "name": "Bayrischzell Road Network",
  "description": "Road network for Bayrischzell area",
  "customer_id": 1,
  "created_at": "2025-04-11T12:00:00.000Z",
  "updated_at": "2025-04-11T12:00:00.000Z",
  "version": 1,
  "node_count": 2,
  "edge_count": 1
}
```

#### Get Networks

Returns all networks owned by the authenticated customer.

- **URL**: `/api/networks/`
- **Method**: `GET`
- **Auth Required**: Yes
- **Query Parameters**:
  - `skip`: Number of items to skip (default: 0)
  - `limit`: Maximum number of items to return (default: 100)

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "name": "Bayrischzell Road Network",
    "description": "Road network for Bayrischzell area",
    "customer_id": 1,
    "created_at": "2025-04-11T12:00:00.000Z",
    "updated_at": "2025-04-11T12:00:00.000Z"
  }
]
```

#### Get Network by ID

Returns information about a specific network.

- **URL**: `/api/networks/{network_id}`
- **Method**: `GET`
- **Auth Required**: Yes
- **Access Control**: Customers can only access their own networks

**Response** (200 OK):
```json
{
  "id": 1,
  "name": "Bayrischzell Road Network",
  "description": "Road network for Bayrischzell area",
  "customer_id": 1,
  "created_at": "2025-04-11T12:00:00.000Z",
  "updated_at": "2025-04-11T12:00:00.000Z"
}
```

#### Update Network

Updates a network and creates a new version if GeoJSON data is provided.

- **URL**: `/api/networks/{network_id}`
- **Method**: `PUT`
- **Auth Required**: Yes
- **Access Control**: Customers can only update their own networks

**Request Body**:
```json
{
  "name": "Updated Network Name",
  "description": "Updated network description",
  "data": {
    "type": "FeatureCollection",
    "features": [
      // Updated GeoJSON features
    ]
  }
}
```

**Response** (200 OK):
```json
{
  "id": 1,
  "name": "Updated Network Name",
  "description": "Updated network description",
  "customer_id": 1,
  "created_at": "2025-04-11T12:00:00.000Z",
  "updated_at": "2025-04-11T13:00:00.000Z",
  "version": 2,
  "node_count": 3,
  "edge_count": 2
}
```

#### Get Network Edges

Returns the edges of a network as GeoJSON, with optional filtering by version or timestamp.

- **URL**: `/api/networks/{network_id}/edges`
- **Method**: `GET`
- **Auth Required**: Yes
- **Access Control**: Customers can only access their own networks
- **Query Parameters**:
  - `version`: Specific version to retrieve (optional)
  - `timestamp`: Point-in-time retrieval (ISO format) (optional)
  - `cursor`: Pagination cursor (optional)
  - `limit`: Maximum number of items to return (default: 100)

**Response** (200 OK):
```json
{
  "type": "FeatureCollection",
  "network_id": 1,
  "version": 2,
  "timestamp": "2025-04-11T13:00:00.000Z",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "LineString",
        "coordinates": [[10.0, 47.0], [10.1, 47.1], [10.2, 47.2]]
      },
      "properties": {
        "id": 1,
        "external_id": "edge-123",
        "source_node_id": 1,
        "target_node_id": 2,
        "is_current": true,
        "valid_from": "2025-04-11T13:00:00.000Z",
        "valid_to": null,
        "name": "Test Road",
        "highway": "residential",
        "length": 100.5
      }
    }
  ],
  "next_cursor": "encoded_cursor_value",
  "total_count": 50
}
```

## Error Responses

The API uses standard HTTP status codes to indicate the success or failure of requests.

### Common Error Responses

#### 401 Unauthorized
```json
{
  "detail": "Invalid API key"
}
```

#### 403 Forbidden
```json
{
  "detail": "Access to this resource is forbidden"
}
```

#### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

#### 422 Unprocessable Entity
```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## GeoJSON Format

### Network Input Format

The network data should be provided in GeoJSON format as a FeatureCollection containing LineString features for edges. If Point features are included, they will be used as nodes. Otherwise, nodes will be automatically generated at the endpoints of LineString features.

Example:
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "LineString",
        "coordinates": [[10.0, 47.0], [10.1, 47.1], [10.2, 47.2]]
      },
      "properties": {
        "id": "road-1",
        "name": "Test Road",
        "highway": "residential",
        "length": 100.5
      }
    },
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [10.0, 47.0]
      },
      "properties": {
        "id": "node-1",
        "type": "junction"
      }
    }
  ]
}
```

## Versioning

The API supports versioning of road networks:

1. When a network is created, it starts at version 1
2. When a network is updated with new GeoJSON data, a new version is created
3. Previous versions remain accessible via the version parameter
4. Edges have temporal validity (valid_from, valid_to) for point-in-time retrieval

## Pagination

The API supports cursor-based pagination for retrieving network edges:

1. The initial request returns a `next_cursor` if more results are available
2. Subsequent requests should include this cursor to fetch the next page
3. When no more results are available, `next_cursor` will be null