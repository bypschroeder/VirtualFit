# VirtualFit Frontend

Docker image for the VirtualFit frontend.

## Installation

### Running the frontend standalone

```bash
docker build -t {image_name} .
docker run -p 5173:5173 \
  --network {network_name} \
  -d {image_name}
```

or with docker-compose

```bash
docker-compose build frontend
docker-compose up -d frontend
```

### Running the whole VirtualFit-App

```bash
docker-compose --profile all build
docker-compose --profile app up -d
```

## Usage

The frontend is accessible at `http://localhost:5173/` or via `localhost` through the nginx reverse proxy (nginx container needs to run).

## Tech-Stack

The frontend is built using the following technologies and libraries:

- React TypeScript
- Vite (build tool)
- Tailwind CSS (styling framework)
- Shadcn UI (UI components)
- Zustand (state management)
- Three.js (3D rendering)
- Zod (data validation)
