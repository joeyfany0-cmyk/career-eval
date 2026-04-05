import streamlit as st
from openai import OpenAI
from fpdf import FPDF
import time

# --- 1. 配置 AI 客户端 (以 DeepSeek 为例) ---
client = OpenAI(
    api_key = st.secrets["DEEPSEEK_API_KEY"], 
    base_url = "https://api.deepseek.com"
)


# --- 2. PDF 生成类 (支持中文) ---
class CareerPDF(FPDF):
    def header(self):
        # 需确保目录下有 simsun.ttf 字体文件
        try:
            self.add_font('Chinese', '', 'simsun.ttf', uni=True)
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

    # 封面页
    pdf.add_page()
    pdf.add_font('Chinese', '', 'simsun.ttf', uni=True)
    pdf.set_font('Chinese', '', 32)
    pdf.ln(50)
    pdf.cell(0, 20, "职业转型评估深度报告", 0, 1, 'C')
    pdf.set_font('Chinese', '', 14)
    pdf.cell(0, 10, "轨道交通设计院从业人员专项", 0, 1, 'C')
    pdf.ln(100)
    pdf.cell(0, 10, f"生成日期: {time.strftime('%Y-%m-%d')}", 0, 1, 'C')

    # 正文页
    pdf.add_page()
    pdf.set_font('Chinese', '', 12)
    for title, content in report_sections.items():
        pdf.set_font('Chinese', '', 16)
        pdf.cell(0, 15, title, 0, 1, 'L')
        pdf.set_font('Chinese', '', 11)
        pdf.multi_cell(0, 8, content)
        pdf.ln(5)

    return pdf.output(dest='S').encode('latin-1')


# --- 3. 网页界面 ---
st.set_page_config(page_title="轨交院转型评估系统", layout="centered")

st.title("🚇 轨道交通设计院转型评估系统")
st.caption("针对土建、通号、机电等专业，AI 驱动的 2026 职业路径规划")

with st.form("user_data"):
    col1, col2 = st.columns(2)
    with col1:
        major = st.selectbox("所属专业", ["线路站场", "通信信号", "供电照明", "土建结构", "机电环控"])
        years = st.number_input("工作年限", 1, 30, 5)
    with col2:
        personality = st.text_input("性格标签 (如: 严谨、追求创意)", "严谨")
        hobby = st.text_input("兴趣爱好", "数码、摄影")

    exp = st.text_area("主要项目经验 (建议输入 200 字以上，越详细评估越准)")

    submit = st.form_submit_button("生成基础评估")

# --- 4. 生成逻辑 ---
if submit:
    st.divider()
    # 简版展示
    st.subheader("📋 初步评估摘要")
    with st.spinner("AI 正在分析行业趋势..."):
        # 这里为了演示，先写死简版逻辑。实际可调一次快速 AI 请求。
        st.info(f"根据您的【{major}】背景，您在『系统集成』和『工程数字化』领域有极高潜能。")

    st.success("✨ 深度报告已就绪（内容超过 10 页，含详细路径设计）")

    # 模拟支付环节
    st.markdown("### 🔓 获取完整 10 页 PDF 报告")
    st.write("请扫码支付 **0.1 元** 咨询费，支付后即可激活下载。")
    st.image("https://via.placeholder.com/200x200.png?text=QR+CODE")  # 替换为你的真实收款码

    # 在实际运营中，这里需要支付回调。原型阶段我们直接提供生成按钮。
    if st.button("我已支付，立即生成 PDF 报告"):
        report_data = {}
        # 定义 6 个章节，每章生成 800-1000 字，加上排版即可达到 10 页以上
        sections = [
            "当前行业形势与轨道交通人才价值锚点",
            "基于个人项目经验的硬技能迁移性深度分析",
            "推荐转型方向一：低空经济与智慧交通融合",
            "推荐转型方向二：BIM/数字化转型顾问路径",
            "未来 3 年技能补齐路线图与学习清单",
            "简历去'土化'修改建议与面试突围策略"
        ]

        progress_bar = st.progress(0)
        for i, s_title in enumerate(sections):
            prompt = f"针对{major}专业，{years}年经验，项目经验：{exp}。请详细撰写：{s_title}。要求字数极多，语气专业。"
            res = client.chat.completions.create(model="deepseek-chat", messages=[{"role": "user", "content": prompt}])
            report_data[s_title] = res.choices[0].message.content
            progress_bar.progress((i + 1) / len(sections))

        pdf_bytes = generate_pdf(report_data)
        st.download_button(
            label="📥 下载 10 页深度评估报告 (PDF)",
            data=pdf_bytes,
            file_name=f"轨交转型报告_{major}.pdf",
            mime="application/pdf"
        )
