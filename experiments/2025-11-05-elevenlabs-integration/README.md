# ElevenLabs TTS Integration Experiment

**Date**: 2025-11-05
**Source Template**: 3553 - AI-Powered YouTube Shorts Automation
**Target Workflow**: wf7 Phase3 (Narration Generation)
**Status**: In Progress

---

## Objective

Extract and test ElevenLabs TTS implementation from template 3553 for integration into wf7's Phase3 narration generation workflow.

## Source Analysis

### Template 3553 Overview
- **Name**: AI-Powered YouTube Shorts Automation: Create & Publish with OpenAI & ElevenLabs
- **Node Count**: 75 nodes
- **Complexity**: Complex
- **Views**: 5,428
- **Key Technologies**: OpenAI, ElevenLabs, YouTube API, Cloudinary

### Key Node: "Convert Script to Audio"
- **Node ID**: 3582171f-da82-4b59-b99e-b08185b282e7
- **Node Type**: `n8n-nodes-base.httpRequest` (v4.2)
- **Position**: After "Script" node, before "Chunk Script" and "Upload to Cloudinary"

### Workflow Flow (Relevant Section)
```
Script Node
  ↓
Convert Script to Audio (ElevenLabs TTS)
  ↓
Chunk Script (Text Processing)
  ↓
Upload to Cloudinary (Asset Storage)
```

---

## ElevenLabs TTS Implementation Pattern

Based on template 3553 analysis and n8n HTTP Request node v4.2 patterns:

### API Configuration

**Endpoint Pattern**:
```
https://api.elevenlabs.io/v1/text-to-speech/{voiceId}
```

**HTTP Method**: `POST`

**Authentication**:
- Type: Header-based API key
- Header: `xi-api-key: {ELEVENLABS_API_KEY}`

**Request Body** (JSON):
```json
{
  "text": "{{$json.script}}",
  "model_id": "eleven_multilingual_v2",
  "voice_settings": {
    "stability": 0.5,
    "similarity_boost": 0.75
  }
}
```

**Response Handling**:
- Format: Binary audio file (MP3)
- Response mode: `file`
- Store as binary data for downstream processing

### n8n Node Configuration (v4.2)

**Key Parameters**:
```javascript
{
  "method": "POST",
  "url": "=https://api.elevenlabs.io/v1/text-to-speech/{{$parameter.voiceId}}",
  "authentication": "genericCredentialType",
  "genericAuthType": "httpHeaderAuth",
  "sendHeaders": true,
  "headerParameters": {
    "parameters": [
      {
        "name": "xi-api-key",
        "value": "={{$credentials.elevenlabsApi.apiKey}}"
      }
    ]
  },
  "sendBody": true,
  "specifyBody": "json",
  "jsonBody": "={{ {\"text\": $json.script, \"model_id\": \"eleven_multilingual_v2\"} }}",
  "options": {
    "response": {
      "response": {
        "responseFormat": "file",
        "outputPropertyName": "audioData"
      }
    }
  }
}
```

**Important n8n v4.2 Requirements**:
- ⚠️ **MUST** use `specifyBody: "json"` when using expressions (`={{ }}`)
- ⚠️ Use `jsonBody` parameter (NOT `bodyParametersJson`)
- ⚠️ Response format `"file"` for binary audio data

---

## wf7 Phase3 Current Implementation

### Current Approach
- **Provider**: ElevenLabs API (primary) / OpenAI TTS API (alternative)
- **Cost**: $0.01-0.05 per video
- **Node Type**: HTTP Request nodes with API calls
- **Location**: `workflows/wf7-video-renderer/phase3-narration.json`

### Integration Opportunities

#### 1. **Voice Model Upgrade**
- Current: Basic TTS configuration
- Template 3553: `eleven_multilingual_v2` model with voice settings
- **Benefit**: Better voice quality, multilingual support

#### 2. **Voice Settings Control**
- Template includes:
  - `stability`: 0.5 (voice consistency)
  - `similarity_boost`: 0.75 (voice character preservation)
- **Benefit**: Fine-tuned voice output control

#### 3. **Error Handling Pattern**
- Template likely includes retry logic and error handling
- **Benefit**: More robust production implementation

#### 4. **Response Processing**
- Binary file handling with proper output naming
- **Benefit**: Clean data flow to Phase4 (FFmpeg)

---

## Testing Plan

### Phase 1: Isolated Component Test
1. Create standalone n8n workflow with extracted ElevenLabs node
2. Test with sample script input: `"これはテストです。ElevenLabsの音声合成をテストしています。"`
3. Verify audio file generation and quality
4. Validate binary data output format

### Phase 2: Integration Test
1. Compare output format with wf7 Phase3 requirements
2. Test data flow compatibility with Phase4 FFmpeg renderer
3. Measure performance and cost vs. current implementation
4. Document any required adaptations

### Phase 3: Production Validation
1. Run side-by-side comparison with existing wf7 Phase3
2. Quality assessment (voice clarity, pronunciation accuracy)
3. Performance benchmarking (generation time, reliability)
4. Cost analysis (API usage, token consumption)

---

## Expected Outcomes

### Success Criteria
- ✅ Audio file successfully generated from text input
- ✅ Output compatible with wf7 Phase4 FFmpeg input requirements
- ✅ Voice quality equal to or better than current implementation
- ✅ Generation time ≤ current implementation (within 10%)
- ✅ Cost per video unchanged or reduced

### Integration Recommendations
Based on test results:
- Full replacement vs. fallback option
- Configuration parameters to expose
- Error handling strategies
- Monitoring and alerting requirements

---

## Required Credentials

### ElevenLabs API
- **Type**: API Key
- **Obtain**: https://elevenlabs.io/app/settings/api-keys
- **Environment Variable**: `ELEVENLABS_API_KEY`
- **n8n Credential Name**: `elevenlabsApi`

### Voice IDs
Popular voices from ElevenLabs:
- `21m00Tcm4TlvDq8ikWAM` - Rachel (American Female)
- `AZnzlk1XvdvUeBnXmlld` - Domi (American Female)
- `EXAVITQu4vr4xnSDxMaL` - Bella (American Female)
- `ErXwobaYiN019PkySvjV` - Antoni (American Male)
- `MF3mGyEYCl7XYWbV9V6O` - Elli (American Female)
- `TxGEqnHWrfWFTfGW9XjX` - Josh (American Male)
- `VR6AewLTigWG4xSOukaG` - Arnold (American Male)
- `pNInz6obpgDQGcFmaJgB` - Adam (American Male)
- `yoZ06aMxZJJ28mfd3POQ` - Sam (American Male)

---

## Next Steps

1. ✅ Create experiment directory
2. ✅ Document ElevenLabs TTS pattern
3. ⏳ Create test workflow JSON
4. ⏳ Execute isolated test
5. ⏳ Compare with wf7 Phase3
6. ⏳ Document integration recommendation

---

## References

- Template Source: [n8n Community Template 3553](https://n8n.io/workflows/3553)
- ElevenLabs API Docs: https://docs.elevenlabs.io/api-reference/text-to-speech
- n8n HTTP Request Node: https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.httprequest/
- wf7 Design Doc: `/docs/wf7-hybrid-veo3-design.md`
