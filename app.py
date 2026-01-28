import streamlit as st

st.set_page_config(page_title="招标文件智能分析系统", page_icon="📊")

st.title("📊 招标文件智能分析系统")

tender_file = st.file_uploader("上传招标文件")
bid_file = st.file_uploader("上传投标文件")

if st.button("开始分析"):
    st.info("演示模式：请上传完整代码后使用")