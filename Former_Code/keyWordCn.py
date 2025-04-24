import jieba
import re
import gensim.downloader as api
import streamlit as st
from gensim.models import KeyedVectors


wv_path = r"..\..\models\100000-small.txt"
wv = KeyedVectors.load_word2vec_format(wv_path, binary=False)

def extractKeywords(text, top_n=5):
    # 使用jieba进行中文分词
    words = jieba.lcut(text)
    # 将分词结果重新组合成字符串
    text_cutted = ' '.join(words)
    # 创建TfidfVectorizer对象
    vectorizer = TfidfVectorizer()
    # 计算tf-idf矩阵
    tfidf_matrix = vectorizer.fit_transform([text_cutted])
    # 获取特征词（即词汇表）
    feature_names = vectorizer.get_feature_names_out()
    # 将tf-idf矩阵转为数组并排序，获取前n个关键词
    scores = tfidf_matrix.toarray()[0]
    indices = scores.argsort()[-top_n:][::-1]
    keywords = [feature_names[i] for i in indices]
    return keywords

def chineseSegmentationWithNumbers(text):
    # 使用正则表达式匹配数字
    numbers = re.findall(r'\d+', text)
    # 使用 jieba 进行分词
    words = jieba.lcut(text)
    # 将分词结果和数字合并
    result = []
    for word in words:
        if word.isdigit():
            result.append(word)
        else:
            # 如果单词包含数字，进一步拆分
            parts = re.split(r'(\d+)', word)
            for part in parts:
                if part:
                    result.append(part)
    return result

def find_matches(words, preset_words, threshold=0.6):
    matches = []
    for word in words:
        for preset in preset_words:
            try:
                similarity = wv.similarity(word, preset)
                if similarity >= threshold:
                    matches.append((word, preset, similarity))
            except KeyError:  # 处理未登录词
                continue
    return matches


# 预设词库
preset_words = {'消除', '删除', '移除', '去掉'}

def checkThreeStages(segmented_words, word_id_mapping, similarity_threshold=0.6):
    preset_words = set()
    #st = StreamlitMagic()  # 假设st是已经定义好的Streamlit对象或类似的通知机制
    
    for i, word in enumerate(segmented_words):
        try:
            if word in preset_words:
                continue
            
            similarity = wv.similarity(word, '消除')
            if similarity >= similarity_threshold:
                preset_words.add(word)
                continue
            
            st.warning(f"未找到消除指令,请检查第 {i+1} 个词: {word}")
        
        except KeyError:  # 处理未登录词
            st.warning(f"文本中含有生僻字/词,请检查第 {i+1} 个词: {word}")
        
        object_types = set(word_id_mapping.keys())
        union1 = object_types & {word}
        if not union1:
            print(f"消除对象名称不匹配,请检查第 {i+1} 个词: {word}")
            continue
        
        target_values = set()
        for ids in word_id_mapping.values():
            target_values.update(ids)
        union2 = target_values & {word}
        if not union2:
            print(f"消除对象ID不匹配,请检查第 {i+1} 个词: {word}")
            continue
        
        print(f"第 {i+1} 个词: {word} 通过所有检查")
    
    if not preset_words:
        st.warning("未找到消除指令,请重新输入")
        
    print("True")

  

# word_id_mapping = {"person": ['1', '2', '3']}
# words = chineseSegmentationWithNumbers("消除person1")
# checkThreeStages(words, word_id_mapping)


# if __name__ == "__main__":
#     # 示例文本（已分词）
#     text = "请完全消除person1并移除所有相关数据"
#     words = chineseSegmentationWithNumbers(text)
    
#     # 查找匹配项
#     matches = find_matches(words, preset_words,0.3)
    
#     print("原始分词:", words)
#     print("匹配结果:")
#     for src, target, similarity in matches:
#         print(f"{src} -> {target} (相似度: {similarity:.2f})")


# for item in sorted_detected_object_ids:
#     # 使用正则表达式分离字母和数字部分
#     match = re.match(r"([a-zA-Z]+)(\d+)", item)
#     if match:
#         word = match.group(1).lower()  # 统一转为小写
#         num_id = match.group(2)
        
#         # 将字符串数字转为整数，也可以保持字符串形式
#         if word not in word_id_mapping:
#             word_id_mapping[word] = []
#         word_id_mapping[word].append(int(num_id))  # 使用int(num_id)转为数字

# # 打印结果
# for word, ids in word_id_mapping.items():
#     print(f"单词 '{word}' 包含ID: {sorted(ids)}")
