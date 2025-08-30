# PassCheck React UI

## Configure API
Create `.env` in this folder:
```
VITE_API_BASE=https://YOUR-RENDER-BACKEND.onrender.com
```

## Run
```
npm install
npm run dev
```

## Build
```
npm run build
```
Deploy the `dist/` folder (Netlify/Vercel).

## Notes
- Top bar centered brand "PassCheck".
- Personal Info collapsible card above "Pass Check".
- Generate section is stacked vertically.
- Analyze will POST personal info to the backend. Crack SSE will pass them via query when "Use personal info" is checked.
