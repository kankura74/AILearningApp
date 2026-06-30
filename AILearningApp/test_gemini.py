from AILearningApp.services.ai_service import (
    evaluate_answer
)

result = evaluate_answer(
    'name に "Taro" を代入してください',
    'name = "Taro"'
)

print(result)