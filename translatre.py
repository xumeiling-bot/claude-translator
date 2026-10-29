import os
import json
from anthropic import Anthropic

# 初始化 Claude 客户端（从云端环境自动读取密钥）
client = Anthropic()

# 需要翻译的 10 个目标小语种列表（可以根据你的需要随时修改）
TARGET_LANGUAGES = [
    "Vietnamese (Vietnam)", "Thai (Thailand)", "Indonesian (Indonesia)", 
    "Malay (Malaysia)", "Tagalog (Philippines)", "Hindi (India)", 
    "Arabic (Saudi Arabia)", "Turkish (Turkey)", "Polish (Poland)", "Dutch (Netherlands)"
]

# 核心：专门针对高度“本地化”的翻译系统提示词
SYSTEM_PROMPT = """
You are an expert native translator and localization specialist. Your goal is to translate Chinese documents into the target language.

CRITICAL REQUIREMENTS FOR LOCALIZATION:
1. DO NOT do a word-for-word literal translation. Rewrite the text so it sounds like it was originally written by a professional native speaker in the target country.
2. Adapt cultural references, idioms, tone, and formatting (like currency, date formats, and counting units) to match local consumer habits and business etiquette.
3. Maintain the original core message and emotional undertone (e.g., professional, casual, persuasive).
4. Output ONLY the final localized translation, without any introduction, explanations, or markdown wrappers like ```.
"""

def translate_text(text, target_lang):
    prompt = f"Please translate the following Chinese text into deeply localized {target_lang}. \n\nOriginal Chinese Text:\n{text}"
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4000,
        temperature=0.3,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content.text

def batch_process(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    if not os.path.exists(input_dir):
        os.makedirs(input_dir)
        print(f"📁 已自动创建 '{input_dir}' 文件夹。请把你要翻译的中文 .txt 文件放进去。")
        return

    files = [f for f in os.listdir(input_dir) if f.endswith(".txt") or f.endswith(".md")]
    if not files:
        print(f"ℹ️ 在 '{input_dir}' 文件夹中没有找到任何中文文档（.txt 或 .md）。")
        return
        
    for filename in files:
        file_path = os.path.join(input_dir, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            chinese_content = f.read()
            
        print(f"📄 正在处理文件: {filename}...")
        
        for lang in TARGET_LANGUAGES:
            lang_name = lang.split(" ")[0]
            lang_folder = os.path.join(output_dir, lang_name)
            if not os.path.exists(lang_folder):
                os.makedirs(lang_folder)
            
            print(f"   ➔ 正在翻译成 {lang}...")
            try:
                translated_content = translate_text(chinese_content, lang)
                output_file_path = os.path.join(lang_folder, f"{os.path.splitext(filename)[0]}_{lang_name}.txt")
                with open(output_file_path, "w", encoding="utf-8") as out_f:
                    out_f.write(translated_content)
            except Exception as e:
                print(f"   ❌ 翻译出错 ({lang}): {e}")

if __name__ == "__main__":
    INPUT_DIRECTORY = "./chinese_docs"
    OUTPUT_DIRECTORY = "./translated_docs"
    batch_process(INPUT_DIRECTORY, OUTPUT_DIRECTORY)
    print("✅ 恭喜！所有批量本地化翻译任务已全部完成！")

