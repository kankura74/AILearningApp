


import os
import json

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field


load_dotenv()


client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)



# Geminiの返却形式をresponse_schema 機能（構造化出力）を使い固定
class EvaluationResult(BaseModel):

    result: str = Field(
        description="OK、NGのいずれか"
    )

    score: int = Field(
        description="0〜100の点数"
    )

    good_points: str = Field(
        description="""
        良かった点。
        コードの正しい部分や評価できる部分を説明してください。
        """
    )

    mistakes: str = Field(
        description="""
        間違いや不足点。
        修正すべき部分を具体的に説明してください。
        """
    )

    improvement: str = Field(
        description="""
        改善例。
        より良いコードの書き方や考え方を説明してください。
        """
    )



def evaluate_answer(question_text, answer_code):


    # 前処理
    answer_code = answer_code.strip()



    # 空欄チェック
    if (
        answer_code == ""
        or answer_code == "# Pythonコードを書いてください"
    ):

        return {
            "result": "NG",
            "score": 0,
            "good_points": "--",
            "mistakes": "空欄またはテンプレートのみの回答です。",
            "improvement": "--"
        }



    prompt = f"""

あなたはPython学習アプリの優しい講師です。

問題:

{question_text}


受講者回答:

{answer_code}



採点基準:

・完全正解 90〜100点
・軽微なミス 60〜89点
・一部だけ正しい 20〜59点
・無関係な回答 0点

採点結果:

・正しく回答できている場合 → OK
・間違いがある場合 → NG
・回答内容を判定できない場合 → UNKNOWN



以下の3項目を必ず埋めてください。

good_points:
良かった点を説明してください。

mistakes:
間違いや不足点を説明してください。

improvement:
改善方法を説明してください。

コードの冗長性や読みやすさについても指摘してください。


"""
    try:


        response = client.models.generate_content(

            model="gemini-2.5-flash-lite",

            contents=prompt,


            config=types.GenerateContentConfig(

                response_mime_type="application/json",

                response_schema=EvaluationResult,


                # 採点の揺れ防止
                temperature=0.2, 

                max_output_tokens=1000

            )

        )


        # JSON → dictへ変換

        result = json.loads(response.text)


        return result



    except Exception as e:


        print(
            f"AIエラー:{e}"
        )


        return {
            "result": "UNKNOWN",
            "score": 0,
            "good_points": "",
            "mistakes": "AIエラー（API例外）",
            "improvement": "再実行してください",
            "reason": "api_error"
        }
    

def generate_learning_comment(
    max_streak,
    current_streak,
    total_days
):

    prompt = f"""

あなたはPython学習アプリの講師です。

ユーザーの学習状況を見て、
モチベーションが上がる短いコメントを作成してください。

学習状況:

・最長継続日数: {max_streak}日
・現在の連続継続日数: {current_streak}日
・総学習日数: {total_days}日


条件:

・100文字以内
・初心者にも優しい表現
・具体的な数字を含める
・改善点があれば優しくアドバイスする
・「頑張りましょう」だけの抽象的な文章は禁止


コメントのみ返してください。

"""


    try:

        response = client.models.generate_content(

            model="gemini-2.5-flash-lite",

            contents=prompt,

            config=types.GenerateContentConfig(

                temperature=0.7,

                max_output_tokens=200

            )

        )


        return response.text


    except Exception as e:

        print(f"AIコメント生成エラー:{e}")

        return "学習を続けることで少しずつ成長しています。今日もコードを書いてみましょう。"