"""
AI を使ってInstagramのキャプションからレシピ情報を抽出
"""
import os
import json
from typing import Optional, Dict
from dotenv import load_dotenv

load_dotenv()


class AIParser:
    def __init__(self, provider: str = "claude"):
        """
        Args:
            provider: "claude" or "openai"
        """
        self.provider = provider
        
        if provider == "claude":
            from anthropic import Anthropic
            self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        elif provider == "openai":
            from openai import OpenAI
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        else:
            raise ValueError("provider must be 'claude' or 'openai'")
    
    def parse_recipe(self, caption: str, post_url: str = "") -> Optional[Dict]:
        """
        キャプションからレシピ情報を抽出
        
        Returns:
            {
                "title": "レシピ名",
                "ingredients": ["材料1", "材料2", ...],
                "steps": ["手順1", "手順2", ...],
                "cooking_time": "30分",
                "calories": "350kcal",
                "servings": "2人分",
                "category": "家庭料理"
            }
        """
        prompt = f"""以下のInstagram投稿のキャプションから、レシピ情報を抽出してJSON形式で出力してください。

キャプション:
{caption}

以下のJSON形式で出力してください。情報がない項目はnullにしてください：
{{
    "title": "レシピ名",
    "ingredients": ["材料1 分量", "材料2 分量"],
    "steps": ["手順1", "手順2"],
    "cooking_time": "調理時間（例: 30分）",
    "calories": "カロリー（例: 350kcal）",
    "servings": "人数（例: 2人分）",
    "category": "カテゴリー（家庭料理/ヴィーガン/時短/スイーツ/その他）"
}}

JSONのみを出力してください。説明文は不要です。
"""
        
        try:
            if self.provider == "claude":
                response = self.client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=2000,
                    messages=[{"role": "user", "content": prompt}]
                )
                content = response.content[0].text
            else:  # openai
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0
                )
                content = response.choices[0].message.content
            
            # JSONを抽出（```json ``` で囲まれている場合に対応）
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            recipe_data = json.loads(content)
            recipe_data["source_url"] = post_url
            
            return recipe_data
            
        except Exception as e:
            print(f"AI解析エラー: {e}")
            return None


# テスト用
if __name__ == "__main__":
    # サンプルキャプションでテスト
    sample_caption = """
    🍝 簡単トマトパスタ 🍝
    
    【材料】2人分
    ・パスタ 200g
    ・トマト缶 1缶（400g）
    ・にんにく 2片
    ・オリーブオイル 大さじ2
    ・塩 小さじ1
    ・バジル 適量
    
    【作り方】
    1. にんにくをみじん切りにする
    2. フライパンにオリーブオイルとにんにくを入れて弱火で香りを出す
    3. トマト缶を加えて10分煮込む
    4. 茹でたパスタを加えて和える
    5. 塩で味を調えて完成！
    
    調理時間：20分
    カロリー：約450kcal
    
    #パスタ #簡単レシピ #時短レシピ
    """
    
    parser = AIParser(provider="claude")  # or "openai"
    result = parser.parse_recipe(sample_caption)
    
    if result:
        print("✅ 抽出成功！")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("❌ 抽出失敗")
