#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<USAGE
Usage:
  run_add_project.sh --name NAME --token TOKEN [options]

Required:
  --name NAME               Project name (agent/account id)
  --token TOKEN             Telegram bot token from BotFather

Optional:
  --description TEXT        Project short description
  --server HOST             SSH server (default: ubuntu@VM-16-15-ubuntu)
  --soul-file PATH          Custom SOUL.md file path
  --agents-file PATH        Custom AGENTS.md file path
  --repo-dir PATH           openclaw-server-config directory
  --dry-run                 Only patch local files, skip git push and deploy
  -h, --help                Show this help

Env:
  OPENCLAW_SERVER_CONFIG_REPO   Fallback repo dir (default: ~/openclaw-server-config)
USAGE
}

name=""
token=""
description=""
server="ubuntu@VM-16-15-ubuntu"
soul_file=""
agents_file=""
dry_run=0
repo_dir="${OPENCLAW_SERVER_CONFIG_REPO:-$HOME/openclaw-server-config}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --name)
      name="$2"
      shift 2
      ;;
    --token)
      token="$2"
      shift 2
      ;;
    --description)
      description="$2"
      shift 2
      ;;
    --server)
      server="$2"
      shift 2
      ;;
    --soul-file)
      soul_file="$2"
      shift 2
      ;;
    --agents-file)
      agents_file="$2"
      shift 2
      ;;
    --repo-dir)
      repo_dir="$2"
      shift 2
      ;;
    --dry-run)
      dry_run=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [[ -z "$name" || -z "$token" ]]; then
  echo "Error: --name and --token are required." >&2
  usage >&2
  exit 1
fi

script_path="$repo_dir/scripts/add-project.py"
if [[ ! -f "$script_path" ]]; then
  echo "Error: add-project.py not found at: $script_path" >&2
  echo "Hint: pass --repo-dir or set OPENCLAW_SERVER_CONFIG_REPO" >&2
  exit 1
fi

cmd=(python3 "$script_path" --name "$name" --token "$token" --description "$description" --server "$server")

if [[ -n "$soul_file" ]]; then
  cmd+=(--soul-file "$soul_file")
fi

if [[ -n "$agents_file" ]]; then
  cmd+=(--agents-file "$agents_file")
fi

if [[ "$dry_run" -eq 1 ]]; then
  cmd+=(--dry-run)
fi

"${cmd[@]}"
