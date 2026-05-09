# AI Setup Guide

OCO uses vision AI to automatically identify items from photos. Three providers are supported.

## Choosing a Provider

| Provider | Cost | Privacy | Quality | Setup |
|---|---|---|---|---|
| **Ollama** (default) | Free | Local | Good | Requires GPU/CPU with RAM |
| **Claude** (Anthropic) | Pay-per-use | Cloud | Excellent | API key only |
| **Mistral** | Pay-per-use | Cloud | Good | API key only |

**Recommendation:** Start with Ollama for privacy and zero cost. Switch to Claude for best quality.

---

## Ollama (Local AI)

Ollama runs the AI model locally on your machine. No data leaves your network.

### Requirements

- 8 GB RAM minimum for `llava-llama3` (16 GB recommended)
- A GPU speeds up processing significantly but is not required

### Setup

1. Install Ollama: https://ollama.ai/download

2. Pull the recommended vision model:
   ```bash
   ollama pull llava-llama3
   ```

3. Configure `.env`:
   ```bash
   AI_PROVIDER=ollama
   OLLAMA_URL=http://localhost:11434
   OLLAMA_MODEL=llava-llama3
   ```

4. If running Ollama in Docker alongside OCO, use the service name:
   ```bash
   OLLAMA_URL=http://ollama:11434
   ```

### Alternative Models

Any Ollama model with vision support works. Other good options:

| Model | Size | Notes |
|---|---|---|
| `llava-llama3` | ~5 GB | Best balance (default) |
| `llava:13b` | ~8 GB | Better quality, slower |
| `llava:7b` | ~4 GB | Faster, slightly lower quality |
| `moondream` | ~2 GB | Very fast, lower quality |

### Verify Ollama is Working

```bash
# Test Ollama directly
curl http://localhost:11434/api/tags

# Test via OCO admin panel
# Admin → AI Config → Test Connection
```

---

## Claude (Anthropic)

Claude claude-sonnet-4-6 is used for image analysis. Excellent quality, requires internet.

### Setup

1. Create an account at https://console.anthropic.com
2. Generate an API key
3. Configure `.env`:
   ```bash
   AI_PROVIDER=claude
   CLAUDE_API_KEY=sk-ant-...
   ```

Or set the API key via the admin panel without restarting:  
**Admin → AI Config → Claude section → enter key → Save**

### Cost

Approximately $0.003–0.01 per item analyzed, depending on photo size.

---

## Mistral

Mistral's vision models provide a good quality/cost balance.

### Setup

1. Create an account at https://console.mistral.ai
2. Generate an API key
3. Configure `.env`:
   ```bash
   AI_PROVIDER=mistral
   MISTRAL_API_KEY=...
   ```

---

## Switching Providers at Runtime

No restart needed. Use the admin panel:

1. Go to **Admin → AI Config**
2. Select the provider
3. Enter/update credentials if needed
4. Click **Save**
5. Click **Test Connection** to verify

---

## AI Analysis Quality Tips

- **Good lighting** — the most impactful factor
- **Single object** — one item per photo works best
- **Hint type** — select "Book" for books, "Set" for grouped items, "Auto" for everything else
- **Manual name** — entering a name hint improves accuracy significantly

## Troubleshooting

**Worker not processing items:**
- Check `podman-compose logs backend` for errors
- Verify AI provider is reachable (Admin → AI Config → Test Connection)
- Items in `draft_ai_failed` status can be retried individually

**Ollama slow:**
- Ensure you have enough RAM
- First request after startup is slow (model loading) — subsequent requests are faster
- Consider a smaller model (`moondream`) for faster processing
