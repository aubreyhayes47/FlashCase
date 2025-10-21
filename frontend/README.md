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

## API Integration

The frontend is configured to connect to the backend API at `http://localhost:8000/api/v1` by default. Update `NEXT_PUBLIC_API_URL` in `.env.local` to change this.
