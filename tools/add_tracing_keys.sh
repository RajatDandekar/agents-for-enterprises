#!/bin/zsh
# Saves the LangSmith and Sentry keys for Lecture 6 into the course .env (which git ignores).
# Each key is typed here, hidden, and never printed. Press Enter on a prompt to skip that key.
ENV_FILE="$(cd "$(dirname "$0")/.." && pwd)/.env"
touch "$ENV_FILE"

save() {  # save NAME VALUE: replace the line if the name is already there, else add it
  local name="$1" value="$2"
  [[ -z "$value" ]] && { echo "  $name: skipped"; return; }
  grep -v "^${name}=" "$ENV_FILE" > "$ENV_FILE.tmp"
  printf '%s=%s\n' "$name" "$value" >> "$ENV_FILE.tmp"
  mv "$ENV_FILE.tmp" "$ENV_FILE"
  echo "  $name: saved"
}

read -rs "A?LangSmith API key (Settings > API keys, starts with lsv2_): "; echo
save LANGSMITH_API_KEY "$A"
read -r  "B?LangSmith region, us or eu [us]: "
[[ "$B" == "eu" ]] && save LANGSMITH_ENDPOINT "https://eu.api.smith.langchain.com" || save LANGSMITH_ENDPOINT "https://api.smith.langchain.com"
read -rs "C?Sentry DSN (Project settings > Client keys, starts with https://): "; echo
save SENTRY_DSN "$C"
read -rs "D?Sentry auth token, optional, to read traces back (Settings > Auth tokens): "; echo
save SENTRY_AUTH_TOKEN "$D"
read -r  "E?Sentry organisation slug, optional (the name in your Sentry URL): "
save SENTRY_ORG "$E"
unset A B C D E
echo "Done. Tell Claude the keys are in."
