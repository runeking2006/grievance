## Grievance Frontend

Production-style frontend for the grievance backend.

### Setup

Create a `.env.local` file in `frontend/`:

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

The app also falls back to `VITE_API_BASE_URL` if that variable is provided.

### Run

```bash
npm install
npm run dev
```

Open `http://localhost:3000`.

### Features

- JWT + API-key based sign in flow
- Live complaint submission
- Async job polling
- User-owned complaint history
- Admin dashboard metrics
- Analytics charts
- Health and metrics observability
