# Arista CVP Webhook Receiver

This is a Python application built using the FastAPI framework to receive webhooks sent by Arista CloudVision Portal (CVP).

## Installation

1. Clone the repository:

    ```shell
    git clone https://github.com/your/repository.git
    ```

2. Create the virtualenv

    ```shell
    sudo apt install python3-virtualenv -y
    virtualenv venv
    ```

3. Install the required dependencies using `pip`:

    ```shell
    source venv/bin/activate
    pip install -r requirements.txt
    ```

## Usage

1. Start the application:

    In development mode:

    ```shell
    uvicorn webhook_listener:app --reload --port 8081
    ```

2. Access the application in your web browser at [http://localhost:8081](http://localhost:8081).

## Endpoints

The application provides the following endpoints:

- `GET /`: Home page that serves a static HTML content from the `static/home.html` file.

- `POST /ipf-webhook`: Endpoint to receive Arista CVP webhooks. It expects a JSON payload conforming to the `AristaCvpWebhook` model. The received webhook data is printed to the console.

- `GET /simulate-cvp-webhook`: This endpoint is used for testing purposes. It accepts an optional query parameter `simulated_webhook` which can be used to simulate a webhook payload. If no `simulated_webhook` is provided, it will load a sample webhook payload from the `static/webhook_example_down.json` file. The simulated webhook payload is rendered using the `test_webhook.html` template.

## Static Files and Templates

The application serves static files from the `static` directory, including the `home.html` file.

Templates are stored in the `templates` directory. The `test_webhook.html` template is used to render the simulated webhook payload.

## Dependencies

The application utilizes the following dependencies:

- `fastapi`: A modern, fast (high-performance), web framework for building APIs.

- `uvicorn`: A lightning-fast ASGI server implementation, which allows running FastAPI applications.

- `pydantic`: A library for data validation and serialization using Python type hints.

## Support

If you have any questions or need further assistance, please create an issue on the [repository](https://github.com/your/repository).
