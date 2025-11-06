# ElevenLabs TTS Integration Guide for wf7 Phase3

**Version**: 1.0
**Date**: 2025-11-05
**Target**: wf7 Phase3 Narration Generation
**Source**: Template 3553 Analysis

---

## Executive Summary

This guide provides step-by-step instructions for integrating the ElevenLabs TTS implementation pattern from template 3553 into wf7's Phase3 narration generation workflow.

**Key Benefits**:
- ✅ Improved voice quality with `eleven_multilingual_v2` model
- ✅ Fine-tuned voice control (stability, similarity_boost)
- ✅ Multilingual support for Japanese narration
- ✅ Production-ready error handling pattern
- ✅ Compatible with existing wf7 Phase4 FFmpeg renderer

**Estimated Integration Time**: 2-3 hours (including testing)

---

## Prerequisites

### 1. ElevenLabs API Credentials

**Setup Steps**:
1. Sign up at https://elevenlabs.io/
2. Navigate to Settings → API Keys
3. Generate new API key
4. Store securely (never commit to Git)

**n8n Credential Configuration**:
```yaml
Credential Type: "HTTP Header Auth"
Name: "ElevenLabs API"
Header Name: "xi-api-key"
Value: {YOUR_ELEVENLABS_API_KEY}
```

### 2. Voice ID Selection

**Recommended Voices for Japanese Content**:
- Test multiple voices to find best match for your content style
- Popular multilingual voices:
  - `21m00Tcm4TlvDq8ikWAM` - Rachel (clear, professional)
  - `EXAVITQu4vr4xnSDxMaL` - Bella (friendly, engaging)
  - `pNInz6obpgDQGcFmaJgB` - Adam (deep, authoritative)

**Testing Voice Quality**:
```bash
# Use the test workflow to compare voices
node scripts/find-template.js "voice synthesis"
```

### 3. Current wf7 Phase3 Location

**File**: `workflows/wf7-video-renderer/phase3-narration.json`

**Current Implementation**:
- Provider: ElevenLabs API (basic configuration)
- Model: Default TTS model
- Voice Settings: Not configured
- Cost: $0.01-0.05 per video

---

## Integration Steps

### Step 1: Backup Current Phase3 Workflow

```bash
# Create backup with timestamp
cp workflows/wf7-video-renderer/phase3-narration.json \
   workflows/backups/verified/phase3-narration_$(date +%Y%m%d_%H%M%S).json
```

### Step 2: Update HTTP Request Node Configuration

**Location**: Phase3 narration.json → "Generate Narration" node

**Key Changes**:

#### A. Update Request URL
```javascript
// Before:
"url": "https://api.elevenlabs.io/v1/text-to-speech/{{voiceId}}"

// After:
"url": "=https://api.elevenlabs.io/v1/text-to-speech/{{ $json.voiceId }}"
```

#### B. Update Body Configuration (CRITICAL)
```javascript
// Before:
"sendBody": true,
"bodyParametersJson": "={{ {...} }}"  // ❌ Old format

// After:
"sendBody": true,
"specifyBody": "json",  // ⚠️ REQUIRED for n8n v4.2+
"jsonBody": "={{ { \"text\": $json.script, \"model_id\": \"eleven_multilingual_v2\", \"voice_settings\": { \"stability\": 0.5, \"similarity_boost\": 0.75 } } }}"
```

**⚠️ CRITICAL n8n v4.2+ Requirement**: Must use `specifyBody: "json"` when using expressions (`={{ }}`). See `/docs/knowledge/n8n-workflow-construction-knowledge.md` line 156.

#### C. Add Voice Settings
```json
{
  "voice_settings": {
    "stability": 0.5,
    "similarity_boost": 0.75
  }
}
```

**Parameter Explanation**:
- `stability` (0.0-1.0): Voice consistency across generation
  - Lower (0.3-0.5): More expressive, varied intonation
  - Higher (0.7-0.9): More stable, consistent delivery
- `similarity_boost` (0.0-1.0): Voice character preservation
  - Lower (0.3-0.5): More creative, may drift from original
  - Higher (0.7-0.9): Closer to original voice characteristics

#### D. Update Response Handling
```javascript
"options": {
  "response": {
    "response": {
      "responseFormat": "file",  // Binary audio data
      "outputPropertyName": "audioData"  // Store as audioData
    }
  }
}
```

### Step 3: Update Model to Multilingual v2

**Model**: `eleven_multilingual_v2`

**Benefits**:
- Superior Japanese pronunciation accuracy
- Natural intonation and prosody
- Consistent quality across languages
- Better handling of technical terms

**Cost**: Same as standard model ($0.30 per 1,000 characters)

### Step 4: Add Error Handling (Optional but Recommended)

Add an "IF" node after "Generate Narration" to handle API failures:

```json
{
  "name": "Check Audio Generation",
  "type": "n8n-nodes-base.if",
  "parameters": {
    "conditions": {
      "string": [
        {
          "value1": "={{ $json.audioData }}",
          "operation": "isNotEmpty"
        }
      ]
    }
  }
}
```

**Fallback Options**:
1. Retry with different voice ID
2. Fall back to OpenAI TTS
3. Send error notification
4. Queue for manual review

### Step 5: Verify Data Flow Compatibility

**Phase3 Output → Phase4 Input**:
- Format: Binary audio file (MP3)
- Property: `audioData` or binary attachment
- Size: Typically 50-500 KB per narration
- Duration: Matches script length

**Validation**:
```javascript
// Add validation node before Phase4
{
  "name": "Validate Audio Output",
  "type": "n8n-nodes-base.set",
  "parameters": {
    "assignments": {
      "assignments": [
        {
          "name": "hasAudio",
          "value": "={{ !!$binary.data }}",
          "type": "boolean"
        },
        {
          "name": "audioSize",
          "value": "={{ $binary.data ? $binary.data.fileSize : 0 }}",
          "type": "number"
        }
      ]
    }
  }
}
```

---

## Testing Protocol

### Phase 1: Isolated Testing

**Use Test Workflow**:
```bash
# Import test workflow into n8n
cat experiments/2025-11-05-elevenlabs-integration/elevenlabs-tts-test.json
```

**Test Cases**:
1. ✅ Short script (1-2 sentences) - Basic functionality
2. ✅ Medium script (3-5 sentences) - Quality assessment
3. ✅ Long script (10+ sentences) - Performance validation
4. ✅ Japanese text with technical terms - Pronunciation accuracy
5. ✅ Mixed Japanese/English - Multilingual handling

**Success Criteria**:
- Audio file generated successfully
- File size > 0 KB
- Playback works correctly
- Voice quality acceptable
- Generation time < 10 seconds

### Phase 2: Integration Testing

**Steps**:
1. Run complete wf7 workflow with updated Phase3
2. Verify Phase4 FFmpeg receives correct audio input
3. Check final video quality (audio/video sync)
4. Validate cost per video (should be unchanged)

**Comparison Metrics**:
| Metric | Current | New (Template 3553) | Target |
|--------|---------|---------------------|--------|
| Voice Quality | Good | Excellent | ≥ Current |
| Generation Time | ~5s | ~5-7s | ≤ +20% |
| Audio Size | ~100KB | ~100-150KB | ≤ 200KB |
| Cost per Video | $0.02 | $0.02 | ≤ Current |

### Phase 3: Production Validation

**Rollout Strategy**:
1. Deploy to test environment first
2. Run 10-20 test videos
3. Manual quality review
4. Monitor for errors (24-48 hours)
5. Gradual production rollout

**Monitoring**:
- ElevenLabs API response times
- Audio generation success rate (target: ≥99%)
- Cost per video tracking
- User feedback on voice quality

---

## Rollback Plan

### Quick Rollback
```bash
# Restore backup immediately
cp workflows/backups/verified/phase3-narration_YYYYMMDD_HHMMSS.json \
   workflows/wf7-video-renderer/phase3-narration.json

# Restart n8n workflow
# Test with sample script
```

### Gradual Rollback
1. Switch voice model back to default
2. Remove voice_settings parameters
3. Revert body configuration to old format
4. Monitor for stability

---

## Troubleshooting

### Issue 1: "Invalid request body" Error

**Cause**: Missing `specifyBody: "json"` parameter
**Fix**: Add `"specifyBody": "json"` to HTTP Request node
**Reference**: n8n-workflow-construction-knowledge.md:156

### Issue 2: Empty Audio Data

**Cause**: Incorrect response format configuration
**Fix**: Ensure `responseFormat: "file"` is set
**Validation**: Check `$json.audioData` exists

### Issue 3: Poor Voice Quality

**Cause**: Suboptimal voice_settings values
**Fix**: Adjust stability and similarity_boost
**Recommended**: stability=0.5, similarity_boost=0.75

### Issue 4: High API Costs

**Cause**: Excessive retries or long scripts
**Fix**:
- Implement caching for repeated scripts
- Limit script length to 500 characters
- Monitor API usage dashboard

### Issue 5: Slow Generation Times

**Cause**: Large script size or API latency
**Fix**:
- Split long scripts into chunks
- Implement parallel processing
- Use shorter sentences

---

## Cost Analysis

### Current Cost Structure
- ElevenLabs: $0.30 per 1,000 characters
- Average script: 50-150 characters
- Cost per video: $0.01-0.05

### Expected Cost Impact
- Model upgrade: No additional cost
- Voice settings: No additional cost
- Multilingual support: No additional cost
- **Net Impact**: $0.00 (unchanged)

### Cost Optimization Tips
1. Cache generated audio for repeated scripts
2. Batch similar scripts together
3. Use script compression techniques
4. Monitor usage with ElevenLabs dashboard

---

## Performance Benchmarks

### Expected Performance (Template 3553 Pattern)

| Metric | Value | Notes |
|--------|-------|-------|
| Generation Time | 3-7s | Depends on script length |
| Audio Quality | 320 kbps | High quality MP3 |
| Pronunciation Accuracy | ≥95% | For Japanese content |
| API Reliability | 99.5% | ElevenLabs SLA |
| Concurrent Requests | 5-10 | Adjust based on plan |

### Optimization Opportunities

1. **Parallel Processing**: Generate audio for multiple scripts simultaneously
2. **Caching**: Store generated audio for repeated scripts
3. **Preloading**: Generate common phrases in advance
4. **Fallback**: Implement OpenAI TTS as backup

---

## Next Steps

### Immediate Actions
1. ✅ Review this integration guide
2. ⏳ Set up ElevenLabs API credentials in n8n
3. ⏳ Test voice quality with test workflow
4. ⏳ Backup current Phase3 configuration
5. ⏳ Implement changes to Phase3 workflow

### Short-term (This Week)
1. Complete integration testing
2. Run side-by-side comparison
3. Collect quality metrics
4. Document findings
5. Plan production rollout

### Long-term (This Month)
1. Monitor production performance
2. Gather user feedback
3. Optimize voice settings based on data
4. Explore additional ElevenLabs features (voice cloning, etc.)
5. Document lessons learned

---

## References

- **Source Template**: Template 3553 Analysis
- **Target Workflow**: wf7 Phase3 (workflows/wf7-video-renderer/phase3-narration.json)
- **Knowledge Base**: /docs/knowledge/n8n-workflow-construction-knowledge.md
- **ElevenLabs API Docs**: https://docs.elevenlabs.io/api-reference/text-to-speech
- **n8n HTTP Request Node**: https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.httprequest/

---

## Support

**Questions or Issues?**
1. Check troubleshooting section above
2. Review n8n workflow construction knowledge base
3. Consult ElevenLabs API documentation
4. Test with provided test workflow first

**Success Indicators**:
- ✅ Audio files generating successfully
- ✅ Voice quality meets or exceeds current standard
- ✅ Phase4 FFmpeg processing without errors
- ✅ No cost increase per video
- ✅ Generation time within acceptable range

---

**Document Version**: 1.0
**Last Updated**: 2025-11-05
**Status**: Ready for Implementation
