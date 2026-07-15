# Appify Social API Documentation

This documentation describes the backend API of the Appify Social Media platform. It outlines the architectural choices, features, database design, and library selections made during development.

---

## 1. Why Choose This Stack (API)?

The backend application is built using **Python, FastAPI, and SQLAlchemy (Async)**:

*   **FastAPI**: Selected for its exceptional speed, fully asynchronous nature, and native support for Python type hints. It automatically generates interactive Swagger/OpenAPI documentation, which accelerates testing and integration.
*   **Python**: Offers clean readability, rapid development speed, and a mature ecosystem for web applications.
*   **SQLAlchemy (Async)**: The premier SQL toolkit and ORM for Python. It allows writing clean, asynchronous database operations, maximizing server throughput by freeing up threads while waiting for DB operations.

---

## 2. Why Choose This Stack DB?

The application database uses **PostgreSQL**:

*   **PostgreSQL**: A highly reliable, open-source object-relational database. It provides full ACID compliance, exceptional handling of high-concurrency workflows, and robust support for relational indexes and constraints.
*   **Native Type & Extension Support**: Features native `UUID` types (via `uuid-ossp`) and `ENUM` types, ensuring strong data integrity directly at the database level.
*   **Performance under Join operations**: Ideal for relational structures like social feeds, where posts, comments, likes, and users are heavily interconnected.

---

## 3. What Are the Features?

*   **JWT Token Authorization**: Enforces access token verification using OAuth2 password bearer schemes.
*   **Timeline API**: Serves a chronological feed of posts with offset-based pagination to support client-side infinite scroll.
*   **Privacy Model filtering**: Enforces user access constraints, ensuring private posts are only visible to their authors.
*   **Hierarchical Comments**: Returns structured comments containing their nested child replies, built in linear time.
*   **Engagement Toggles**: Exposes flexible endpoints to like or unlike posts and comments, and returns the updated counts instantly.
*   **Engagement Listing**: Exposes endpoints to retrieve the list of users who have liked any given post or comment.

---

## 4. Why We Choose These Libraries

To support the core FastAPI framework, we selected several specialized libraries:

*   **`uvicorn`**:
    *   *Purpose*: ASGI web server.
    *   *Why chosen*: It is the standard high-performance ASGI server for Python web applications, built on `uvloop` to achieve extreme concurrency.
*   **`asyncpg`**:
    *   *Purpose*: Database client driver.
    *   *Why chosen*: Unlike synchronous drivers (like `psycopg2`), `asyncpg` is built specifically for async execution and is significantly faster, enabling low-latency database queries.
*   **`passlib` (with `bcrypt` backend)**:
    *   *Purpose*: Password hashing and verification.
    *   *Why chosen*: Provides an industry-standard, secure password hashing implementation that resists brute-force attacks.
*   **`pyjwt`**:
    *   *Purpose*: JSON Web Token encoding and decoding.
    *   *Why chosen*: Simple, lightweight, and robust library for signing and validating authentication tokens.
*   **`python-decouple`**:
    *   *Purpose*: Environment configuration manager.
    *   *Why chosen*: Safely isolates application secrets (such as database URLs and JWT secret keys) into a `.env` file, preventing credentials from being committed to version control.
*   **`email-validator`**:
    *   *Purpose*: Email validation.
    *   *Why chosen*: Built directly into Pydantic, ensuring that only syntax-correct emails are registered.
