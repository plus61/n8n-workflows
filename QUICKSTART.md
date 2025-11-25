# 🚀 Quick Start Guide
## Get Started with 3-MCP n8n Workflow Development in 15 Minutes

## 📋 Prerequisites

Before starting, ensure you have:
- ✅ Cursor IDE installed
- ✅ n8n instance running (local or cloud)
- ✅ Node.js 16+ installed
- ✅ n8n MCP servers configured in Cursor
  - `n8n-mcp` (Research)
  - `n8n-workflows` (Validation)
  - `n8n API` (Execution)

---

## ⚡ 5-Minute Setup

### Step 1: Clone Project Structure (1 min)

```bash
# Option A: Start fresh
cd /path/to/your/projects
cp -r /path/to/n8n-workflows-project ./my-n8n-project
cd my-n8n-project

# Option B: Initialize in existing directory
cd /path/to/existing/project
mkdir -p .cursor/rules workflows/{development,production} scripts docs
```

### Step 2: Configure Cursor Rules (1 min)

The `.cursor/rules/` directory contains two essential files:
- `n8n-workflow-design.mdc` - Workflow design best practices
- `n8n-mcp-usage.mdc` - MCP orchestration guidelines

**These files are automatically loaded by Cursor!**

Verify they're loaded:
1. Open Cursor
2. Start a chat with Claude
3. Ask: "What are the n8n workflow design rules?"
4. Claude should reference the rules from `.cursor/rules/`

### Step 3: Verify MCP Connection (1 min)

In Cursor, ask Claude:
```
Can you search for n8n nodes related to webhooks?
```

If MCPs are configured correctly, Claude will use:
- `search_nodes({ query: "webhook" })`
- Return a list of webhook-related nodes

### Step 4: Configure Environment (2 min)

Create `.env` file:
```bash
# n8n Instance Configuration
N8N_API_URL=https://your-n8n-instance.com
N8N_API_KEY=your_api_key_here

# Project Configuration
PROJECT_NAME=my-n8n-project
DEFAULT_TIMEZONE=Asia/Tokyo
```

**For local n8n:**
```bash
N8N_API_URL=http://localhost:5678
N8N_API_KEY=n8n_api_xxxxxxxxxxxxx
```

---

## 🎯 Your First Workflow in 10 Minutes

### Scenario: Simple Webhook Processor

We'll create a workflow that:
1. Receives data via webhook
2. Processes the data
3. Returns a response

### Phase 0: Pre-Validation (2 min)

**In Cursor, ask Claude:**
```
I want to create a webhook workflow that receives JSON data and processes it.
Expected data size: ~1KB per request
Expected volume: 100 requests/day
Can you help me assess the risk and architecture?
```

**Claude will:**
1. Calculate data size (1KB × 100 = 100KB/day)
2. Assess risk level (LOW - simple workflow OK)
3. Recommend simple architecture
4. Search for webhook templates

**Expected Phase 0 result:**
```typescript
{
  riskLevel: "LOW",
  architecture: "simple",
  estimatedTime: "30 minutes"
}
```

### Phase 1: Design (3 min)

**Ask Claude:**
```
Can you show me examples of webhook node configuration 
and help me design a simple webhook→process→response workflow?
```

**Claude will:**
1. Search: `search_nodes({ query: "webhook" })`
2. Get examples: `get_node_essentials({ nodeType: "nodes-base.webhook", includeExamples: true })`
3. Provide workflow structure

**You'll get:**
```json
{
  "name": "Simple Webhook Processor",
  "nodes": [
    {
      "id": "webhook",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "my-webhook",
        "responseMode": "lastNode"
      }
    },
    {
      "id": "process",
      "type": "n8n-nodes-base.code",
      "parameters": {
        "jsCode": "return { json: { processed: true, data: $json } };"
      }
    }
  ],
  "connections": {
    "webhook": { "main": [[{ "node": "process" }]] }
  }
}
```

### Phase 2: Validate (2 min)

**Ask Claude:**
```
Please validate this workflow before deployment.
```

**Claude will:**
1. Run: `validate_workflow({ workflow: workflowJson })`
2. Check nodes, connections, expressions
3. Report any issues

**Expected output:**
```
✅ Validation passed
- Workflow structure: Valid
- Node configurations: Valid
- Connections: Valid
- No errors or warnings
```

### Phase 3: Deploy (2 min)

**Ask Claude:**
```
Deploy this workflow to my n8n instance.
```

**Claude will:**
1. Use n8n API: `n8n_create_workflow({ ... })`
2. Return deployment details

**You'll get:**
```
✅ Workflow deployed successfully
   ID: workflow_abc123
   Webhook URL: https://your-n8n.com/webhook/my-webhook
   Status: Inactive
```

### Phase 4: Test (1 min)

**Test the webhook:**
```bash
curl -X POST https://your-n8n.com/webhook/my-webhook \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

**Check execution:**
```
Can you show me the last execution result for this workflow?
```

**Claude will:**
```typescript
n8n_get_execution({ 
  id: "latest",
  mode: "preview" 
})
```

---

## 🎓 Learning Path

### Week 1: Master the Basics
**Day 1-2: Understand Phase 0**
- Read: `/docs/phase0-validation-framework.md`
- Practice: Assess 3 different workflow scenarios
- Goal: Accurately predict risk levels

**Day 3-4: Learn n8n-mcp (Research)**
- Practice: `search_nodes()` for different use cases
- Practice: `get_node_essentials()` with examples
- Practice: `search_templates()` and analyze structures

**Day 5-7: Learn n8n-workflows (Validation)**
- Practice: `validate_workflow()` on sample workflows
- Practice: Fix validation errors
- Practice: Use `n8n_autofix_workflow()`

### Week 2: Real Workflows
**Build 5 Complete Workflows:**
1. **Email automation** (3 hours)
2. **Data sync** (2 hours)
3. **Webhook processor** (2 hours)
4. **Scheduled task** (2 hours)
5. **Multi-step process** (4 hours)

For each workflow:
1. Complete Phase 0 (15-30 min)
2. Design with validation (30-60 min)
3. Deploy and test (30 min)
4. Document (15 min)

### Week 3: Advanced Patterns
- Sub-workflow architecture
- Binary data handling
- Error handling strategies
- Async processing patterns
- Performance optimization

### Week 4: Production Mastery
- Monitoring and alerting
- Version management
- Rollback procedures
- Backup strategies
- Team collaboration

---

## 📚 Essential Commands Reference

### Research (n8n-mcp)
```typescript
// Find nodes
search_nodes({ query: "keyword" })

// Get configuration examples
get_node_essentials({ 
  nodeType: "nodes-base.xxxx",
  includeExamples: true 
})

// Find proven solutions
search_templates({ query: "use case" })
```

### Validate (n8n-workflows)
```typescript
// Validate complete workflow
validate_workflow({ workflow: json })

// Validate single node
validate_node_operation({ 
  nodeType: "...",
  config: { ... }
})

// Auto-fix issues
n8n_autofix_workflow({ 
  id: "workflow_id",
  applyFixes: true 
})
```

### Deploy (n8n API)
```typescript
// Create workflow
n8n_create_workflow({ 
  name: "...",
  nodes: [ ... ],
  connections: { ... }
})

// Get execution
n8n_get_execution({ 
  id: "exec_id",
  mode: "preview"  // Start with preview!
})

// List workflows
n8n_list_workflows({ limit: 100 })
```

---

## 🛠️ Automation Scripts

### Validate All Workflows
```bash
node scripts/validate-all.js
node scripts/validate-all.js --profile=strict
node scripts/validate-all.js --autofix
```

### Deploy Workflow
```bash
node scripts/deploy.js workflows/development/my-workflow.json
node scripts/deploy.js my-workflow.json --env=prod --activate
```

### Backup Workflows
```bash
node scripts/backup.js --all
node scripts/backup.js --id=workflow_123
node scripts/backup.js --all --include-executions
```

---

## 🎯 Common Scenarios

### Scenario 1: "I have an idea, where do I start?"

**Ask Claude:**
```
I want to create a workflow that [describe your idea].
Can you help me with Phase 0 validation?
```

**Claude will guide you through:**
1. Data size estimation
2. Risk assessment
3. Architecture recommendation
4. Template search
5. MVP design

### Scenario 2: "My workflow isn't working"

**Ask Claude:**
```
My workflow ID is [workflow_id]. 
Can you check the latest execution and tell me what went wrong?
```

**Claude will:**
1. Get execution: `n8n_get_execution()`
2. Analyze error
3. Suggest fixes
4. Help implement solution

### Scenario 3: "I want to optimize my workflow"

**Ask Claude:**
```
Can you validate my workflow and suggest optimizations?
File: workflows/development/my-workflow.json
```

**Claude will:**
1. Validate workflow
2. Check for anti-patterns
3. Suggest improvements
4. Help refactor

---

## 🚨 Troubleshooting

### Problem: "MCPs not working in Cursor"

**Solution:**
1. Check Cursor settings for MCP servers
2. Restart Cursor
3. Ask Claude: "Can you run n8n_health_check()?"
4. If still failing, check server logs

### Problem: "Validation always fails"

**Solution:**
1. Start with lenient profile: `profile: "ai-friendly"`
2. Fix one error at a time
3. Use autofix: `n8n_autofix_workflow()`
4. Gradually move to `profile: "strict"`

### Problem: "Can't deploy to n8n"

**Solution:**
1. Check `.env` configuration
2. Verify n8n API key
3. Test connection: `n8n_health_check()`
4. Check n8n instance logs

---

## 💡 Pro Tips

### Tip 1: Always Use includeExamples
```typescript
// ❌ Without examples
get_node_essentials({ nodeType: "nodes-base.httpRequest" })

// ✅ With examples (much better!)
get_node_essentials({ 
  nodeType: "nodes-base.httpRequest",
  includeExamples: true 
})
```

### Tip 2: Start with Preview Mode
```typescript
// ❌ Getting too much data
n8n_get_execution({ id: "exec_id", mode: "full" })

// ✅ Start small
n8n_get_execution({ id: "exec_id", mode: "preview" })
```

### Tip 3: Use Templates as Learning Tools
```typescript
// Find similar workflows
search_templates({ query: "your use case" })

// Study the structure
get_template({ templateId: 123, mode: "structure" })

// Learn from proven solutions
```

### Tip 4: Validate Before Every Deploy
```typescript
// ALWAYS validate first
await validate_workflow({ workflow, options: { profile: "strict" } })

// Then deploy
await n8n_create_workflow(workflow)
```

---

## 🎓 Next Steps

1. **Complete Your First Workflow** (Today)
   - Follow the 10-minute guide above
   - Deploy to development
   - Test thoroughly

2. **Read Documentation** (This Week)
   - `/docs/phase0-validation-framework.md`
   - `/docs/3-mcp-integration-guide.md`
   - `/.cursor/rules/n8n-workflow-design.mdc`

3. **Build 5 Practice Workflows** (Next 2 Weeks)
   - Start simple
   - Gradually increase complexity
   - Learn from mistakes

4. **Master Advanced Patterns** (Month 2)
   - Sub-workflows
   - Binary data
   - Error handling
   - Async processing

5. **Go to Production** (Month 3)
   - Deploy real workflows
   - Monitor performance
   - Optimize continuously

---

## 📞 Getting Help

### In Cursor with Claude
Just ask! Examples:
- "Help me design a workflow for [use case]"
- "Why did my workflow fail?"
- "How do I handle binary data?"
- "What's the best practice for [scenario]?"

### Documentation
- Phase 0: `/docs/phase0-validation-framework.md`
- Integration: `/docs/3-mcp-integration-guide.md`
- Design Rules: `/.cursor/rules/n8n-workflow-design.mdc`
- MCP Usage: `/.cursor/rules/n8n-mcp-usage.mdc`

### Community
- n8n Community: https://community.n8n.io/
- n8n Documentation: https://docs.n8n.io/

---

## 🎉 Success Checklist

After completing this guide, you should be able to:
- [ ] Understand the 3-MCP architecture
- [ ] Complete Phase 0 validation
- [ ] Search for nodes and templates
- [ ] Validate workflows before deployment
- [ ] Deploy workflows to n8n
- [ ] Monitor and debug executions
- [ ] Use automation scripts
- [ ] Apply best practices

---

## 🚀 Remember

**The Golden Rule:**
```
Research (n8n-mcp)
   ↓
Validate (n8n-workflows)
   ↓
Deploy (n8n API)
   ↓
Monitor (n8n API)
```

**30 minutes of Phase 0 saves 140 hours of debugging!**

---

*Last updated: 2025-11-15*
*Version: 1.0*

**Ready to start? Open Cursor and say:**
```
Hi Claude! I want to create my first n8n workflow.
Can you guide me through Phase 0 validation?
```

🚀 **Happy workflow building!**
