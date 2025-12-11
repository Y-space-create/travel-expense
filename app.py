# app.py 
import streamlit as st
import pandas as pd
import json, os, datetime, base64

DB_FILE = "db.json" 

# ---------- 工具 ----------
@st.cache_data 
def load_db():
    if not os.path.exists(DB_FILE): 
        return {"records": []}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f) 

def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db,  f, ensure_ascii=False, indent=2)

# ---------- Streamlit UI ----------
st.set_page_config( 
    page_title="旅行记账",
    page_icon="💰",
    layout="centered"
)

st.title("💰  旅行记账 · 在线同步版")
st.caption(" 所有人同时填写，实时汇总")

CATEGORIES = ["住宿", "餐饮", "交通", "其他"]

with st.form("add_record"): 
    st.subheader("➕  新增支出")
    col1, col2 = st.columns(2) 
    person   = col1.text_input(" 人员姓名", placeholder="张三")
    category = col2.selectbox(" 分类", CATEGORIES)
    amount   = st.number_input(" 金额（元）", min_value=0.0, step=0.01)
    remark   = st.text_input(" 备注", placeholder="晚餐")
    submitted = st.form_submit_button(" 保存")
    if submitted and person:
        db = load_db()
        db["records"].append({
            "time": datetime.datetime.now().strftime("%Y-%m-%d  %H:%M:%S"),
            "person": person,
            "category": category,
            "amount": amount,
            "remark": remark
        })
        save_db(db)
        st.success(" 已保存")

# ---------- 汇总 ----------
db = load_db()
if db["records"]:

    df = pd.DataFrame(db["records"])

    st.subheader("📊  汇总")
    col1, col2 = st.columns(2) 

    with col1:
        st.write("** 按人员**")
        st.dataframe(
            df.groupby("person")["amount"].sum()
            .reset_index()
            .sort_values("amount", ascending=False)
        )

    with col2:
        st.write("** 按分类**")
        st.dataframe(
            df.groupby("category")["amount"].sum()
            .reset_index()
            .sort_values("amount", ascending=False)
        )

    total = df["amount"].sum()
    st.metric(" 总计", f"{total:.2f} 元")

    st.subheader("📋  明细")
    st.dataframe(df) 

    # CSV 导出
    csv = df.to_csv(index=False).encode() 
    st.download_button("📥  下载 CSV", csv, "travel_expense.csv",  "text/csv")

else:
    st.info(" 暂无记录")

# ---------- 清空 ----------
if st.button("🗑️  清空全部记录"):
    save_db({"records": []})
    st.rerun()
