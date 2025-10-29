# Agent Bletchley Frontend

Next.js 16 frontend application for the Agent Bletchley research system.

## Setup

### Prerequisites

- Node.js 18 or higher
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Configure environment variables:
```bash
cp .env.local.example .env.local
# Edit .env.local with your configuration
```

### Required Environment Variables

- `NEXT_PUBLIC_BACKEND_URL` - Backend API URL (default: http://localhost:8000)
- `NEXT_PUBLIC_WS_URL` - WebSocket URL (default: ws://localhost:8000)
- `NEXT_PUBLIC_SUPABASE_URL` - Your Supabase project URL
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` - Your Supabase anon key

### Running the Development Server

```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

### Building for Production

```bash
npm run build
npm start
```

### Project Structure

```
frontend/
├── app/                    # Next.js App Router pages
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Home page
│   ├── research/          # Research dashboard pages
│   └── api/               # API routes
├── components/            # React components
├── lib/                   # Utility libraries
├── types/                 # TypeScript type definitions
├── package.json           # Dependencies
└── README.md              # This file
```

### Features

- **Next.js 16 App Router** - Modern routing and server components
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first CSS with dark mode support
- **Framer Motion** - Animations and transitions
- **Supabase** - Database integration
- **WebSocket** - Real-time updates for research jobs

### Development

The codebase uses:
- TypeScript strict mode
- App Router (not Pages Router)
- Tailwind CSS with dark mode
- Proper error boundaries
- TypeScript interfaces for all props

