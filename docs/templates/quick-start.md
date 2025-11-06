# n8n Template Library - Quick Start Guide

**5-minute guide to finding and using n8n community templates**

---

## 🎯 Common Use Cases

### Use Case 1: "I need AI video generation"

```bash
# 1. Search templates
node scripts/find-template.js "AI video generation"

# 2. Results show:
#    - ID 3553: YouTube Shorts Automation
#    - ID 4630: Full video pipeline with ElevenLabs
#    - ID 5910: Instagram Reels with Veo3

# 3. Get details in Claude Code
mcp__n8n-mcp__get_template({ templateId: 3553, mode: "structure" })
```

**Expected Output**: 10+ relevant templates with descriptions

---

### Use Case 2: "Show me all AI video templates"

```bash
# Browse by category
node scripts/find-template.js --category ai-video

# View category details
cat templates/ai-video/metadata.json
```

**Expected Output**: Full category listing with use cases and credentials

---

### Use Case 3: "Find templates using OpenAI"

```bash
# Search by node type (in Claude Code)
mcp__n8n-mcp__list_node_templates({
  nodeTypes: ["@n8n/n8n-nodes-langchain.lmChatOpenAi"],
  limit: 15
})
```

**Expected Output**: Templates using OpenAI ChatGPT nodes

---

### Use Case 4: "I want to add voice to my video workflow"

```bash
# 1. Search voice synthesis
node scripts/find-template.js "voice synthesis ElevenLabs"

# 2. Find template 3553 or 4630

# 3. Extract voice generation nodes
# (Use Claude Code with get_template)

# 4. Test in experiments/
mkdir experiments/2025-11-05-voice-test

# 5. Integrate into wf7
```

---

## 📚 Command Cheat Sheet

### Search Commands

```bash
# Text search
node scripts/find-template.js "your query"

# Category browse
node scripts/find-template.js --category ai-video

# Interactive mode
node scripts/find-template.js --interactive

# List categories
node scripts/find-template.js --list-categories
```

### MCP Commands (Claude Code)

```javascript
// Search by keyword
mcp__n8n-mcp__search_templates({
  query: "video automation",
  limit: 10
})

// Get template details
mcp__n8n-mcp__get_template({
  templateId: 3553,
  mode: "structure"  // or "full"
})

// Find by node type
mcp__n8n-mcp__list_node_templates({
  nodeTypes: ["n8n-nodes-base.youTube"],
  limit: 10
})

// Search nodes
mcp__n8n-mcp__search_nodes({
  query: "video",
  includeExamples: true
})
```

---

## 🔍 Search Strategy

### 1. Start Broad
```bash
node scripts/find-template.js "video"
# → Too many results (100+)
```

### 2. Add Specificity
```bash
node scripts/find-template.js "AI video automation"
# → Better (20-30 results)
```

### 3. Filter by Category
```bash
node scripts/find-template.js --category ai-video
# → Focused (10 results in category)
```

### 4. Search by Service
```bash
node scripts/find-template.js "YouTube Shorts"
# → Specific (5-10 results)
```

---

## 🎬 Example: Integrating ElevenLabs Voice

**Goal**: Add AI voice narration to wf7

### Step-by-Step

```bash
# 1. Find voice templates
node scripts/find-template.js "ElevenLabs voice"

# 2. Identify template 3553 (YouTube Shorts with ElevenLabs)

# 3. View structure in Claude Code
```

```javascript
// In Claude Code
const template = await mcp__n8n-mcp__get_template({
  templateId: 3553,
  mode: "structure"
});

// Look for httpRequest nodes calling api.elevenlabs.io
```

```bash
# 4. Create test environment
mkdir experiments/2025-11-05-elevenlabs-test

# 5. Extract key configuration
```

**Key Node Configuration** (from template):
```json
{
  "name": "ElevenLabs TTS",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "url": "https://api.elevenlabs.io/v1/text-to-speech/{{voiceId}}",
    "method": "POST",
    "authentication": "headerAuth",
    "sendHeaders": true,
    "headerParameters": {
      "parameters": [
        { "name": "xi-api-key", "value": "={{$credentials.apiKey}}" }
      ]
    },
    "sendBody": true,
    "bodyParametersJson": "={{ { \"text\": $json.narration, \"model_id\": \"eleven_multilingual_v2\" } }}",
    "options": {
      "response": {
        "response": {
          "responseFormat": "file"
        }
      }
    }
  }
}
```

```bash
# 6. Test in experiments/

# 7. Integrate into wf7 Phase3
# (Update workflows/wf7-video-renderer/phase3-narration.json)

# 8. Document in wf7 README
```

---

## 💡 Pro Tips

### 1. Use Template Metadata
```bash
# Check what credentials you'll need
cat templates/ai-video/metadata.json | jq '.requiredCredentials'
```

### 2. Node Usage Patterns
```bash
# See most common nodes in category
cat templates/00-index.json | jq '.statistics.topNodes'
```

### 3. Integration Points
```bash
# Check wf7 integration suggestions
cat templates/ai-video/metadata.json | jq '.integrationPoints.["wf7-video-renderer"]'
```

### 4. Experiments Directory
```bash
# Always test in experiments first
mkdir experiments/$(date +%Y-%m-%d)-template-test
cd experiments/$(date +%Y-%m-%d)-template-test
# Test here, then move to production
```

---

## 🚨 Common Issues

### "No templates found"
- **Solution**: Broaden search query or use category browsing

### "Template too complex"
- **Solution**: Extract specific nodes, don't copy entire workflow

### "Credentials missing"
- **Solution**: Check `templates/<category>/metadata.json` for requirements

### "Index outdated"
- **Solution**: Run `node scripts/build-template-index.js`

---

## 📖 Next Steps

1. **Explore Categories**: `node scripts/find-template.js --list-categories`
2. **Read Full Docs**: `docs/templates/README.md`
3. **Integration Patterns**: `docs/templates/usage-patterns.md` (coming soon)
4. **wf7 Integration**: Start with templates 3553, 2976, or 4630

---

**Quick Help**:
- Search: `node scripts/find-template.js "query"`
- Browse: `node scripts/find-template.js --category <name>`
- Interactive: `node scripts/find-template.js --interactive`
