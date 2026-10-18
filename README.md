# Inventory Management System

A Python inventory management application built with Flask,
a REST API, an interactive command-line interface (CLI),
and Open Food Facts integration.

## Features

- View all inventory products
- View individual products by ID
- Add products to inventory
- Update product prices, stock, names, and brands
- Delete products
- Search Open Food Facts by barcode
- Search Open Food Facts by product name
- Import external products into local inventory
- Validate user input and handle API errors
- Run automated tests using pytest

## Technologies

- Python 3.12
- Flask
- Requests
- Pytest
- Git and GitHub
- Open Food Facts API

## Project Structure

inventory-management-system/
app.py
cli.py
external_api.py
requirements.txt
README.md
.gitignore
tests/
conftest.py
test_crud.py
test_external_api.py
test_cli.py

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/inventory-management-system.git
cd inventory-management-system
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Running the Application

Start the Flask server:

```bash
python app.py
```

In a second terminal, start the CLI:

```bash
python cli.py
```

The CLI displays an interactive menu for managing products.

## REST API Endpoints

| Method | Endpoint                     | Description       |
| ------ | ---------------------------- | ----------------- |
| GET    | /inventory                   | View all products |
| GET    | /inventory/<id>              | View one product  |
| POST   | /inventory                   | Add a product     |
| PATCH  | /inventory/<id>              | Update a product  |
| DELETE | /inventory/<id>              | Delete a product  |
| GET    | /external/products/<barcode> | Barcode lookup    |
| GET    | /external/search?name=<name> | Search by name    |
| POST   | /inventory/import/<barcode>  | Import a product  |

## Example API Requests

View inventory:

```bash
curl http://127.0.0.1:5000/inventory
```

Add a product:

```bash
curl -X POST http://127.0.0.1:5000/inventory \
  -H "Content-Type: application/json" \
  -d '{"product_name":"Coffee","price":850,"quantity":12}'
```

Import a product:

```bash
curl -X POST \
  http://127.0.0.1:5000/inventory/import/3017620422003 \
  -H "Content-Type: application/json" \
  -d '{"price":650,"quantity":25}'
```

## Automated Testing

Run all tests:

```bash
python -m pytest -v
```

The test suite covers:

- Flask CRUD operations and validation
- Open Food Facts lookups and error handling
- External product imports
- CLI commands and user input validation

Latest verified result: 44 tests passed.

## Data Storage

The application uses a temporary Python list of dictionaries
to simulate an inventory database.

Data is not persistent. Restarting Flask resets the inventory
to its initial sample records.

## External API

Product information is retrieved from Open Food Facts.

The retailer supplies local selling prices and stock quantities
when importing products.

## Development Workflow

Git feature branches and pull requests are used to organize
development and review changes before merging.

## Limitations

- Inventory is stored in memory only.
- The application requires internet access for external lookups.
- Flask debug mode is intended for local development only.

````

Replace `YOUR_USERNAME` with `khishaplays` if that's the GitHub account you'll use for submission.

## Step 2 — Commit the README

You're currently on `feature/inventory-cli`. Run:

```bash
git add README.md
git commit -m "docs: add project setup and API documentation"
git status
````

## Step 3 — Prepare GitHub properly

One important detail: your branches were created consecutively, meaning `feature/inventory-cli` already contains the CRUD and external API commits. We need to merge them **in order** so your pull requests show meaningful changes rather than duplicating the whole project.

We'll use this sequence:

<box border radius="lg" padding={3}>
  <box align="center" gap={1}>
    <box background="surface-secondary" radius="md" padding={3} width="100%" align="center">
      **main**

      <caption>Initial project setup</caption>
    </box>
    <icon name="arrow-down" color="secondary"/>
    <box border radius="md" padding={3} width="100%" align="center">
      **feature/inventory-crud**

      <caption>CRUD routes + 15 tests</caption>
    </box>
    <icon name="arrow-down" color="secondary"/>
    <box border radius="md" padding={3} width="100%" align="center">
      **feature/openfoodfacts-integration**

      <caption>External integration + 13 tests</caption>
    </box>
    <icon name="arrow-down" color="secondary"/>
    <box border radius="md" padding={3} width="100%" align="center">
      **feature/inventory-cli**

      <caption>CLI + 16 tests + README</caption>
    </box>

  </box>
</box>

Before creating the pull requests, we need to confirm whether you've already connected this repository to GitHub.

Run:

```bash
git remote -v
git branch
git log --oneline -8
```

**Send me the output of those three commands.** I'll guide you through publishing the repository, merging the pull requests in the correct order, and preparing the final submission without losing any of your 44 passing tests.
