# Requinsta

Universal media request system for self-hosted home media libraries.

## What is Requinsta?

Requinsta allows family and friends to request any type of media (books, movies, TV shows, music, comics, etc.) from your self-hosted media servers. Unlike existing solutions that focus only on movies/TV, Requinsta handles all media types through a modular plugin system.

## Features (Planned)

- Books, audiobooks, movies, TV, music, comics, and more
- Modular plugin system for metadata providers and media managers
- Easy Docker deployment for Unraid and Docker Compose
- Multi-user support with request collaboration
- Universal search across all media types

## Current Status

**MVP Complete** - Basic functionality working:

- User registration/authentication
- Media request creation and viewing
- Admin panel for request management
- Docker deployment ready

## Quick Start

```bash
docker-compose up
```

Frontend: http://localhost:3000
Backend API: http://localhost:8000

### First Admin User (shouldn't be needed, should be done by UI)

```bash
docker compose exec db psql -U requinsta -d requinsta -c "UPDATE users SET role = 'ADMIN' WHERE email = 'your@email.com';"
```

## Contributing

Interested in contributing? Check out our Issues for planned features and bugs.

## License

MIT License - see LICENSE file for details.
