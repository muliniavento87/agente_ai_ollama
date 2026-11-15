#!/bin/bash
set -e

# Directory di configurazione di Pi Agent (default: /etc/.pi/agent)
CONFIG_DIR="${PI_CODING_AGENT_DIR:-/etc/.pi/agent}"

# - Inizializzazione auth.json
cat << 'EOF' > "$CONFIG_DIR/auth.json"
{
    "ollama": {
        "type": "api_key",
        "key": "ollama"
    },
    "edge0": {
        "type": "api_key",
        "key": "edge0"
    }
}
EOF

# - Inizializzazione mcp.json
cat << 'EOF' > "$CONFIG_DIR/mcp.json"
{
    "settings": {
        "directTools": true
    },
    "mcpServers": {
        "miei-tool-python": {
            "command": "/server_mcp/venv/bin/python",
            "args": ["/server_mcp/server.py"]
        }
    }
}
EOF

# - Inizializzazione models.json
cat << 'EOF' > "$CONFIG_DIR/models.json"
{
    "providers": {
        "ollama": {
            "old": "http://192.168.1.173:11434/v1",
            "baseUrl": "http://host.docker.internal:11434/v1",
            "api": "openai-completions",
            "apiKey": "ollama",
            "models": [
                {
                    "id": "Qwen3.6-35B-A3B-Q4-K-M-32k",
                    "contextWindow": 32768,
                    "maxTokens": 32768,
                    "input": ["text", "image"]
                },
                {
                    "id": "lfm2.5-32k",
                    "contextWindow": 32768,
                    "maxTokens": 32768
                },
                {
                    "id": "Saluki-27b-IQ2-32k",
                    "contextWindow": 32768,
                    "maxTokens": 32768
                },
                {
                    "old": "8192-32768",
                    "id": "Ornith-1.5-9b-Q4-K-M-32k",
                    "contextWindow": 32768,
                    "maxTokens": 32768
                },
                {
                    "id": "Ornith-1.5-9b-IQ3-M-8k",
                    "contextWindow": 8192,
                    "maxTokens": 8192
                }
            ]
        },
        "edge0": {
            "baseUrl": "http://host.docker.internal:8080/v1",
            "api": "openai-completions",
            "apiKey": "edge0",
            "models": [
                {
                    "id": "edge0-35b",
                    "contextWindow": 32768,
                    "maxTokens": 32768,
                    "input": ["text"]
                }
            ]
        },
        "freetoken": {
            "baseUrl": "http://192.168.1.173:1919/v1",
            "api": "openai-completions",
            "apiKey": "freetoken",
            "models": [
                {
                    "id": "Qwen3.6-35B-A3B-NVFP4",
                    "contextWindow": 32768,
                    "maxTokens": 32768,
                    "input": ["text", "image"]
                }
            ]
        }
    }
}
EOF

# - Inizializzazione sandbox.json
cat << 'EOF' > "$CONFIG_DIR/sandbox.json"
{
    "enabled": true,
    "allowRead": ["."],
    "allowWrite": ["."],
    "allowDelete": ["."],
    "permissionPromptTimeoutSeconds": 1,
    "OLDdenyWrite": [],
    "OLDenableWeakerNestedSandbox": true
}
EOF

# - Inizializzazione settings.json
cat << 'EOF' > "$CONFIG_DIR/settings.json"
{
    "OLDdefaultModel": "Ornith-1.5-9b-Q4-K-M-32k",
    "OLDdefaultProvider": "ollama",
    "defaultModel": "edge0-35b",
    "defaultProvider": "edge0",
    "httpIdleTimeoutMs": 0,
    "compaction": {
        "enabled": false
    },
    "extensions": [
        "-builtin:mcp"
    ],
    "lastChangelogVersion": "1.5.2"
}
EOF

# - Imposta i permessi corretti per l'utente "agent_user" per poter scrivere in "/etc/.pi/agent"
chown -R agent_user:agent_user "$CONFIG_DIR"
chmod -R 755 "$CONFIG_DIR"
