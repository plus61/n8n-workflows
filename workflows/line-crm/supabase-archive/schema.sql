-- ============================================================================
-- LINE CRM - Supabase Schema Definition
-- ============================================================================
-- テーブル名: line_leads
-- 目的: LINE友だち追加イベントの記録
-- 作成日: 2025-10-25
-- アーカイブ日: 2025-10-26
-- ============================================================================

-- ============================================================================
-- 1. テーブル作成
-- ============================================================================

CREATE TABLE IF NOT EXISTS line_leads (
  -- 主キー
  id BIGSERIAL PRIMARY KEY,
  
  -- ビジネスキー（n8n実行ID + タイムスタンプ）
  lead_id VARCHAR(255) NOT NULL UNIQUE 
    COMMENT 'n8n実行ID + タイムスタンプのユニークキー',
  
  -- LINE情報
  user_id VARCHAR(255) NOT NULL 
    COMMENT 'LINE ユーザーID',
  display_name VARCHAR(255) NOT NULL DEFAULT '' 
    COMMENT 'LINE表示名（後から取得）',
  picture_url TEXT NOT NULL DEFAULT '' 
    COMMENT 'LINEプロフィール画像URL（後から取得）',
  
  -- タイムスタンプ情報
  timestamp_jst TIMESTAMPTZ NOT NULL 
    COMMENT 'イベント発生時刻（JST）',
  processed_at TIMESTAMPTZ NOT NULL 
    COMMENT 'n8n処理時刻（JST）',
  
  -- メタデータ
  source VARCHAR(50) NOT NULL DEFAULT 'webhook' 
    COMMENT 'データソース: webhook, manual, import等',
  status VARCHAR(50) NOT NULL DEFAULT 'pending' 
    COMMENT 'ステータス: pending, processed, error等',
  
  -- システムカラム
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  deleted_at TIMESTAMPTZ NULL 
    COMMENT '論理削除用タイムスタンプ'
);

-- ============================================================================
-- 2. インデックス作成
-- ============================================================================

-- ユーザーIDでの高速検索
CREATE INDEX idx_line_leads_user_id ON line_leads(user_id);

-- ステータスでのフィルタリング
CREATE INDEX idx_line_leads_status ON line_leads(status);

-- ソースでのフィルタリング
CREATE INDEX idx_line_leads_source ON line_leads(source);

-- タイムスタンプでのソート（最新順）
CREATE INDEX idx_line_leads_timestamp_jst ON line_leads(timestamp_jst DESC);

-- 論理削除フィルタリング
CREATE INDEX idx_line_leads_deleted_at ON line_leads(deleted_at) 
  WHERE deleted_at IS NULL;

-- 複合インデックス: status + timestamp_jst（ダッシュボード用）
CREATE INDEX idx_line_leads_status_timestamp ON line_leads(status, timestamp_jst DESC);

-- ============================================================================
-- 3. トリガー作成（updated_at自動更新）
-- ============================================================================

-- updated_atを自動更新する関数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- トリガーを設定
CREATE TRIGGER update_line_leads_updated_at 
  BEFORE UPDATE ON line_leads
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- 4. RLS（Row Level Security）ポリシー
-- ============================================================================

-- RLS有効化
ALTER TABLE line_leads ENABLE ROW LEVEL SECURITY;

-- n8nサービスロール用ポリシー（全アクセス許可）
CREATE POLICY "n8n_service_role_all_access" ON line_leads
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- 認証ユーザー用ポリシー（読み取り専用）
CREATE POLICY "authenticated_users_read_only" ON line_leads
  FOR SELECT
  TO authenticated
  USING (deleted_at IS NULL);

-- 管理者用ポリシー（全アクセス）
CREATE POLICY "admin_users_all_access" ON line_leads
  FOR ALL
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM profiles
      WHERE profiles.id = auth.uid()
      AND profiles.is_admin = true
    )
  );

-- ============================================================================
-- 5. コメント追加
-- ============================================================================

COMMENT ON TABLE line_leads IS 'LINE友だち追加イベントの記録テーブル';
COMMENT ON COLUMN line_leads.id IS '主キー（自動採番）';
COMMENT ON COLUMN line_leads.lead_id IS 'n8n実行ID + タイムスタンプのユニークキー';
COMMENT ON COLUMN line_leads.user_id IS 'LINE ユーザーID';
COMMENT ON COLUMN line_leads.display_name IS 'LINE表示名（後から取得）';
COMMENT ON COLUMN line_leads.picture_url IS 'LINEプロフィール画像URL（後から取得）';
COMMENT ON COLUMN line_leads.timestamp_jst IS 'イベント発生時刻（JST）';
COMMENT ON COLUMN line_leads.processed_at IS 'n8n処理時刻（JST）';
COMMENT ON COLUMN line_leads.source IS 'データソース: webhook, manual, import等';
COMMENT ON COLUMN line_leads.status IS 'ステータス: pending, processed, error等';
COMMENT ON COLUMN line_leads.created_at IS 'レコード作成日時';
COMMENT ON COLUMN line_leads.updated_at IS 'レコード更新日時（自動更新）';
COMMENT ON COLUMN line_leads.deleted_at IS '論理削除用タイムスタンプ';

-- ============================================================================
-- 6. サンプルデータ挿入（オプション）
-- ============================================================================

-- テスト用データ
-- INSERT INTO line_leads (lead_id, user_id, timestamp_jst, processed_at)
-- VALUES 
--   ('test-001-1729875600000', 'U1234567890abcdef1234567890abcdef1', NOW(), NOW()),
--   ('test-002-1729875700000', 'U1234567890abcdef1234567890abcdef2', NOW(), NOW());

-- ============================================================================
-- 完了
-- ============================================================================

