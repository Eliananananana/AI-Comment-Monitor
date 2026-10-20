import pandas as pd
import json
import time
from openai import OpenAI

# ================= 1. 配置你的 Key =================
API_KEY = "你的_API_KEY_填在这里"

client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.moonshot.cn/v1"
)


# ================= 2. AI 分析函数 =================
def analyze_comment(comment_text):
    prompt = f"""
    你是一个专业的电商客服主管。请分析以下用户的评论：
    "{comment_text}"

    任务：
    1. 判断情感倾向（正向、中性、负向）。
    2. 提取核心问题分类（物流、包装破损、口感、客服态度、其他）。
    3. 如果是负向评论，写一句安抚话术。

    严格只输出 JSON 格式（不要包含 markdown 标记，如 ```json），格式如下：
    {{
        "sentiment": "正向/中性/负向",
        "category": "问题分类",
        "reply": "安抚话术（如果没有问题，填无）"
    }}
    """

    response = client.chat.completions.create(
        model="kimi-k2.6",  # 👈 改成截图里显示的这个名字
        messages=[{"role": "user", "content": prompt}],
        temperature=1,
    )
    result_text = response.choices[0].message.content
    return json.loads(result_text)


# ================= 3. 主流程 =================
def main():
    print("🚀 开始读取数据...")
    # 兼容 Windows 的编码
    df = pd.read_csv('comments.csv', encoding='utf-8')
    results = []

    for index, row in df.iterrows():
        comment = row['comment']
        print(f"正在让 AI 分析第 {index+1} 条...")

        max_retries = 3
        for attempt in range(max_retries):
            try:
                ai_result = analyze_comment(comment)
                results.append({
                    'id': row['id'],
                    'comment': comment,
                    '情感': ai_result.get('sentiment'),
                    '分类': ai_result.get('category'),
                    '安抚话术': ai_result.get('reply')
                })
                break  # 如果成功，跳出重试循环
            except Exception as e:
                print(f"第 {index+1} 条解析出错 (尝试 {attempt+1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2  5)
                else:
                    print(f"第 {index+1} 条最终失败。")

        # ⏳ 关键：如果你充值还没满 50 元，账号依然是 Tier0（每分钟限 3 次）
        # 所以强制等待 21 秒是必须的，否则马上又会 429 报错
        time.sleep(21)

    result_df = pd.DataFrame(results)
    result_df.to_excel('result.xlsx', index=False)
    print("✅ 跑完啦！去文件夹里打开 result.xlsx 看看效果！")


if __name__ == "__main__":
    main()