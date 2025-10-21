# FlashCase Frontend

Next.js frontend for FlashCase flashcard application.

## Features

- Next.js 15 with App Router
- TypeScript for type safety
- Tailwind CSS for styling
- Core pages: Dashboard, Discover, Study, Card Creator
- Responsive design for all devices

## Setup

### Local Development

1. Install dependencies:
```bash
npm install
```

2. Copy environment file:
```bash
cp .env.local.example .env.local
```

3. Run the development server:
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Docker

Build and run with Docker:
```bash
docker build -t flashcase-frontend .
docker run -p 3000:3000 flashcase-frontend
```

## Pages

- `/` - Home page with hero and features
- `/dashboard` - User dashboard with stats and recent activity
- `/discover` - Browse and search community decks
- `/study` - Study session with spaced repetition
- `/create` - Create flashcards manually or with AI assistance

## Project Structure

```
frontend/
├── app/
│   ├── dashboard/      # Dashboard page
│   ├── discover/       # Discover decks page
│   ├── study/          # Study session page
│   ├── create/         # Card creation page
│   ├── layout.tsx      # Root layout
│   ├── page.tsx        # Home page
│   └── globals.css     # Global styles
├── public/             # Static assets
├── Dockerfile          # Docker configuration
└── package.json        # Dependencies
```

## Technology Stack

- **Next.js 15** with App Router and Turbopack
- **React 19** for UI components
- **TypeScript 5** for type safety
- **Tailwind CSS 4** for styling

## Environment Variables

Create a `.env.local` file (see `.env.local.example`):

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

For production, update the API URL to your deployed backend.

## Available Scripts

- `npm run dev` - Start development server with Turbopack
- `npm run build` - Build for production with Turbopack
- `npm start` - Start production server

## Development

### Adding New Pages

Create a new directory under `app/` with a `page.tsx` file for new routes.

### Styling

Uses Tailwind CSS utility classes for styling. Global styles are in `app/globals.css`.

## Troubleshooting

**Port Already in Use:**
```bash
PORT=3001 npm run dev
```

**Module Errors:**
```bash
rm -rf node_modules .next
npm install
```

## Contributing

See [../CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines.

---

**Last Updated**: October 21, 2025
