# n8n Template Library

**Version**: 1.0.0
**Last Updated**: 2025-11-05
**Total Templates Indexed**: 10 (AI Video category)

## 📚 Overview

This template library provides a structured catalog of 399+ community n8n workflows, organized by category and searchable through CLI tools. Templates serve as:

- **🔍 Reference**: Learn workflow patterns and best practices
- **🧩 Components**: Extract reusable node configurations
- **🚀 Rapid Prototyping**: Bootstrap new workflows quickly
- **💡 Inspiration**: Discover solutions to common automation challenges

---

## 📁 Directory Structure

```
templates/
├── 00-index.json                    # Master template catalog
├── ai-video/                        # AI video automation templates
│   └── metadata.json
├── content-creation/                # Content generation workflows
│   └── metadata.json
├── data-processing/                 # ETL and data transformation
│   └── metadata.json
├── social-media/                    # Social media automation
│   └── metadata.json
└── business-automation/             # Business process workflows
    └── metadata.json
```

---

## 🎯 Categories

### 🎬 AI Video Automation (10 templates)
**Description**: AI-powered video generation, editing, and publishing workflows

**Popular Templates**:
- **ID 3553**: AI-Powered YouTube Shorts Automation (OpenAI + ElevenLabs)
- **ID 2976**: Automatically Create YouTube Metadata with AI
- **ID 5910**: Auto-Generate and Post Instagram Reels (Veo3 + Blotato)
- **ID 4630**: Generate Videos with AI, ElevenLabs & Post to YouTube

**Common Nodes**:
- `@n8n/n8n-nodes-langchain.lmChatOpenAi` - AI script generation
- `n8n-nodes-base.httpRequest` - API integrations (ElevenLabs, Runway, etc.)
- `n8n-nodes-base.youTube` - Video publishing
- `n8n-nodes-base.googleDrive` - Asset storage

**Use Cases**:
- YouTube Shorts/Reels automation
- AI-powered video metadata generation
- Text-to-video generation with AI avatars
- Music video creation with Suno AI

**Integration with wf7**:
- Extract OpenAI script generation patterns
- Integrate ElevenLabs voice synthesis
- Adopt video assembly workflows
- Learn metadata optimization techniques

---

### ✍️ Content Creation (Coming Soon)
Blog posts, SEO optimization, social media content

### 🔄 Data Processing (Coming Soon)
ETL pipelines, API synchronization, data transformation

### 📱 Social Media (Coming Soon)
Scheduling, cross-platform posting, engagement automation

### 💼 Business Automation (Coming Soon)
CRM integration, sales pipelines, customer notifications

---

## 🚀 Quick Start

### 1. Search Templates

```bash
# Search by keyword
node scripts/find-template.js "video automation"

# Browse category
node scripts/find-template.js --category ai-video

# Interactive search
node scripts/find-template.js --interactive

# List all categories
node scripts/find-template.js --list-categories
```

### 2. View Template Details

```bash
# Get full template information (requires n8n MCP)
# In Claude Code:
mcp__n8n-mcp__get_template({
  templateId: 3553,
  mode: "structure"  # or "full" for complete workflow
})
```

### 3. Integration Workflow

```bash
# 1. Search for relevant templates
node scripts/find-template.js "AI voice synthesis"

# 2. Review template structure
# (Use MCP get_template in Claude Code)

# 3. Create experiment branch
mkdir experiments/2025-11-05-elevenlabs-integration

# 4. Test integration in isolated environment

# 5. Extract successful components into production workflow
```

---

## 🔗 Integration Patterns

### Pattern 1: Component Extraction
**Use Case**: Extract reusable node configurations

```javascript
// Example: Extract ElevenLabs TTS from template 3553
{
  "name": "ElevenLabs TTS",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "url": "https://api.elevenlabs.io/v1/text-to-speech/{{voiceId}}",
    "method": "POST",
    "authentication": "headerAuth",
    "bodyParametersJson": {
      "text": "={{$json.script}}",
      "model_id": "eleven_multilingual_v2"
    }
  }
}
```

### Pattern 2: Workflow Inspiration
**Use Case**: Learn architectural patterns for similar problems

```
Template 4630 Pattern:
[Schedule] → [AI Script] → [Voice Gen] → [Image Gen] →
[Video Assembly] → [YouTube Upload] → [Notification]

Applicable to: wf7, wf8, any video automation workflow
```

### Pattern 3: API Integration Reference
**Use Case**: Learn how to integrate specific services

**Top APIs in AI Video Templates**:
- OpenAI GPT-4 (script generation)
- ElevenLabs (voice synthesis)
- Runway ML (video generation)
- Creatomate (video assembly)
- Google Drive (asset management)
- YouTube API (publishing)

---

## 📊 Statistics

### Top 10 Nodes in AI Video Templates

| Node | Uses | Purpose |
|------|------|---------|
| `n8n-nodes-base.httpRequest` | 10 | API integrations |
| `n8n-nodes-base.stickyNote` | 10 | Documentation |
| `n8n-nodes-base.wait` | 9 | Async operations |
| `@n8n/n8n-nodes-langchain.lmChatOpenAi` | 7 | AI generation |
| `@n8n/n8n-nodes-langchain.agent` | 7 | AI orchestration |
| `n8n-nodes-base.set` | 7 | Data transformation |
| `n8n-nodes-base.googleDrive` | 7 | File storage |
| `@n8n/n8n-nodes-langchain.openAi` | 6 | AI completion |
| `n8n-nodes-base.googleSheets` | 6 | Data tracking |
| `n8n-nodes-base.youTube` | 2 | Video publishing |

---

## 💡 Best Practices

### Template Usage Guidelines

1. **🔍 Research First**: Search templates before building from scratch
2. **📝 Document Learnings**: Note useful patterns in project docs
3. **🧪 Test Safely**: Use `/experiments` for template testing
4. **🎯 Extract Components**: Don't copy entire workflows, extract patterns
5. **📚 Contribute Back**: Document successful integrations

### wf7 Integration Strategy

**Current wf7 Workflow**: Phase1 Script → Phase2 Assets → Phase3 Narration → Phase4 FFmpeg Render

**Template Enhancement Opportunities**:

1. **Phase1 Enhancement** (Template 3553)
   - Add AI-powered script optimization
   - Integrate SEO keyword generation
   - Enhance script structure with proven patterns

2. **Phase3 Enhancement** (Template 4630)
   - Explore ElevenLabs advanced voice models
   - Add voice cloning capabilities
   - Implement multi-language narration

3. **Phase2 Alternative** (Template 5910)
   - AI image generation with DALL-E/Midjourney
   - Dynamic asset selection algorithms
   - Advanced Google Drive integration

4. **Metadata Generation** (Template 2976)
   - Post-render metadata optimization
   - YouTube SEO enhancements
   - Automated thumbnail generation

---

## 🛠️ CLI Tools Reference

### find-template.js
**Purpose**: Search and discover templates

```bash
# Search
node scripts/find-template.js "query"

# Category browse
node scripts/find-template.js --category ai-video

# Interactive
node scripts/find-template.js --interactive
```

### build-template-index.js
**Purpose**: Rebuild template catalog

```bash
# Refresh index (updates 00-index.json)
node scripts/build-template-index.js
```

---

## 📖 Related Documentation

- [n8n Workflow Construction Knowledge](../knowledge/n8n-workflow-construction-knowledge.md)
- [wf7 Phase4 Troubleshooting Guide](../knowledge/wf7-phase4-troubleshooting-guide.md)
- [n8n Skills Integration](../n8n-skills-integration.md)

---

## 🔄 Maintenance

**Update Frequency**: Monthly or when adding new workflow categories

**Update Process**:
1. Run `node scripts/build-template-index.js`
2. Review new templates in `00-index.json`
3. Update category metadata files
4. Document integration patterns in this README

---

## 🤝 Contributing

Found a useful template integration pattern? Document it:

1. Add entry to relevant category metadata
2. Create integration example in `/experiments`
3. Update this README with pattern details
4. Share learnings in project docs

---

**Last Index Rebuild**: 2025-11-05
**Templates Tracked**: 10 (AI Video)
**Categories Active**: 1/5
