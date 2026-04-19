#!/usr/bin/env bash
set -e

echo "==> Instalando dependencias Python..."
uv venv --python 3.12 2>/dev/null || true
uv pip install -r requirements.txt

echo ""
echo "==> Instalando gstack (skills para Claude Code)..."
if [ -d "$HOME/.claude/skills/gstack" ]; then
  echo "    gstack ya existe, actualizando..."
  git -C "$HOME/.claude/skills/gstack" pull --ff-only
else
  git clone --single-branch --depth 1 https://github.com/garrytan/gstack.git "$HOME/.claude/skills/gstack"
fi

# Asegurarse de que bun está disponible
export PATH="$HOME/.bun/bin:$PATH"
if ! command -v bun &>/dev/null; then
  echo "    Instalando bun..."
  BUN_VERSION="1.3.10"
  tmpfile=$(mktemp)
  curl -fsSL "https://bun.sh/install" -o "$tmpfile"
  BUN_VERSION="$BUN_VERSION" bash "$tmpfile"
  rm "$tmpfile"
  export PATH="$HOME/.bun/bin:$PATH"
fi

cd "$HOME/.claude/skills/gstack" && ./setup
cd - > /dev/null

echo ""
echo "==> Configurando .env..."
if [ ! -f .env ]; then
  cp .env.example .env 2>/dev/null || cat > .env << 'EOF'
COOKIDOO_EMAIL=tu@email.com
COOKIDOO_PASSWORD=tupassword
COOKIDOO_COUNTRY=es
COOKIDOO_LANGUAGE=es-ES
COOKIDOO_DEVICE=TM6
EOF
  echo "    .env creado — edítalo con tus credenciales de Cookidoo."
else
  echo "    .env ya existe, no se sobreescribe."
fi

echo ""
echo "==> Listo. Próximos pasos:"
echo "    1. Edita .env con tus credenciales de Cookidoo"
echo "    2. Añade el MCP server a Claude Desktop (ver README.md)"
echo "    3. Reinicia Claude Desktop"
echo "    4. Prueba con /receta en Claude Desktop o Claude Code"
