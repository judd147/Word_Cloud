# -*- coding: utf-8 -*-
"""
Created on Tue Jun 7 10:45:46 2022

@author: zhangliyao
"""

import streamlit as st
import pandas as pd
import jieba.analyse
import imageio
from wordcloud import WordCloud
from matplotlib import colors

def main():
    jieba_cut()
    
def jieba_cut():
    st.header("词云分析")
    st.caption('上传文本在线生成词云图')
    num_color = st.number_input("字体颜色数量", min_value=1, max_value=8, value=3)
    with st.form(key='word_freq'):
        #文件设置
        fr = st.file_uploader("上传停用词", type='txt', key='stop_word')
        fr_xyj = st.file_uploader("上传分析文本", type='txt', key='text')
        shape = st.file_uploader("上传词云形状", type=['jpg','png'], key='word_cloud')
        
        col1, col2, col3 = st.columns(3)
        with col1:
            num_show = st.number_input("输出词汇数（按排名）", min_value=1, max_value=500, value=100, help="显示词频表中前xxx个词")
            min_font_size = st.number_input("字体最小值", min_value=1, max_value=50, value=5)
            bg_color = st.color_picker('背景颜色', '#FFFFFF', help="词云图背景颜色，默认为白色")
            
        with col2:
            max_words = st.number_input("显示最大词数", min_value=1, max_value=500, value=80, help="词云图显示最大词数")
            max_font_size = st.number_input("字体最大值", min_value=50, max_value=300, value=150)
            
            
        with col3:
            colloc_choice = st.selectbox("是否允许词汇重复显示", options=['否','是'])
            prefer_horizontal = st.number_input("词汇横排比例", min_value=0.0, max_value=1.0, value=1.0, help="区间为0-1，越趋于0竖向分词比例越高")
        
        color_list_input = []
        col01, col02, col03, col04 = st.columns(4)
        if num_color >= 1:
            with col01:
                color1 = st.color_picker('字体颜色', '#228B22', help="自定义颜色")
                color_list_input.append(color1)
        if num_color >= 2:
            with col02:
                color2 = st.color_picker('字体颜色', '#CD661D', help="自定义颜色")
                color_list_input.append(color2)
        if num_color >= 3:
            with col03:
                color3 = st.color_picker('字体颜色', '#5CACEE', help="自定义颜色")
                color_list_input.append(color3)
        if num_color >= 4:
            with col04:
                color4 = st.color_picker('字体颜色', '#FFFFFF', help="自定义颜色")
                color_list_input.append(color4)
        if num_color >= 5:
            col_list = st.columns(4)
            for i in range(num_color-4):
                with col_list[i]:
                    color = st.color_picker('字体颜色', '#FFFFFF', help="自定义颜色", key=i)
                    color_list_input.append(color)

        run = st.form_submit_button(label='运行')
        
    if run:
        stop_word_list = fr.readlines()
        new_stop_word_list = []
        for stop_word in stop_word_list:
            new_stop_word_list.append(stop_word)
        
        #输出词语出现的次数
        s = fr_xyj.read()
        words = jieba.cut(s, cut_all=False)
        word_dict= {}
        word_list = ''
        for word in words:
            if (len(word) > 1 and not word in new_stop_word_list):
                word_list = word_list + ' ' + word
                if (word_dict.get(word)):
                    word_dict[word] = word_dict[word] + 1
                else:
                    word_dict[word] = 1
        fr.close()
        sort_words = sorted(word_dict.items(), key=lambda x:x[1], reverse=True)
        
        #输出词频排名前xxx的词
        wordssc = pd.DataFrame(data=sort_words)
        wordssc = wordssc.reset_index()
        wordssc.columns = ['序号','关键词','词频']
        #wordssc.drop(index=0, inplace=True)
        
        st.subheader('词频表预览')
        st.dataframe(wordssc[0:num_show])
        
        #导出文件
        csv = convert_df(wordssc)
        st.download_button(
             label="下载词频表并退出",
             data=csv,
             file_name='词频表.txt',
             mime='text',
        )

        color_list=color_list_input   #词云图的词颜色列表，设定想要呈现的颜色，几种均可.参考网址：https://tool.oschina.net/commons?type=3
        if colloc_choice == '是':
            collocations = True
        elif colloc_choice == '否':
            collocations = False
            
        wc = WordCloud(
                background_color=bg_color,                # 词云图背景颜色，除了常见几种，还可使用background_color=WordCloud(background_color=(135,206,250)设定
                max_words=max_words,                      # 词云图显示最大词数
                font_path="SIMHEI.TTF",  # 使用字体 SIMHEI.TTF
                min_font_size=min_font_size,              # 字体最小尺寸
                max_font_size=max_font_size,              # 字体最大尺寸
                colormap=colors.ListedColormap(color_list),
                mask=imageio.imread(shape),               # 词云图形状，可用Visio形状工具生成，形状内为黑色，背景白色；或使用ps将所需形状外的部分删除即可
                collocations=collocations,                # 图中的分词能否重复，不重复用False，可重复为True
                prefer_horizontal=prefer_horizontal)      # 图中的分词横排的比例，区间为0-1，越趋于0竖向分词比例越高
        
        wc.generate(word_list)
        st.subheader('词云图')
        st.image(wc.to_array())

@st.cache()
def convert_df(df):
    return df.to_string(index=False).encode('UTF-8')

if __name__ == "__main__":
    main()
