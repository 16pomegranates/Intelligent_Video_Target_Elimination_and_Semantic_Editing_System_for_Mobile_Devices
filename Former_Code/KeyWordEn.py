#近义词
# import nltk
# from nltk.corpus import wordnet
# nltk.download('wordnet')  
# nltk.download('punkt_tab')
# synsets = wordnet.synsets("remove")
# for syn in synsets:
#     print(syn.lemma_names())  # 输出: ['happy', 'felicitous'], ['happy'], ['happy', 'glad'], ['happy', 'well-chosen']
    
from nltk.tokenize import word_tokenize
from googletrans import Translator
import streamlit as st
import re
# 将表示数字的单词转换为数字
number_words = {
    "one": 1,       "first":1,
    "two": 2,       "second":2,
    "three": 3,     "third":3,
    "four": 4,      "fourth":4,
    "five": 5,      "fifth":5,
    "six": 6,       "sixth":6,
    "seven": 7,     "seventh":7,
    "eight": 8,     "eighth":8,
    "nine": 9,      "ninth":9,
    "ten": 10,      "tenth":10,
    "eleven": 11,   "eleventh":11,
    "twelve": 12,   "twelfth":12,
    "thirteen": 13, "thirteenth":13,
    "fourteen": 14, "fourteenth":14,
    "fifteen": 15,  "fifteenth":15,
    "sixteen": 16,  "sixteenth":16,
    "seventeen": 17,"seventeenth":17,
    "eighteen": 18, "eighteenth":18,
    "nineteen": 19, "nineteenth":19,
    "twenty": 20,   "twentieth":20
}

target_classes = {"person": "人","animal":"动物","bicycle":"自行车"}

# 表示“消除”的单词列表
eliminate_synonyms = ["eliminate", "remove", "delete"]

# 原始文本
text = "消除第一个人" 


# # 要翻译的文本
# text = "c旁边的人"

# # 翻译成英文
# translated = translator.translate(text, src='zh-cn', dest='en')

# # 输出翻译结果
# print(translated.text)

#分词
def tokenize(text):
    # 翻译
    print("text:", text)
    translator = Translator()
    translated_text = translator.translate(text, dest='en')
    text = translated_text.text.lower()
    print("translated_text:", translated_text.text)

    # 使用正则表达式将字符与数字之间没有空格直接连接的字符串分割
    text = re.sub(r'([a-zA-Z]+)(\d+)', r'\1 \2', text)
    tokens = word_tokenize(text)
    print("tokens:", tokens)

    # 将表示数字的单词转换为数字
    final_tokens = []
    for word in tokens:
        if word.lower() in number_words:
            final_tokens.append(str(number_words[word.lower()]))
        else:
            final_tokens.append(word.lower())

    print("final_tokens:", final_tokens)
    return final_tokens

def checkRemoveObjects(target_classes,detected_object_ids,filtered_tokens):
    target_remove_objects = []

    p = 0
    #第一步检查，查找“删除”关键词
    for index, word in enumerate(filtered_tokens):
        if word.lower() in eliminate_synonyms:
            step1 = True
            print(f"检测到表示消除的单词: {word}，位置为第 {index + 1} 个单词")
            p = index
            break 
    else:
        print("未检测到表示消除的单词")
        return target_remove_objects

    #第二步检查，获取目标对象
    targetlist = []
    numberlist = []
    for index in range(p + 1, len(filtered_tokens)):
        word = filtered_tokens[index]
        if word in target_classes:  # 检查是否与 target_classes 的 key 一致
            targetlist.append(word)
        elif word.isdigit():  # 检查是否是数字
            numberlist.append(word)

    print("targetlist:", targetlist)
    print("numberlist:", numberlist)

    #第三步检查，组合目标对象和数字
    if len(targetlist) != len(numberlist):
        print("targetlist 和 numberlist 的大小不一致，程序终止。")
        return target_remove_objects

    for i in range(len(targetlist)):
        combined_string = targetlist[i] + ' ' + numberlist[i]
        if combined_string in detected_object_ids:
            target_remove_objects.append(combined_string)

    print("target_remove_objects:", target_remove_objects)
    return target_remove_objects

#checkRemoveObjects(target_classes,["person1"],tokenize(text))
