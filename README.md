# Instagram レシピ抽出ツール

Instagramのレシピ投稿から材料・手順を自動抽出して保存するツールです。

## セットアップ

### 1. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定

`.env.example` を `.env` にコピーして、必要な情報を設定してください。

```bash
cp .env.example .env
```

`.env` ファイルを編集：

```
# AI API Keys (どちらか一方でOK)
ANTHROPIC_API_KEY=your_anthropic_api_key_here
# または
OPENAI_API_KEY=your_openai_api_key_here

# Instagram認証情報（サブアカウント推奨）
INSTAGRAM_USERNAME=your_instagram_username
INSTAGRAM_PASSWORD=your_instagram_password
```

### 3. サブアカウントの作成（推奨）

メインアカウントのBAN防止のため、テスト用のサブアカウント作成を強く推奨します。

## 使い方

### メインツールの起動

```bash
python main.py
```

### コマンド

- Instagram URLを入力: レシピを抽出して保存
- `list`: 保存済みレシピ一覧を表示
- `search キーワード`: レシピを検索
- `quit`: 終了

### 個別テスト

各モジュールを個別にテストできます：

```bash
# AI解析のテスト（サンプルデータ使用）
python ai_parser.py

# Instagram取得のテスト
python instagram_scraper.py
```

## 注意事項

### 垢BAN対策

1. **サブアカウントを使用**してください
2. **レート制限を守る**: 1リクエストごとに30秒以上の間隔
3. **1日の取得数を制限**: 10-20件程度に抑える
4. **深夜の大量取得は避ける**

### 規約について

- 個人利用の範囲に留めてください
- 商用利用は避けてください
- Instagram側の仕様変更でツールが動作しなくなる可能性があります

## トラブルシューティング

### ログインエラー

- 2段階認証を無効にしてください（サブアカで）
- パスワードに特殊文字が含まれる場合は `.env` で適切にエスケープ

### レート制限エラー

- 待機時間を長くしてください（60秒以上）
- 1日の取得数を減らしてください

### AI解析エラー

- APIキーが正しく設定されているか確認
- API利用制限に達していないか確認

## 次のステップ

- [ ] 買い物リスト生成機能
- [ ] Webインターフェース（PWA化）
- [ ] YouTube、TikTok対応
- [ ] カテゴリーフィルタリング
