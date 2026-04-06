import streamlit as st
from openai import OpenAI
from fpdf import FPDF
import time
import os

# --- 1. 配置 AI 客户端 ---
# 请确保在 Streamlit Cloud 的 Secrets 中配置了 DEEPSEEK_API_KEY
client = OpenAI(
    api_key = st.secrets["DEEPSEEK_API_KEY"], 
    base_url = "https://api.deepseek.com"
)

# --- 2. PDF 生成类 (支持中文) ---
class CareerPDF(FPDF):
    def header(self):
        try:
            # 自动检测当前目录下的字体文件
            font_path = os.path.join(os.path.dirname(__file__), "simsun.ttf")
            self.add_font('Chinese', '', font_path, uni=True)
            self.set_font('Chinese', '', 10)
        except:
            self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, '轨交院转型评估报告 - 2026专业版', 0, 1, 'R')

    def footer(self):
        self.set_y(-15)
        try:
            self.set_font('Chinese', '', 8)
        except:
            self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'第 {self.page_no()} 页', 0, 0, 'C')

def generate_pdf(report_sections):
    pdf = CareerPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    font_path = os.path.join(os.path.dirname(__file__), "simsun.ttf")
    pdf.add_font('Chinese', '', font_path, uni=True)

    # 封面页
    pdf.add_page()
    pdf.set_font('Chinese', '', 32)
    pdf.ln(50)
    pdf.cell(0, 20, "职业转型评估深度报告", 0, 1, 'C')
    pdf.set_font('Chinese', '', 14)
    pdf.cell(0, 10, "轨道交通设计院从业人员专项", 0, 1, 'C')
    pdf.ln(100)
    pdf.cell(0, 10, f"生成日期: {time.strftime('%Y-%m-%d')}", 0, 1, 'C')

    # 正文页
    pdf.add_page()
    for title, content in report_sections.items():
        pdf.set_font('Chinese', '', 16)
        pdf.cell(0, 15, title, 0, 1, 'L')
        pdf.set_font('Chinese', '', 11)
        pdf.multi_cell(0, 8, content)
        pdf.ln(5)

    return pdf.output()

# --- 3. 状态初始化 ---
if 'report_ready' not in st.session_state:
    st.session_state.report_ready = False
if 'report_data' not in st.session_state:
    st.session_state.report_data = None

# --- 4. 网页界面 ---
st.set_page_config(page_title="轨交院转型评估系统", layout="centered")

st.title("🚇 轨道交通设计院转型评估系统")
st.caption("针对土建、通号、机电等专业，AI 驱动的 2026 职业路径规划")

# 表单部分
with st.form("user_data"):
    col1, col2 = st.columns(2)
    with col1:
        major = st.selectbox("所属专业", ["线路站场", "通信信号", "供电照明", "土建结构", "机电环控"])
        years = st.number_input("工作年限", 1, 30, 5)
    with col2:
        personality = st.text_input("性格标签", "严谨")
        hobby = st.text_input("兴趣爱好", "数码、摄影")

    exp = st.text_area("主要项目经验 (建议 200 字以上)")
    submit_base = st.form_submit_button("开始评估")

# --- 5. 逻辑处理 ---
if submit_base:
    st.divider()
    st.subheader("📋 初步评估摘要")
    st.info(f"根据您的【{major}】背景，系统判定您在『系统集成』和『工程数字化』领域有极高潜能。")
    st.success("✨ 深度报告内容已就绪（内容约 10-15 页）")
    
    # 展示二维码
    st.markdown("### 🔓 获取完整 10 页 PDF 报告")
    st.write("请扫码支付 **0.1 元** 咨询费，支付后即可点击下方按钮生成。")
    if os.path.exists("pay_qr.png"):
        st.image("pay_qr.png", caption="微信/支付宝扫码支付", width=250)
    else:
        st.error("未找到二维码图片 pay_qr.png")

# 重要：不要嵌套按钮！将生成按钮放在 form 之外
if not st.session_state.report_ready:
    if st.button("我已支付，立即开始生成报告"):
        if not exp:
            st.error("请先在上方填写项目经验并点击『开始评估』按钮")
        else:
            report_data = {}
            sections = [
                "当前行业形势与轨道交通人才价值锚点",
                "基于个人项目经验的硬技能迁移性深度分析",
                "推荐转型方向一：低空经济与智慧交通融合",
                "推荐转型方向二：BIM/数字化转型顾问路径",
                "未来 3 年技能补齐路线图与学习清单",
                "简历去'土化'修改建议与面试突围策略"
            ]
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                for i, s_title in enumerate(sections):
                    status_text.text(f"正在撰写第 {i+1}/6 章节: {s_title}...")
                    prompt = f"针对{major}专业，{years}年经验，性格{personality}，经验：{exp}。请详细撰写：{s_title}。要求字数在 1200 字以上，条理清晰，专业性强。"
                    
                    res = client.chat.completions.create(
                        model="deepseek-chat", 
                        messages=[{"role": "user", "content": prompt}]
                    )
                    report_data[s_title] = res.choices[0].message.content
                    progress_bar.progress((i + 1) / len(sections))
                
                st.session_state.report_data = report_data
                st.session_state.report_ready = True
                st.rerun() # 强制刷新显示下载按钮
                
            except Exception as e:
                st.error(f"生成失败，请检查 API 或网络：{e}")

# 显示下载按钮
if st.session_state.report_ready and st.session_state.report_data:
    st.balloons()
    try:
        # 1. 生成 PDF 数据
        pdf_data = generate_pdf(st.session_state.report_data)
        
        # 2. 这里的 pdf_data 现在已经是二进制格式了
        st.download_button(
            label="📥 下载您的 10 页深度评估报告 (PDF)",
            data=pdf_data, # 直接传入
            file_name=f"轨交转型报告_{major}.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        # 如果还有错，这行会告诉你具体的错误
        st.error(f"PDF 渲染失败：{e}")
