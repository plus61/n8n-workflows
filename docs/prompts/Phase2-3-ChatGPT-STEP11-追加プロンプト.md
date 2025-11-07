# Phase 2-3 ChatGPT プロンプト STEP11 追加

**目的**: FAL.ai Image-to-Video用の動きプロンプト生成
**追加先**: 既存のPhase 2-3 ChatGPTプロンプトの最後に追加
**バージョン**: 1.0

---

## STEP11: 動きのプロンプト生成

あなたはこれから、各セクションの動画に適した「動きのプロンプト」を生成します。

### 各セクションの目的と推奨される動き

#### 1. フック（3秒）

**目的**: 視聴者の注意を一瞬で引く

**推奨される動き**: ズームイン、ドラマチックな登場

**プロンプト例**:
```
dramatic zoom in effect, professional business style, sharp focus
```

**キーワード**:
- dramatic, impactful, attention-grabbing
- zoom in, quick reveal
- professional, business style
- sharp focus, high contrast

---

#### 2. 導入（10秒）

**目的**: 視聴者の悩みに共感し、動画の価値を示す

**推奨される動き**: スムーズなスライド、落ち着いたトーン

**プロンプト例**:
```
smooth slide transition, calm professional tone, steady camera
```

**キーワード**:
- smooth, gentle, flowing
- slide transition, steady movement
- calm, professional, reassuring
- clear, focused

---

#### 3. 本編（13秒×3）

**目的**: 3つの要点を明確に伝える

**推奨される動き**: フェードイン、軽いズーム、教育的な雰囲気

**プロンプト例**:
```
gentle fade in with subtle zoom, educational style, clean motion
```

**キーワード**:
- gentle, subtle, gradual
- fade in, soft zoom
- educational, informative
- clean, organized, clear

---

#### 4. まとめ（20秒）

**目的**: 得られる未来を描き、信頼感を与える

**推奨される動き**: シネマティックなパン、インスピレーショナル

**プロンプト例**:
```
cinematic pan effect, inspiring tone, smooth movement
```

**キーワード**:
- cinematic, elegant, polished
- pan effect, sweeping motion
- inspiring, uplifting, motivational
- smooth, fluid, professional

---

#### 5. CTA（7秒）

**目的**: 行動を促す

**推奨される動き**: パルス効果、緊急感、注目を引く

**プロンプト例**:
```
pulsing call-to-action, urgent professional, attention-grabbing
```

**キーワード**:
- pulsing, rhythmic, dynamic
- call-to-action, urgent
- attention-grabbing, compelling
- professional, trustworthy

---

## 出力形式

上記のガイドラインに基づき、今回の動画内容に最適な「動きのプロンプト」を**JSON形式**で生成してください。

### JSON構造

```json
{
  "hook": "dramatic zoom in effect, professional business style, sharp focus",
  "intro": "smooth slide transition, calm professional tone, steady camera",
  "point1": "gentle fade in with subtle zoom, educational style, clean motion",
  "point2": "gentle fade in with subtle zoom, educational style, clean motion",
  "point3": "gentle fade in with subtle zoom, educational style, clean motion",
  "summary": "cinematic pan effect, inspiring tone, smooth movement",
  "cta": "pulsing call-to-action, urgent professional, attention-grabbing"
}
```

### 重要な注意事項

1. **英語で記述**: FAL.ai APIは英語プロンプトを使用
2. **簡潔に**: 各プロンプトは10-15単語程度
3. **動画内容に合わせる**: 動画のトーンに応じて調整
4. **一貫性**: 全体の流れが自然になるように

---

## 具体例

### 例1: LINE登録誘導動画（ビジネス系）

**動画トーン**: プロフェッショナル、信頼感、緊急性

```json
{
  "hook": "dramatic zoom with professional impact, sharp business focus, attention-grabbing",
  "intro": "smooth corporate slide, calm confident tone, steady professional camera",
  "point1": "clean fade in with subtle corporate zoom, business educational style",
  "point2": "gentle business transition, clear informative motion, professional focus",
  "point3": "confident fade with strategic emphasis, clear business messaging",
  "summary": "cinematic corporate pan, inspiring professional future, smooth elevation",
  "cta": "urgent professional pulse, compelling call-to-action, trustworthy emphasis"
}
```

### 例2: MEO集客動画（地域ビジネス）

**動画トーン**: 親しみやすい、地域密着、実用的

```json
{
  "hook": "friendly zoom in, warm local business style, inviting focus",
  "intro": "smooth welcoming slide, approachable tone, steady friendly camera",
  "point1": "gentle reveal with practical zoom, helpful local style, clear guidance",
  "point2": "warm transition with community feel, practical informative motion",
  "point3": "friendly fade with local emphasis, clear neighborhood messaging",
  "summary": "warm community pan, inspiring local success, smooth growth",
  "cta": "friendly urgent pulse, warm call-to-action, local trust emphasis"
}
```

### 例3: 教育系動画（スキルアップ）

**動画トーン**: 知的、成長志向、励まし

```json
{
  "hook": "smart zoom in, intellectual style, focused learning emphasis",
  "intro": "smooth educational slide, encouraging tone, steady teaching camera",
  "point1": "gentle knowledge reveal, educational clarity, progressive learning",
  "point2": "smart fade with skill emphasis, clear instructional motion",
  "point3": "confident learning transition, clear growth messaging",
  "summary": "cinematic achievement pan, inspiring success journey, smooth progression",
  "cta": "motivating pulse, encouraging call-to-action, growth-focused emphasis"
}
```

---

## デフォルト値

もし動画のトーンが不明な場合は、以下のデフォルト値を使用してください：

```json
{
  "hook": "dramatic zoom in effect, professional business style, sharp focus",
  "intro": "smooth slide transition, calm professional tone, steady camera",
  "point1": "gentle fade in with subtle zoom, educational style, clean motion",
  "point2": "gentle fade in with subtle zoom, educational style, clean motion",
  "point3": "gentle fade in with subtle zoom, educational style, clean motion",
  "summary": "cinematic pan effect, inspiring tone, smooth movement",
  "cta": "pulsing call-to-action, urgent professional, attention-grabbing"
}
```

---

## 追加の視覚要素設定

動きプロンプトと併せて、以下のJSON構造も生成してください：

### Duration Config（秒数設定）

```json
{
  "hook": 3,
  "intro": 10,
  "point1": 13,
  "point2": 13,
  "point3": 14,
  "summary": 20,
  "cta": 7,
  "total": 80
}
```

### Visual Elements（視覚要素）

```json
{
  "hook": {
    "icon": "⚠️",
    "position": "top-center",
    "size": "large"
  },
  "intro": {
    "icon": "📊",
    "position": "bottom-right"
  },
  "point1": {
    "icon": "🎯",
    "emphasis": "bold"
  },
  "point2": {
    "icon": "💡",
    "emphasis": "bold"
  },
  "point3": {
    "icon": "✅",
    "checkmark": true
  },
  "summary": {
    "icon": "🚀",
    "position": "center"
  },
  "cta": {
    "icon": "👉",
    "position": "center",
    "size": "large"
  }
}
```

### Brand Colors（ブランドカラー）

```json
{
  "background": "#1a1a2e",
  "primary_text": "#ffffff",
  "secondary_text": "#aaaaaa",
  "accent": "#00d4ff",
  "cta_bg": "#ff6b6b",
  "cta_text": "#ffffff"
}
```

---

## Notion DBへの保存

生成したJSONは以下のNotion DBプロパティに保存されます：

- **Motion Prompts**: 動きプロンプトのJSON
- **Duration Config**: 秒数設定のJSON
- **Visual Elements**: 視覚要素のJSON
- **Brand Colors**: ブランドカラーのJSON

---

**作成**: Claude Code (Sonnet 4.5)
**バージョン**: 1.0
**更新日**: 2025-11-06
