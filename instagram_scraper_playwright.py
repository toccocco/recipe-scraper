"""
Playwright を使ったInstagramスクレイパー（より安定）
"""
import time
import json
from typing import Optional, Dict
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout


class InstagramScraperPlaywright:
    def __init__(self, headless: bool = True):
        """
        Args:
            headless: ブラウザを表示しない場合True
        """
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
    
    def __enter__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.context = self.browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        self.page = self.context.new_page()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
    
    def get_post_from_url(self, url: str) -> Optional[Dict]:
        """
        Instagram投稿URLから情報を取得
        
        Args:
            url: Instagram投稿のURL
        
        Returns:
            {
                "caption": "投稿のキャプション",
                "url": "投稿URL",
                "username": "投稿者名",
                "likes": いいね数,
                "date": "投稿日時"
            }
        """
        try:
            print(f"   ブラウザでページを開いています...")
            self.page.goto(url, wait_until='networkidle', timeout=30000)
            
            # 少し待機（コンテンツの読み込み）
            time.sleep(3)
            
            # ページのHTMLを取得
            content = self.page.content()
            
            # JSON-LDデータを探す（構造化データ）
            json_ld_data = None
            try:
                json_ld_script = self.page.locator('script[type="application/ld+json"]').first
                if json_ld_script:
                    json_text = json_ld_script.inner_text()
                    json_ld_data = json.loads(json_text)
            except:
                pass
            
            # キャプションを取得
            caption = ""
            try:
                # 複数の方法を試す
                selectors = [
                    'meta[property="og:description"]',
                    'meta[name="description"]',
                ]
                
                for selector in selectors:
                    try:
                        element = self.page.locator(selector).first
                        if element:
                            caption = element.get_attribute('content') or ""
                            if caption:
                                break
                    except:
                        continue
                
                # それでも取れない場合、h1タグを探す
                if not caption:
                    try:
                        h1_element = self.page.locator('h1').first
                        if h1_element:
                            caption = h1_element.inner_text()
                    except:
                        pass
                        
            except Exception as e:
                print(f"   ⚠️  キャプション取得エラー: {e}")
            
            # ユーザー名を取得
            username = ""
            try:
                username_element = self.page.locator('meta[property="og:title"]').first
                if username_element:
                    title = username_element.get_attribute('content') or ""
                    # "(@username)" の形式から抽出
                    if "(@" in title:
                        username = title.split("(@")[1].split(")")[0]
            except:
                pass
            
            # いいね数（取得できない場合が多い）
            likes = 0
            
            # 投稿日時（取得できない場合が多い）
            date = ""
            
            if not caption:
                print("   ⚠️  キャプションが取得できませんでした")
                return None
            
            return {
                "caption": caption,
                "url": url,
                "username": username or "unknown",
                "likes": likes,
                "date": date,
            }
            
        except PlaywrightTimeout:
            print(f"   ❌ タイムアウト: ページの読み込みに時間がかかりすぎました")
            return None
        except Exception as e:
            print(f"   ❌ 投稿取得エラー: {e}")
            return None


# テスト用
if __name__ == "__main__":
    test_url = "https://www.instagram.com/p/DThsVsFj1Tl/"
    
    print("=" * 60)
    print("📱 Playwright版 Instagram取得テスト")
    print("=" * 60)
    print(f"\n📥 投稿を取得中: {test_url}")
    
    with InstagramScraperPlaywright(headless=True) as scraper:
        post_data = scraper.get_post_from_url(test_url)
        
        if post_data:
            print("\n✅ 取得成功！")
            print(f"投稿者: {post_data['username']}")
            print(f"\nキャプション:\n{post_data['caption'][:300]}...")
        else:
            print("\n❌ 取得失敗")
