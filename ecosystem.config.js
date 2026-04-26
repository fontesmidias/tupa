// PM2 ecosystem (ADR-004). 3 processos: web, worker (Dramatiq), daemon IMAP.
// Comandos: `pm2 start ecosystem.config.js`, `pm2 logs gv-web`, `pm2 delete ecosystem.config.js`.
module.exports = {
  apps: [
    {
      name: "gv-web",
      cwd: __dirname,
      script: "uv",
      args: "run python manage.py runserver 3005",
      watch: ["apps", "config"],
      ignore_watch: ["**/__pycache__/**", "**/*.pyc", ".venv", "media", "staticfiles"],
      env: { DJANGO_SETTINGS_MODULE: "config.settings.dev" },
      autorestart: true,
    },
    {
      name: "gv-worker",
      cwd: __dirname,
      script: "uv",
      args: "run python -m dramatiq config.dramatiq --processes 1 --threads 4",
      env: { DJANGO_SETTINGS_MODULE: "config.settings.dev" },
      autorestart: true,
    },
    {
      name: "gv-email-ingestion",
      cwd: __dirname,
      script: "uv",
      args: "run python manage.py run_email_daemon",
      env: { DJANGO_SETTINGS_MODULE: "config.settings.dev" },
      autorestart: true,
      // Daemon real chega na Story 7.2a; placeholder apenas loga e dorme.
    },
  ],
};
