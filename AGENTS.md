Practices to be followed in this Python Fast API codebase:

- Each service(inside services directory) should have these files: routes, constants, ios, models(database models), request dtos, response dtos, middlewares, repository, service, errors
- Use dependency injection if applicable
- Makefile to define repetitive commands
- Keep common packages which are non service(business logic) specific inside pkg directory
- Create a logger package inside pkg directory with best logging practices in mind
- Create a error handling package inside pkg directory with best error handling practices in mind
- Configuration management: keep in config directory
- Always think about the system design from distributed system point of view
- Always follow good practices like SOLID design principles, object oriented design and design patterns for coding
