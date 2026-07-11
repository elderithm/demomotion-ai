# Authenticated recordings

To demo a page that requires login, capture a browser session once and reuse it.
DemoMotion never handles your credentials — you log in yourself.

```bash
make auth-capture URL=https://your-app.example.com
```

A real browser window opens. Log in, then press Enter. The session is saved to
`auth/state.json`, which docker-compose mounts into the API and the recorder
picks up automatically (via `DEMOMOTION_AUTH_STATE`).

`auth/state.json` contains session cookies — it is gitignored; never commit it.
