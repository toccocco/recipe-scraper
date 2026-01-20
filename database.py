"""
レシピデータベース管理
"""
import sqlite3
import json
from typing import List, Optional, Dict
from datetime import datetime


class RecipeDatabase:
    def __init__(self, db_path: str = "recipes.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """データベースとテーブルを初期化"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS recipes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    ingredients TEXT,
                    steps TEXT,
                    cooking_time TEXT,
                    calories TEXT,
                    servings TEXT,
                    category TEXT,
                    source_url TEXT UNIQUE,
                    username TEXT,
                    likes INTEGER,
                    created_at TEXT
                )
            """)
            
            conn.commit()
            conn.close()
            print(f"データベース初期化完了: {self.db_path}")
        except Exception as e:
            print(f"データベース初期化エラー: {e}")
    
    def save_recipe(self, recipe_data: Dict, post_data: Dict) -> bool:
        """レシピを保存"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO recipes 
                (title, ingredients, steps, cooking_time, calories, servings, 
                 category, source_url, username, likes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                recipe_data.get("title"),
                json.dumps(recipe_data.get("ingredients", []), ensure_ascii=False),
                json.dumps(recipe_data.get("steps", []), ensure_ascii=False),
                recipe_data.get("cooking_time"),
                recipe_data.get("calories"),
                recipe_data.get("servings"),
                recipe_data.get("category"),
                post_data.get("url"),
                post_data.get("username"),
                post_data.get("likes"),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ 保存エラー: {e}")
            return False
    
    def get_all_recipes(self) -> List[Dict]:
        """全レシピを取得"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM recipes ORDER BY created_at DESC")
            rows = cursor.fetchall()
            conn.close()
            
            recipes = []
            for row in rows:
                recipes.append({
                    "id": row[0],
                    "title": row[1],
                    "ingredients": json.loads(row[2]) if row[2] else [],
                    "steps": json.loads(row[3]) if row[3] else [],
                    "cooking_time": row[4],
                    "calories": row[5],
                    "servings": row[6],
                    "category": row[7],
                    "source_url": row[8],
                    "username": row[9],
                    "likes": row[10],
                    "created_at": row[11]
                })
            
            return recipes
        except Exception as e:
            print(f"レシピ取得エラー: {e}")
            return []
    
    def search_recipes(self, keyword: str) -> List[Dict]:
        """キーワードでレシピを検索"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM recipes 
            WHERE title LIKE ? OR ingredients LIKE ? OR category LIKE ?
            ORDER BY created_at DESC
        """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
        
        rows = cursor.fetchall()
        conn.close()
        
        recipes = []
        for row in rows:
            recipes.append({
                "id": row[0],
                "title": row[1],
                "ingredients": json.loads(row[2]) if row[2] else [],
                "steps": json.loads(row[3]) if row[3] else [],
                "cooking_time": row[4],
                "calories": row[5],
                "servings": row[6],
                "category": row[7],
                "source_url": row[8],
                "username": row[9],
                "likes": row[10],
                "created_at": row[11]
            })
        
        return recipes
