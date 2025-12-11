"""Utility functions for language processing."""
import re
from collections import defaultdict


def chinese_dominant(sentence: str) -> bool:
    """Check if Chinese characters dominate in the string."""
    chinese_count = 0
    english_count = 0

    for char in sentence:
        # 判断是否为中文字符（常用汉字 Unicode 范围）
        if '\u4e00' <= char <= '\u9fff':
            chinese_count += 1
        # 判断是否为英文字母（大小写）
        elif char.isalpha() and ord(char) < 128:
            english_count += 1

    return chinese_count > english_count



def count_code_block_languages(text: str) -> dict:
    """Count occurrences of different programming languages in code blocks."""
    # 匹配 ```language ... ``` 的模式，非贪婪匹配
    pattern = r'```(\w+)\s*[\s\S]*?```'
    matches = re.findall(pattern, text)

    # 转为小写并统计
    counts = defaultdict(int)
    for lang in matches:
        counts[lang.lower()] += 1

    return dict(counts)


REFUSE_WORDS_LIST = [
    "对不起"
]
