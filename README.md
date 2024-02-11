### Running the Application with Docker Compose

To start the application, follow these steps:

1. Locate the docker-compose.yml file in the `chemondis/src/` directory.
2. Open a terminal and navigate to the directory containing the docker-compose.yml file.
3. Run the following command to start the application:
    ```bash
    sudo docker-compose up
    ```
    This command will initiate the Docker Compose setup and start running the application.

### Retrieving Data from the /weather Endpoint
To check if data can be retrieved from the /weather endpoint:

1. Ensure that the application is running using the steps mentioned above.
2. Open a web browser or use a tool like curl or httpie.
3. Make a request to the /weather endpoint with `q` as a query parameter with the city name as the value.
    ```bash
    # Example using curl
    curl http://localhost:8000/weather?q=London
    ```
    If the application is functioning correctly, you should receive current weather data for London city as a response from the /weather endpoint. 
    Adjust the endpoint and port based on your application's configuration.