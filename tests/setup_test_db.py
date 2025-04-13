import os
import sys

import psycopg2


def setup_test_db():
    """Set up the test database with PostGIS extension"""
    conn = psycopg2.connect(
        dbname="postgres", user="postgres", password="postgres", host="localhost"
    )
    conn.autocommit = True
    cursor = conn.cursor()

    # Check if database exists
    cursor.execute("SELECT 1 FROM pg_database WHERE datname='road_network_test'")
    if not cursor.fetchone():
        # Create database
        cursor.execute("CREATE DATABASE road_network_test")

    # Connect to the test database
    conn.close()
    conn = psycopg2.connect(
        dbname="road_network_test",
        user="postgres",
        password="postgres",
        host="localhost",
    )
    conn.autocommit = True
    cursor = conn.cursor()

    # Create PostGIS extension if it doesn't exist
    cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    conn.close()
    print("Test database set up successfully")


def teardown_test_db():
    """Drop the test database"""
    conn = psycopg2.connect(
        dbname="postgres", user="postgres", password="postgres", host="localhost"
    )
    conn.autocommit = True
    cursor = conn.cursor()

    # Terminate all connections to the test database
    cursor.execute(
        "SELECT pg_terminate_backend(pg_stat_activity.pid) "
        "FROM pg_stat_activity "
        "WHERE pg_stat_activity.datname = 'road_network_test' "
        "AND pid <> pg_backend_pid()"
    )

    # Drop database
    cursor.execute("DROP DATABASE IF EXISTS road_network_test")

    conn.close()
    print("Test database dropped successfully")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--teardown":
        teardown_test_db()
    else:
        setup_test_db()
