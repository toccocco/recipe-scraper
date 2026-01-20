"""
Streamlit版 Instagram レシピ抽出ツール（デバッグ強化版）
"""
import streamlit as st
import time
from instagram_scraper_playwright import InstagramScraperPlaywright
from ai_parser import AIParser
from database import RecipeDatabase
import pandas as pd
import traceback

# ページ設定
st.set_page_config(
    page_title="Instagram レシピ抽出ツール",
    page_icon="📱",
    layout="wide"
)

# 初期化
@st.cache_resource
def init_components():
    parser = AIParser(provider="claude")
    db = RecipeDatabase()
    return parser, db

parser, db = init_components()

# メインタイトル
st.title("📱 Instagram レシピ抽出ツール")
st.markdown("Instagram投稿からレシピを自動抽出して保存")

# タブの作成
tab1, tab2, tab3 = st.tabs(["🔍 レシピ抽出", "📚 保存済みレシピ", "🔧 デバッグ"])

# タブ1: レシピ抽出
with tab1:
    st.header("Instagram URLからレシピを抽出")
    
    # URL入力
    instagram_url = st.text_input(
        "Instagram投稿のURLを入力してください",
        placeholder="https://www.instagram.com/p/...",
        help="Instagram投稿のURLを貼り付けてください"
    )
    
    # 抽出ボタン
    if st.button("🤖 レシピを抽出", type="primary", use_container_width=True):
        if not instagram_url:
            st.error("URLを入力してください")
        elif "instagram.com" not in instagram_url:
            st.error("有効なInstagram URLを入力してください")
        else:
            # プログレスバー
            progress_bar = st.progress(0)
            status_text = st.empty()
            debug_info = st.empty()
            
            try:
                # ステップ1: Instagram投稿取得
                status_text.text("📥 Instagram投稿を取得中...")
                debug_info.text("ブラウザを起動しています...")
                progress_bar.progress(25)
                
                with InstagramScraperPlaywright(headless=True) as scraper:
                    post_data = scraper.get_post_from_url(instagram_url)
                
                if not post_data:
                    st.error("❌ 投稿の取得に失敗しました")
                    debug_info.text("Instagram投稿が取得できませんでした。URLが正しいか、投稿が公開されているか確認してください。")
                    st.stop()
                
                progress_bar.progress(50)
                status_text.text("✅ 投稿を取得しました")
                debug_info.text(f"キャプション長: {len(post_data.get('caption', ''))}文字")
                
                # デバッグ情報を表示
                with st.expander("📋 取得した投稿データ", expanded=False):
                    st.write("**投稿者:**", post_data.get('username', 'unknown'))
                    st.write("**キャプション（最初の500文字）:**")
                    st.text(post_data.get('caption', '')[:500] + "..." if len(post_data.get('caption', '')) > 500 else post_data.get('caption', ''))
                
                # ステップ2: AI解析
                status_text.text("🤖 AIでレシピ情報を抽出中...")
                debug_info.text("Claude APIに送信中...")
                progress_bar.progress(75)
                
                recipe_data = parser.parse_recipe(post_data['caption'], post_data['url'])
                
                if not recipe_data:
                    st.error("❌ レシピ情報の抽出に失敗しました")
                    debug_info.text("AI解析でレシピ情報を抽出できませんでした。投稿にレシピが含まれているか確認してください。")
                    
                    # スマホでも見やすいエラー詳細
                    st.warning("🔧 トラブルシューティング")
                    st.write("1. サイドバーの「🧪 AI解析テスト」を試してください")
                    st.write("2. APIキーが設定されているか確認してください")
                    st.write("3. 投稿にレシピが含まれているか確認してください")
                    
                    st.stop()
                
                # ステップ3: データベースに保存
                status_text.text("💾 データベースに保存中...")
                debug_info.text("SQLiteに保存中...")
                progress_bar.progress(90)
                
                db.save_recipe(recipe_data, post_data)
                
                progress_bar.progress(100)
                status_text.text("✅ 完了しました！")
                debug_info.text("すべての処理が完了しました。")
                
                # 結果表示
                st.success("🎉 レシピを抽出して保存しました！")
                
                # レシピ詳細を表示
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.subheader(f"📝 {recipe_data.get('title', '(タイトルなし)')}")
                    
                    # メタ情報
                    meta_cols = st.columns(4)
                    with meta_cols[0]:
                        if recipe_data.get('category'):
                            st.metric("カテゴリー", recipe_data['category'])
                    with meta_cols[1]:
                        if recipe_data.get('cooking_time'):
                            st.metric("調理時間", recipe_data['cooking_time'])
                    with meta_cols[2]:
                        if recipe_data.get('calories'):
                            st.metric("カロリー", recipe_data['calories'])
                    with meta_cols[3]:
                        if recipe_data.get('servings'):
                            st.metric("人数", recipe_data['servings'])
                    
                    # 材料
                    if recipe_data.get('ingredients'):
                        st.subheader(f"🥕 材料 ({len(recipe_data['ingredients'])}個)")
                        for i, ingredient in enumerate(recipe_data['ingredients'], 1):
                            st.write(f"{i}. {ingredient}")
                    
                    # 手順
                    if recipe_data.get('steps'):
                        st.subheader(f"👩‍🍳 手順 ({len(recipe_data['steps'])}ステップ)")
                        for i, step in enumerate(recipe_data['steps'], 1):
                            st.write(f"{i}. {step}")
                
                with col2:
                    st.subheader("📎 元の投稿")
                    st.write(f"投稿者: @{post_data['username']}")
                    st.link_button("Instagram で見る", recipe_data['source_url'])
                
            except Exception as e:
                st.error(f"❌ エラーが発生しました: {str(e)}")
                debug_info.text(f"詳細エラー: {traceback.format_exc()}")
                
                # デバッグ情報
                with st.expander("🔧 エラー詳細", expanded=True):
                    st.code(traceback.format_exc())
                    
            finally:
                progress_bar.empty()
                status_text.empty()

# タブ2: 保存済みレシピ
with tab2:
    st.header("保存済みレシピ一覧")
    
    # 検索機能
    col1, col2 = st.columns([3, 1])
    with col1:
        search_keyword = st.text_input("🔍 レシピを検索", placeholder="材料名、カテゴリーなど")
    with col2:
        if st.button("検索", use_container_width=True):
            st.rerun()
    
    # レシピ取得
    if search_keyword:
        recipes = db.search_recipes(search_keyword)
        st.subheader(f"検索結果: {len(recipes)}件")
    else:
        recipes = db.get_all_recipes()
        st.subheader(f"全レシピ: {len(recipes)}件")
    
    if not recipes:
        st.info("レシピが見つかりませんでした")
    else:
        # レシピ一覧表示
        for recipe in recipes:
            with st.expander(f"📝 {recipe['title'] or '(タイトルなし)'}", expanded=False):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    # メタ情報
                    meta_info = []
                    if recipe['category']:
                        meta_info.append(f"📂 {recipe['category']}")
                    if recipe['cooking_time']:
                        meta_info.append(f"⏱️ {recipe['cooking_time']}")
                    if recipe['calories']:
                        meta_info.append(f"🔥 {recipe['calories']}")
                    if recipe['servings']:
                        meta_info.append(f"👥 {recipe['servings']}")
                    
                    if meta_info:
                        st.write(" | ".join(meta_info))
                    
                    # 材料
                    if recipe['ingredients']:
                        st.write("**材料:**")
                        for ingredient in recipe['ingredients']:
                            st.write(f"• {ingredient}")
                    
                    # 手順
                    if recipe['steps']:
                        st.write("**手順:**")
                        for i, step in enumerate(recipe['steps'], 1):
                            st.write(f"{i}. {step}")
                
                with col2:
                    st.write(f"**投稿者:** @{recipe['username']}")
                    st.write(f"**保存日:** {recipe['created_at'][:10]}")
                    if recipe['source_url']:
                        st.link_button("元の投稿", recipe['source_url'])

# タブ3: デバッグ
with tab3:
    st.header("🔧 デバッグ情報")
    
    # システム情報
    st.subheader("システム情報")
    import os, sys
    st.write(f"**Python バージョン:** {sys.version}")
    st.write(f"**作業ディレクトリ:** {os.getcwd()}")
    
    # 環境変数チェック
    st.subheader("環境変数")
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        st.success(f"✅ ANTHROPIC_API_KEY: 設定済み (長さ: {len(api_key)}文字)")
    else:
        st.error("❌ ANTHROPIC_API_KEY: 未設定")
    
    # テスト機能
    st.subheader("テスト機能")
    
    if st.button("🧪 AI解析テスト"):
        test_text = """
        🍝 簡単トマトパスタ 🍝
        
        【材料】2人分
        ・パスタ 200g
        ・トマト缶 1缶（400g）
        ・にんにく 2片
        
        【作り方】
        1. にんにくをみじん切りにする
        2. フライパンで炒める
        3. パスタを茹でて和える
        
        調理時間：20分
        """
        
        try:
            result = parser.parse_recipe(test_text, "https://test.com")
            if result:
                st.success("✅ AI解析テスト成功")
                st.json(result)
            else:
                st.error("❌ AI解析テスト失敗")
        except Exception as e:
            st.error(f"❌ AI解析エラー: {str(e)}")
            st.code(traceback.format_exc())

# サイドバー
with st.sidebar:
    st.header("ℹ️ 使い方")
    st.markdown("""
    1. **レシピ抽出**タブでInstagram URLを入力
    2. 「レシピを抽出」ボタンをクリック
    3. 自動で材料・手順が抽出されます
    4. **保存済みレシピ**タブで一覧・検索が可能
    """)
    
    st.header("⚠️ 注意事項")
    st.markdown("""
    - 1日10-20件程度に抑えてください
    - Instagram側の制限にご注意ください
    - 公開投稿のみ取得可能です
    """)
    
    # 統計情報
    try:
        total_recipes = len(db.get_all_recipes())
        st.metric("保存済みレシピ数", total_recipes)
    except:
        st.metric("保存済みレシピ数", "エラー")
    
    # スマホ用デバッグ機能
    st.header("🔧 クイックデバッグ")
    
    # 環境変数チェック
    import os
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        st.success(f"✅ API設定済み")
    else:
        st.error("❌ API未設定")
    
    # AI解析テスト
    if st.button("🧪 AI解析テスト", use_container_width=True):
        test_text = """
        🍝 簡単トマトパスタ 🍝
        
        【材料】2人分
        ・パスタ 200g
        ・トマト缶 1缶（400g）
        ・にんにく 2片
        
        【作り方】
        1. にんにくをみじん切りにする
        2. フライパンで炒める
        3. パスタを茹でて和える
        
        調理時間：20分
        """
        
        try:
            result = parser.parse_recipe(test_text, "https://test.com")
            if result:
                st.success("✅ AI解析成功")
                st.json(result)
            else:
                st.error("❌ AI解析失敗")
        except Exception as e:
            st.error(f"❌ エラー: {str(e)}")
            st.code(str(e))
