# gta_aqui
This application provides a web interface for managing firewall rules allowing the host to control which IPs can communicate with the host.

The application stores IPs of registered users in the host machine and blacklists any other IP that is not associated with the registered users.

The application also has a client which enables the clients attempting to connect to host without having to provide public IP via 3rd party communication apps.

This application is specifically designed for GTA Online.

##Requirements
1. Python3.6 +
2. Flask

##Hosting the server
Setup env.json as required.

-IP_ADDRESS : Determines which IP the web application will be hosted on

-PORT : Determines which PORT the web application will be hosted on

-SECRET_KEY : Secret key for session management

-ADMIN_USER : Username for admin access

-ADMIN_PASS : Password for admin access

Run server.py to start server.

##Registering the client
1. Sign up as a user in the server web application.
2. Once admin has approved your request, log in and copy the generated token.
3. Run client.py to register your public IP onto the server. Enter the server IP and host, your username and the token when requested.

##Updating the client IP
After the client setup has been performed once, client.py can be run again to register new IP. This process will performed based on the configuration from initial client setup.



