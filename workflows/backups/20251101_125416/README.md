# n8n Workflow Backup - 2025-11-01 12:54:16

## Backup Summary

**Total Active Workflows**: 14
**Backup Date**: 2025-11-01 12:54:16 JST
**Backup Location**: `/Users/yuichiroooosuger/Desktop/n8n-workflows/workflows/backups/20251101_125416/`

## Workflow List

### WF7 Video Generation Pipeline (5 workflows)
1. **WF7_Phase1_SNS動画台本整形.json**
   - ID: fqbULAMXIGyBkNtL
   - Webhook: wf7-test-webhook
   - Nodes: 10
   - Purpose: GPT-4 script generation and formatting

2. **WF7_Phase2_素材取得.json**
   - ID: sGjN9Vqw4pGTLmaX
   - Webhook: wf7-phase2-assets
   - Nodes: 15
   - Purpose: Pexels/Unsplash asset retrieval

3. **WF7_Phase3_音声・字幕生成.json**
   - ID: KkiF386PmAVaY1mA
   - Webhook: wf7-phase3-audio
   - Nodes: 12
   - Purpose: OpenAI TTS and SRT subtitle generation

4. **WF7_Phase4_動画レンダリング.json** ⚡ CRITICAL
   - ID: VF3kFwJLKVq990jn
   - Webhook: wf7-phase4-render
   - Nodes: 12
   - Purpose: Python video rendering execution
   - Last Updated: 2025-11-01T01:41:28.209Z

5. **WF7_Phase5_メタデータ登録・連携.json**
   - ID: 0CK4yaBsipa1UgSz
   - Webhook: wf7-phase5-metadata
   - Nodes: 11
   - Purpose: Notion metadata updates

### Content Generation Workflows (3 workflows)
6. **WF4_note_Article_Detection_System.json**
   - ID: RffNVk7h3Q6aEfY0
   - Schedule: RSS monitoring
   - Nodes: 10

7. **WF5_トピック抽出AI.json**
   - ID: jhhxhXABBwXxQ1GJ
   - Schedule: 0 9 * * 3,6 (Wed/Sat 9am)
   - Nodes: 11
   - Purpose: GPT-4 trend analysis

8. **Phase2_WF6_note記事自動生成.json**
   - ID: tkmG4YSZyi5RLiPw
   - Schedule: 0 10 * * * (Daily 10am)
   - Nodes: 10
   - Purpose: GPT-4 article generation

### LINE Integration Workflows (3 workflows)
9. **LINE_Lead_Pipeline_Notion.json**
   - ID: cmp1aRcobG9TYpAu
   - Webhook: line-lead-notion
   - Nodes: 13
   - Purpose: Rich menu postback handling

10. **LINE_Rich_Menu_Integration.json**
    - ID: Blu10Nw42Tklenjs
    - Nodes: 9
    - Purpose: Postback data parsing

11. **LINE_Step_Delivery_System.json**
    - ID: TllqY0y6xAGQvyyD
    - Nodes: 12
    - Purpose: Step-based message delivery

### Test & Utility Workflows (3 workflows)
12. **Conditional_Logic_Test.json**
    - ID: NgXgJuKJp15edOK4
    - Webhook: conditional-test
    - Purpose: Conditional logic testing

13. **Simple_Webhook_Test_Auto_Active.json**
    - ID: h7AOOMtgwrMwMpiB
    - Webhook: test-webhook
    - Nodes: 3
    - Purpose: Basic webhook testing

14. **Advanced_Data_Processing_Pipeline.json**
    - ID: 06eepVXbFwzHVP3L
    - Webhook: advanced-pipeline
    - Nodes: 8
    - Purpose: Validation and transformation

## Important Notes

- All workflows are currently **ACTIVE** in n8n
- Webhook-based workflows may require UI re-save after container restart (known n8n limitation)
- File Server workflows (6 total) were updated with node-level `onError: "continueRegularOutput"` on 2025-11-01
- WF7 Phase4 is critical for video rendering pipeline testing

## Next Steps

1. File Server Webhook疎通テスト
2. Phase4 E2Eテスト実行
