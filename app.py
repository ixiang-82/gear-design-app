import math
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
import streamlit as st

# 設定網頁版面
st.set_page_config(
    page_title="機械元件設計 - 齒輪設計與分析系統", layout="wide"
)

st.title("⚙️ 齒輪幾何設計、運動與動力分析完整系統")
st.markdown("---")


# ==================== 0. 定義預設值與 Session State 初始化 (對應題目照片條件) ====================
default_values = {
    "pressure_angle": 14.5,
    "module": 5.0,
    "gear_type": "全齒制",
    "n1": 32,
    "n2": 48,
    "center_distance": 200.0,
    "gear_ratio": 1.5,
    "rpm_in": 1200.0,
    "b_width": 30.0,
    "power_kw": 25.0,
    "spring_const_mode": "標準值 (Standard)",
    "custom_spring_k": 1e6,
    "e1": 207000.0,
    "e2": 207000.0,
    "agma_q": 10,
    "shape_e": 0.00130,
    "gamma_1": 7850.0,
    "rim_d1": 0.0,
    "gamma_2": 7850.0,
    "rim_d2": 0.0,
    "lewis_y": 0.104,
    "bhn_val": 200,
}

for key, val in default_values.items():
  if key not in st.session_state:
    st.session_state[key] = val


# ==================== 0-1. 定義大螢幕彈出視窗 (st.dialog) ====================
@st.dialog("📋 AGMA 形狀誤差 e 值完整查表 (表 10-2)", width="large")
def show_agma_dialog():
  st.markdown("##### 輪齒與輪齒之間的總間隙及形狀誤差 $e$ (單位: 吋/mm)")
  agma_lookup_data = {
      "AGMA 品質號碼": [8, 9, 10, 11, 12],
      "節徑 38mm (1.5 in)": [
          "0.0017 in",
          "0.0016 in",
          "0.0012 in",
          "0.0008 in",
          "0.0006 in",
      ],
      "節徑 75mm (3 in)": [
          "0.0018 in",
          "0.0017 in",
          "0.0012 in",
          "0.0009 in",
          "0.0006 in",
      ],
      "節徑 150mm (6 in)": [
          "0.0019 in",
          "0.0018 in",
          "0.0012 in",
          "0.0009 in",
          "0.0007 in",
      ],
      "節徑 300mm (12 in)": [
          "0.0020 in",
          "0.0019 in",
          "0.0013 in",
          "0.0010 in",
          "0.0007 in",
      ],
      "節徑 600mm (24 in)": [
          "0.0022 in",
          "0.0021 in",
          "0.0014 in",
          "0.0011 in",
          "0.0008 in",
      ],
  }
  st.dataframe(agma_lookup_data, use_container_width=True)
  st.info(
      "💡 工程提示：精度等級越高（如 11~12 級），形狀誤差 $e$ 越小，動態衝擊負荷也越低。"
  )


@st.dialog("📋 路易士係數 Y 值完整查表 (表 10-3)", width="large")
def show_lewis_dialog():
  st.markdown("##### 齒頂承受負荷之正齒輪的齒形係數或路易士係數 Y")
  lewis_lookup_data = {
      "齒數 N": [
          10,
          12,
          14,
          15,
          16,
          17,
          18,
          19,
          20,
          21,
          22,
          24,
          26,
          28,
          30,
          34,
          38,
          43,
          50,
          60,
          75,
          100,
          150,
          300,
          "Rack (齒條)",
      ],
      "14.5° 全高制": [
          0.056,
          0.067,
          0.075,
          0.078,
          0.081,
          0.083,
          0.086,
          0.088,
          0.090,
          0.092,
          0.094,
          0.097,
          0.099,
          0.100,
          0.101,
          0.104,
          0.105,
          0.106,
          0.110,
          0.113,
          0.115,
          0.117,
          0.120,
          0.122,
          0.124,
      ],
      "20° 全高制": [
          0.064,
          0.078,
          0.088,
          0.090,
          0.094,
          0.096,
          0.098,
          0.100,
          0.102,
          0.103,
          0.104,
          0.108,
          0.110,
          0.112,
          0.114,
          0.118,
          0.120,
          0.122,
          0.130,
          0.135,
          0.138,
          0.142,
          0.147,
          0.151,
          0.154,
      ],
      "20° 短齒制": [
          0.083,
          0.099,
          0.108,
          0.111,
          0.115,
          0.117,
          0.120,
          0.122,
          0.123,
          0.125,
          0.127,
          0.133,
          0.135,
          0.137,
          0.139,
          0.142,
          0.144,
          0.145,
          0.151,
          0.155,
          0.158,
          0.161,
          0.168,
          0.172,
          0.175,
      ],
  }
  st.dataframe(lewis_lookup_data, use_container_width=True)
  st.info(
      "💡 工程提示：Y 值與齒數及壓力角直接相關，齒數越多或壓力角越大，Y 值越高，抗彎曲能力越強。"
  )


@st.dialog(
    "📋 常見機械材料特性與 BHN / K 值 / 彈性係數總表", width="large"
)
def show_material_dialog():
  st.markdown(
      "##### 不同材料之彈性係數 E、布氏硬度 BHN、容許應力與 Wear 壓力 K"
      " 值對照"
  )
  material_table = {
      "材料名稱與代號": [
          "碳鋼 (S45C 調質)",
          "合金鋼 (SNCM439)",
          "合金鋼 (SCM440 滲碳淬火)",
          "灰鑄鐵 (FC250)",
          "球狀石墨鑄鐵 (FCD600)",
          "磷青銅 (PB2)",
      ],
      "彈性係數 E (MPa)": [
          207000,
          210000,
          210000,
          118000,
          174000,
          110000,
      ],
      "布氏硬度 BHN": [220, 280, 550, 200, 260, 120],
      "容許彎曲應力 σ (MPa)": [195, 260, 480, 105, 220, 90],
      "Wear 壓力 K 值": [0.42, 0.65, 1.45, 0.38, 0.58, 0.20],
      "適用情境與說明": [
          "一般工業機械變速箱",
          "高負載、高強度動力傳動",
          "航太與重負荷極限齒輪",
          "一般低速、低載荷機械",
          "耐磨耗、抗衝擊齒輪",
          "耐腐蝕、低摩擦減速機構",
      ],
  }
  st.dataframe(material_table, use_container_width=True)
  st.info(
      "💡 工程提示：不同材料的彈性係數 E 與硬度 BHN 會直接影響齒輪的接觸變形量、磨耗負荷 Fw 與容許彎曲應力。"
  )


# ==================== 1. 側邊欄：自由輸入區 (綁定 Session State) ====================
st.sidebar.header("📍 設計條件自由輸入區")

st.sidebar.subheader("一、 齒輪幾何與尺寸參數輸入")
pressure_angle = st.sidebar.number_input(
    "壓力角 $\psi$ (度)",
    value=st.session_state.pressure_angle,
    step=0.5,
    format="%.1f",
    key="pressure_angle",
)
module = st.sidebar.number_input(
    "模數 M",
    value=st.session_state.module,
    step=0.5,
    format="%.1f",
    key="module",
)
gear_type = st.sidebar.selectbox(
    "齒形製程", ["全齒制", "短齒制"], key="gear_type"
)

n1 = st.sidebar.number_input(
    "主動件齒數 $N_1$ (齒)",
    value=st.session_state.n1,
    step=1,
    key="n1",
)
n2 = st.sidebar.number_input(
    "從動件齒數 $N_2$ (齒)",
    value=st.session_state.n2,
    step=1,
    key="n2",
)

auto_center_distance = (module * (n1 + n2)) / 2
center_distance = st.sidebar.number_input(
    "中心距 C (mm)",
    value=float(auto_center_distance),
    step=1.0,
    format="%.2f",
    key="center_distance",
)

auto_gear_ratio = n2 / n1 if n1 > 0 else 1.0
gear_ratio = st.sidebar.number_input(
    "減速比 $r_i$",
    value=float(auto_gear_ratio),
    step=0.01,
    format="%.3f",
    key="gear_ratio",
)

# ----------------- 二、 動力分析輸入 -----------------
st.sidebar.subheader("二、 動力分析輸入條件")
rpm_in = st.sidebar.number_input(
    "轉速 (rpm)", value=st.session_state.rpm_in, step=50.0, key="rpm_in"
)
b_width = st.sidebar.number_input(
    "齒面寬 (mm)",
    value=st.session_state.b_width,
    step=0.1,
    format="%.3f",
    key="b_width",
)
power_kw = st.sidebar.number_input(
    "傳遞動力 (kW)", value=st.session_state.power_kw, step=1.0, key="power_kw"
)

spring_const_mode = st.sidebar.selectbox(
    "嚙合齒輪彈簧常數",
    ["標準值 (Standard)", "自訂值"],
    key="spring_const_mode",
)
if spring_const_mode == "自訂值":
  custom_spring_k = st.sidebar.number_input(
      "自訂彈簧常數值 K (N/mm)",
      value=st.session_state.custom_spring_k,
      step=1e4,
      key="custom_spring_k",
  )

c_col1, c_col2 = st.sidebar.columns(2)
with c_col1:
  e1 = st.number_input(
      "E1 (小齒輪彈性係數)",
      value=st.session_state.e1,
      step=1000.0,
      key="e1",
  )
with c_col2:
  e2 = st.number_input(
      "E2 (大齒輪彈性係數)",
      value=st.session_state.e2,
      step=1000.0,
      key="e2",
  )

# AGMA 品質號碼與大視窗查詢按鈕
agma_col1, agma_col2 = st.sidebar.columns([3, 2])
with agma_col1:
  agma_q = st.selectbox("AGMA 品質號碼", [8, 9, 10, 11, 12], index=2, key="agma_q")
with agma_col2:
  st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)
  if st.button("查e值表"):
    show_agma_dialog()

shape_e = st.sidebar.number_input(
    "形狀誤差 e (in/mm)",
    value=st.session_state.shape_e,
    format="%.5f",
    key="shape_e",
)

st.sidebar.markdown("---")
st.sidebar.markdown("**⚙️ 齒輪 1 與 齒輪 2 附加性質**")
g1_col1, g1_col2 = st.sidebar.columns(2)
with g1_col1:
  gamma_1 = st.number_input(
      "單位體積重量 γ1",
      value=st.session_state.gamma_1,
      step=10.0,
      key="gamma_1",
  )
with g1_col2:
  rim_d1 = st.number_input(
      "輪緣內徑1 (實心0)",
      value=st.session_state.rim_d1,
      step=5.0,
      key="rim_d1",
  )

g2_col1, g2_col2 = st.sidebar.columns(2)
with g2_col1:
  gamma_2 = st.number_input(
      "單位體積重量 γ2",
      value=st.session_state.gamma_2,
      step=10.0,
      key="gamma_2",
  )
with g2_col2:
  rim_d2 = st.number_input(
      "輪緣內徑2 (實心0)",
      value=st.session_state.rim_d2,
      step=5.0,
      key="rim_d2",
  )

# 路易士係數 Y 與大視窗查詢按鈕
y_col1, y_col2 = st.sidebar.columns([3, 2])
with y_col1:
  lewis_y = st.number_input(
      "路易士係數 Y",
      value=st.session_state.lewis_y,
      format="%.3f",
      key="lewis_y",
  )
with y_col2:
  st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)
  if st.button("查Y值表"):
    show_lewis_dialog()

# BHN 硬度與材料總表大視窗查詢按鈕
bhn_col1, bhn_col2 = st.sidebar.columns([3, 2])
with bhn_col1:
  bhn_val = st.slider(
      "材料布氏硬度 K (BHN)",
      150,
      350,
      value=st.session_state.bhn_val,
      step=10,
      key="bhn_val",
  )
with bhn_col2:
  st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)
  if st.button("查K值表"):
    show_material_dialog()


# ==================== 2. 核心計算邏輯 ====================
d1 = module * n1  # 小齒輪節圓直徑
d2 = module * n2  # 大齒輪節圓直徑
r1 = d1 / 2
r2 = d2 / 2

# 齒冠、齒根高與直徑
addendum = 1.0 * module if gear_type == "全齒制" else 0.8 * module
dedendum = 1.25 * module if gear_type == "全齒制" else 1.0 * module
da1 = d1 + 2 * addendum
da2 = d2 + 2 * addendum
df1 = d1 - 2 * dedendum
df2 = d2 - 2 * dedendum

# 基圓直徑
psi_rad = math.radians(pressure_angle)
rb1 = r1 * math.cos(psi_rad)
rb2 = r2 * math.cos(psi_rad)

# 運動分析
rpm_out = rpm_in / gear_ratio if gear_ratio > 0 else 0
v_vel = (math.pi * d1 * rpm_in) / 60000  # 切線速度 (m/s)

# 動力分析計算
ft_force = (power_kw * 1000) / v_vel if v_vel > 0 else 0  # 切線力 Ft (N)
fr_force = ft_force * math.tan(psi_rad)  # 徑向力 Fr (N)

torque_kgcm = (9550 * power_kw / rpm_in) * 10.1972 if rpm_in > 0 else 0  # 驅動扭矩 (kg-cm)
r1_cm = r1 / 10  # 小齒輪半徑 (cm)
fp_kg = torque_kgcm / r1_cm if r1_cm > 0 else 0  # 傳遞力 Fp (kg)
required_power_kw = power_kw / 0.95  # 所需動力 (kW)

# 材料容許應力與 K 值計算
allowed_sigma = 0.0031 * (bhn_val**2) - 0.9973 * bhn_val + 216.79
current_k = 2e-05 * (bhn_val**2) - 0.0059 * bhn_val + 0.7761
fw_load = d1 * b_width * current_k  # 磨耗負荷 Fw (N)

# 相當質量 Me 計算
vol_1 = math.pi * ((r1**2) - (rim_d1 / 2) ** 2) * b_width
vol_2 = math.pi * ((r2**2) - (rim_d2 / 2) ** 2) * b_width
mass_1 = vol_1 * (gamma_1 / 1e9)
mass_2 = vol_2 * (gamma_2 / 1e9)
equivalent_mass_me = mass_1 + mass_2 * ((n1 / n2) ** 2)

# 嚙合齒度 K
mesh_k = (
    custom_spring_k
    if (spring_const_mode == "自訂值" and "custom_spring_k" in locals())
    else (1.4e7 * b_width)
)

# 動態負荷 Fd 計算
error_factor = shape_e * 25.4 * 1000 if shape_e < 0.01 else shape_e
dynamic_load_fd = ft_force + (
    0.16 * v_vel * (error_factor * b_width + ft_force)
) / (0.16 * v_vel + math.sqrt(max(1, error_factor * b_width + ft_force)))

# 彎曲負荷 Fb
fb_load = allowed_sigma * b_width * module * lewis_y

# 幾何限制與研判計算
limit_R2 = math.sqrt(rb2**2 + (center_distance**2) * (math.sin(psi_rad) ** 2))
pass_R2 = (da2 / 2) <= limit_R2
status_r2_str = "OK" if pass_R2 else "FAIL"

limit_r1 = math.sqrt(rb1**2 + (center_distance**2) * (math.sin(psi_rad) ** 2))
pass_r1 = (da1 / 2) <= limit_r1
status_r1_str = "OK" if pass_r1 else "FAIL"

min_teeth_limit = 32 if pressure_angle <= 14.5 else 18
min_teeth_ok = n1 >= min_teeth_limit
min_teeth_str = "OK" if min_teeth_ok else "FAIL"

ra1, ra2 = da1 / 2, da2 / 2
term1 = math.sqrt(max(0, ra1**2 - rb1**2))
term2 = math.sqrt(max(0, ra2**2 - rb2**2))
contact_ratio = (
    (term1 + term2 - center_distance * math.sin(psi_rad))
    / (math.pi * module * math.cos(psi_rad))
    if (math.pi * module * math.cos(psi_rad)) > 0
    else 0
)
cr_status = (
    "適合" if (1.2 <= contact_ratio <= 2.0) else ("過大" if contact_ratio > 2.0 else "過小")
)


# ==================== 輔助函式：建立美化卡片 ====================
def render_card(label, val, unit=""):
  st.markdown(
      f"""
    <div style="
        background-color: #1e1e1e; 
        padding: 14px 16px; 
        border-radius: 8px; 
        border: 1px solid #333333;
        margin-bottom: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    ">
        <div style="color: #ffffff; font-size: 0.9rem; margin-bottom: 6px;">{label}</div>
        <div>
            <span style="color: #58a6ff; font-size: 1.4rem; font-weight: bold;">{val}</span>
            <span style="color: #ffffff; font-size: 0.9rem; margin-left: 6px;">{unit}</span>
        </div>
    </div>
    """,
      unsafe_allow_html=True,
  )


# ==================== 3. 畫面呈現 ====================

# Ⅰ. 齒輪尺寸輸出
st.subheader("⚙️ Ⅰ. 齒輪尺寸輸出")
c1, c2, c3, c4 = st.columns(4)
with c1:
  render_card("小齒輪齒數 N1", f"{n1}", "齒")
with c2:
  render_card("大齒輪齒數 N2", f"{n2}", "齒")
with c3:
  render_card("模數 M", f"{module:.1f}", "")
with c4:
  render_card("壓力角 ψ", f"{pressure_angle:.1f}", "°")

c5, c6, c7, c8 = st.columns(4)
with c5:
  render_card("小齒節圓直徑 D1", f"{d1:.2f}", "mm")
with c6:
  render_card("大齒節圓直徑 D2", f"{d2:.2f}", "mm")
with c7:
  render_card("小齒冠圓直徑 Da1", f"{da1:.2f}", "mm")
with c8:
  render_card("大齒冠圓直徑 Da2", f"{da2:.2f}", "mm")

c9, c10, c11, c12 = st.columns(4)
with c9:
  render_card("小齒根圓直徑 Df1", f"{df1:.2f}", "mm")
with c10:
  render_card("大齒根圓直徑 Df2", f"{df2:.2f}", "mm")
with c11:
  render_card("中心距 C", f"{center_distance:.2f}", "mm")
with c12:
  render_card("齒面寬 b", f"{b_width:.3f}", "mm")

# (2) 幾何限制條件與研判
col_chk1, col_chk2 = st.columns(2)
with col_chk1:
  st.subheader("🔸 通過研判")
  r2_color = "#28a745" if pass_R2 else "#dc3545"
  st.markdown(
      f"**大齒冠圓半徑 $R$** $\\le \\sqrt{{R_b^2 + C^2\\sin^2\\psi}}$ ="
      f" <span style='font-size: 1.25rem; font-weight: bold; color:"
      f" #58a6ff;'>{limit_R2:.2f}</span> ➔ <span style='font-size: 1.25rem;"
      f" font-weight: bold; color: {r2_color};'>{status_r2_str}</span>",
      unsafe_allow_html=True,
  )

  r1_color = "#28a745" if pass_r1 else "#dc3545"
  st.markdown(
      f"**小齒冠圓半徑 $r$** $\\le \\sqrt{{r_b^2 + C^2\\sin^2\\psi}}$ ="
      f" <span style='font-size: 1.25rem; font-weight: bold; color:"
      f" #58a6ff;'>{limit_r1:.2f}</span> ➔ <span style='font-size: 1.25rem;"
      f" font-weight: bold; color: {r1_color};'>{status_r1_str}</span>",
      unsafe_allow_html=True,
  )

with col_chk2:
  st.subheader("🔸 干涉")
  mt_color = "#28a745" if min_teeth_ok else "#dc3545"
  st.markdown(
      f"**最小齒數限制** (標準 $\\ge$ {min_teeth_limit})： "
      f"<span style='font-size: 1.25rem; font-weight: bold; color: #58a6ff;"
      f" background-color: #262730; padding: 2px 6px; border-radius:"
      f" 4px;'>N1 = {n1}</span> ➔ <span style='font-size: 1.25rem; font-weight:"
      f" bold; color: {mt_color};'>{min_teeth_str}</span>",
      unsafe_allow_html=True,
  )

  cr_color = (
      "#28a745"
      if cr_status == "適合"
      else ("#ffc107" if cr_status == "過大" else "#dc3545")
  )
  st.markdown(
      f"**接觸齒對數**： <span style='font-size: 1.25rem; font-weight: bold;"
      f" color: #58a6ff;'>{contact_ratio:.2f}</span> ➔ <span"
      f" style='font-size: 1.25rem; font-weight: bold; color:"
      f" {cr_color};'>{cr_status}</span>",
      unsafe_allow_html=True,
  )

# 齒型顯示
st.subheader("🔸 齒型")
st.info(f"目前選定之齒型製程：**{gear_type}**（壓力角: {pressure_angle}°）")

st.markdown(
    """
<div style="background-color: #161616; padding: 14px 18px; border-radius: 8px; border: 1px solid #2c2c2c; margin-top: 8px; margin-bottom: 20px;">
    <div style="color: #c7c7c7; font-size: 0.9rem; font-weight: 400; margin-bottom: 8px;">💡 判定標準與參數規範說明：</div>
    <ul style="color: #9e9e9e; font-size: 0.82rem; font-weight: 300; line-height: 1.6; margin: 0; padding-left: 18px;">
        <li><b>大/小齒冠圓半徑</b>：實際半徑小於等於安全極限時顯示 <span style='color: #28a745;'><b>OK</b></span>；若大於則顯示 <span style='color: #dc3545;'><b>FAIL</b></span>（代表冠圓過大，運轉時會產生干涉）。</li>
        <li><b>最小齒數限制</b>：壓力角 14.5度時標準需大於等於 32 齒；壓力角 20度時標準需大於等於 18 齒。主動輪達標顯示 <span style='color: #28a745;'><b>OK</b></span>，不足則顯示 <span style='color: #dc3545;'><b>FAIL</b></span>（會發生齒根根切）。</li>
        <li><b>接觸齒對數</b>：理想適合範圍為 <b>1.2 至 2.0 之間</b>。大於 2.0 顯示 <span style='color: #ffc107;'><b>過大</b></span>（平穩但滑動磨耗增加），小於 1.2 顯示 <span style='color: #dc3545;'><b>過小</b></span>（會產生衝擊與噪音）。</li>
    </ul>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown("---")

# ==================== (3) 運動分析輸出 ====================
st.subheader("🚀 Ⅱ. 運動分析輸出")
m1, m2, m3, m4 = st.columns(4)
with m1:
  render_card("主動輪轉速", f"{rpm_in:.1f}", "rpm")
with m2:
  render_card("輸出輪轉速", f"{rpm_out:.2f}", "rpm")
with m3:
  render_card("減速比 ri", f"{gear_ratio:.3f}", "")
with m4:
  render_card("切線速度 V", f"{v_vel:.2f}", "m/s")

# ----------------- 📋 運動分析詳細計算依據與公式說明卡片 -----------------
motion_basis_html = f"""
<div style="background-color: #161616; padding: 16px 20px; border-radius: 8px; border: 1px solid #2c2c2c; margin-top: 15px; margin-bottom: 25px;">
    <div style="color: #c7c7c7; font-size: 0.9rem; font-weight: 400; margin-bottom: 8px;">💡 運動分析詳細計算依據與工程公式說明 (Kinematics Calculation Basis)：</div>
    <ul style="color: #9e9e9e; font-size: 0.82rem; font-weight: 300; line-height: 1.6; margin: 0; padding-left: 18px;">
        <li><b>減速比 rᵢ</b>：公式 rᵢ = N₂ / N₁ ➔ 計算代入：{n2} / {n1} = <b>{gear_ratio:.3f}</b>。</li>
        <li><b>輸出輪轉速 (n₂)</b>：公式 n₂ = n₁ / rᵢ ➔ 計算代入：{rpm_in:.1f} / {gear_ratio:.3f} = <b>{rpm_out:.2f} rpm</b>。</li>
        <li><b>切線速度 V (m/s)</b>：公式 V = (π · d₁ · n₁) / 60000 ➔ 計算代入：(π · {d1:.2f} · {rpm_in:.1f}) / 60000 = <b>{v_vel:.2f} m/s</b>。</li>
        <li><b>運動學物理意義</b>：決定齒輪傳動時的速度轉換關係與周邊線速度，切線速度過高時需注意動態衝擊與潤滑條件。</li>
    </ul>
</div>
"""
st.markdown(motion_basis_html, unsafe_allow_html=True)

st.markdown("---")
st.subheader("⚡ Ⅲ. 動力分析輸出")

# 🔹 磨耗分析
st.markdown("##### 🔹 磨耗分析 (Wear Analysis)")
wa1, wa2, wa3, wa4 = st.columns(4)
with wa1:
  render_card("齒面寬 b", f"{b_width:.3f}", "mm")
with wa2:
  render_card("磨耗負荷 Fw", f"{fw_load:.2f}", "N")
with wa3:
  render_card("傳遞動力", f"{power_kw:.2f}", "kW")
with wa4:
  render_card("布氏硬度 BHN", f"{bhn_val}", "")

# 🔹 傳動分析
st.markdown("##### 🔹 傳動分析 (Transmission Analysis)")
ta1, ta2, ta3, ta4 = st.columns(4)
with ta1:
  render_card("傳遞力 Fp", f"{fp_kg:.2f}", "kg")
with ta2:
  render_card("驅動扭矩", f"{torque_kgcm:.2f}", "kg-cm")
with ta3:
  render_card("所需動力", f"{required_power_kw:.2f}", "kW")
with ta4:
  render_card("傳遞動力", f"{power_kw:.2f}", "kW")

# 🔹 力學與動態負荷分析
st.markdown("##### 🔹 力學與動態負荷分析 (Forces & Dynamic Analysis)")
fo1, fo2, fo3, fo4 = st.columns(4)
with fo1:
  render_card("切線力 Ft", f"{ft_force:.2f}", "N")
with fo2:
  render_card("徑向力 Fr", f"{fr_force:.2f}", "N")
with fo3:
  render_card("動態負荷 Fd", f"{dynamic_load_fd:.2f}", "N")
with fo4:
  render_card("相當質量 Me", f"{equivalent_mass_me:.4f}", "N-sec^2/mm")

# 🔹 彎曲分析
st.markdown("##### 🔹 彎曲分析 (Bending Analysis)")
ba1, ba2, ba3, ba4 = st.columns(4)
with ba1:
  render_card("容許彎曲應力 σ", f"{allowed_sigma:.2f}", "MPa")
with ba2:
  render_card("彎曲負荷 Fb", f"{fb_load:.2f}", "N")
with ba3:
  render_card("路易士係數 Y", f"{lewis_y:.3f}", "")
with ba4:
  render_card("模數 M", f"{module:.1f}", "")

# ----------------- 📋 動力詳細計算依據與標準來源區塊 -----------------
calc_basis_html = f"""
<div style="background-color: #161616; padding: 16px 20px; border-radius: 8px; border: 1px solid #2c2c2c; margin-top: 15px; margin-bottom: 25px;">
    <div style="color: #c7c7c7; font-size: 0.9rem; font-weight: 400; margin-bottom: 8px;">💡 詳細計算依據、工程公式來源與判定標準 (Calculation Basis)：</div>
    <ul style="color: #9e9e9e; font-size: 0.82rem; font-weight: 300; line-height: 1.6; margin: 0; padding-left: 18px;">
        <li><b>標準與公式來源</b>：齒輪彎曲強度與齒形係數採用 <b>Lewis 方程式</b> 與 <b>AGMA 標準規範</b>；材料性質擬合依據機械工程設計手冊（Shigley's）；動態負荷採用 <b>Buckingham 方程式</b>。</li>
        <li><b>切線速度 V (m/s)</b>：公式 V = (π · d₁ · n₁) / 60000 ➔ 計算代入：(π · {d1:.2f} · {rpm_in:.1f}) / 60000 = <b>{v_vel:.2f} m/s</b>。</li>
        <li><b>切線力 Ft 與徑向力 Fr (N)</b>：Ft = (P · 1000) / V = <b>{ft_force:.2f} N</b>；徑向力 Fr = Ft · tan(ψ) = <b>{fr_force:.2f} N</b>。</li>
        <li><b>容許彎曲應力 σ (MPa)</b> [BHN = {bhn_val}]：經驗擬合公式 σ = 0.0031 · BHN² - 0.9973 · BHN + 216.79 = <b>{allowed_sigma:.2f} MPa</b>。</li>
        <li><b>路易士彎曲負荷 Fb (N)</b>：公式 Fb = σ · b · m · Y = {allowed_sigma:.2f} · {b_width:.3f} · {module:.1f} · {lewis_y:.3f} = <b>{fb_load:.2f} N</b>。</li>
        <li><b>表面磨耗負荷 Fw (N)</b> [目前 K = {current_k:.3f}]：K = 2×10⁻⁵·BHN² - 0.0059·BHN + 0.7761；磨耗負荷 Fw = d₁ · b · K = <b>{fw_load:.2f} N</b>。</li>
        <li><b>工程判定標準</b>：容許彎曲負荷 Fb 需大於動態負荷 Fd；表面磨耗負荷 Fw 需大於切線力 Ft，且幾何干涉與齒數需符合規範。</li>
    </ul>
</div>
"""
st.markdown(calc_basis_html, unsafe_allow_html=True)

st.markdown("---")

# ==================== 5. 動態工程特性曲線圖 (含完整軸名、單位、物理意義與懸停) ====================
st.subheader("📊 IV. 動態工程特性曲線圖")

col_fig1, col_fig2 = st.columns(2)

bhn_arr = np.linspace(150, 350, 100)
stress_arr = 0.0031 * (bhn_arr**2) - 0.9973 * bhn_arr + 216.79
k_arr = 2e-05 * (bhn_arr**2) - 0.0059 * bhn_arr + 0.7761

with col_fig1:
  fig1 = go.Figure()
  fig1.add_trace(
      go.Scatter(
          x=bhn_arr,
          y=stress_arr,
          mode="lines",
          name="鋼材容許彎曲應力極限曲線",
          line=dict(color="#1f77b4", width=2.5),
          hovertemplate=(
              "<b>物理意義</b>: 決定齒根抗斷裂與承受反覆彎曲載荷之極限<br><b>布氏硬度"
              " BHN</b>: %{x}<br><b>容許彎曲應力 σ</b>: %{y:.1f}"
              " MPa<extra></extra>"
          ),
      )
  )
  fig1.add_trace(
      go.Scatter(
          x=[bhn_val],
          y=[allowed_sigma],
          mode="markers+text",
          name=f"目前設計點 (BHN={bhn_val})",
          text=[f"  目前設計點: σ={allowed_sigma:.1f} MPa"],
          textposition="top right",
          marker=dict(color="crimson", size=14),
          hovertemplate=(
              "<b>目前設計點</b><br>BHN: %{x}<br>容許應力: %{y:.1f}"
              " MPa<br><b>安全界線關係</b>: 當前容許應力需大於動態工作應力方為安全<extra></extra>"
          ),
      )
  )
  fig1.update_layout(
      title=dict(
          text=(
              "<b>y = 0.0031·BHN² - 0.9973·BHN + 216.79</b><br><span"
              " style='font-size: 14px; color: #ffffff;'>圖一：布氏硬度 BHN"
              " 與容許彎曲應力 σ 關係圖</span>"
          ),
          font=dict(size=13, color="#58a6ff"),
      ),
      xaxis_title="材料布氏硬度 BHN (無因次)",
      yaxis_title="容許彎曲應力 σ (MPa)",
      template="plotly_dark",
      height=400,
      margin=dict(l=40, r=20, t=65, b=30),
      xaxis=dict(
          showgrid=True,
          gridcolor="#333333",
          gridwidth=1,
          zeroline=True,
          zerolinecolor="#444444",
          dtick=50,
      ),
      yaxis=dict(
          showgrid=True,
          gridcolor="#333333",
          gridwidth=1,
          zeroline=True,
          zerolinecolor="#444444",
      ),
  )
  st.plotly_chart(fig1, use_container_width=True)
  st.caption(
      "📌 **圖一說明**：此曲線代表不同硬度鋼材的**齒根抗彎曲疲勞極限安全界線**。目前設計點（紅點）落在安全曲線上方或對應足夠強度即代表齒根結構安全。"
  )

with col_fig2:
  fig2 = go.Figure()
  fig2.add_trace(
      go.Scatter(
          x=bhn_arr,
          y=k_arr,
          mode="lines",
          name="Wear 壓力係數極限曲線",
          line=dict(color="#2ca02c", width=2.5),
          hovertemplate=(
              "<b>物理意義</b>: 決定齒面抗磨損、抗膠合與表面接觸疲勞壽命<br><b>布氏硬度"
              " BHN</b>: %{x}<br><b>Wear 壓力 K 值</b>: %{y:.3f}"
              " (N/mm²)<extra></extra>"
          ),
      )
  )
  fig2.add_trace(
      go.Scatter(
          x=[bhn_val],
          y=[current_k],
          mode="markers+text",
          name=f"目前設計點 (K={current_k:.3f})",
          text=[f"  目前設計點: K={current_k:.3f}"],
          textposition="top right",
          marker=dict(color="darkorange", size=14),
          hovertemplate=(
              "<b>目前設計點</b><br>BHN: %{x}<br>K 值: %{y:.3f}<br><b>安全界線關係</b>:"
              " 決定磨耗負荷 Fw 之大小基準<extra></extra>"
          ),
      )
  )
  fig2.update_layout(
      title=dict(
          text=(
              "<b>y = 2E-05·BHN² - 0.0059·BHN + 0.7761</b><br><span"
              " style='font-size: 14px; color: #ffffff;'>圖二：Wear 壓力 K"
              " 值與 BHN 關係圖</span>"
          ),
          font=dict(size=13, color="#2ca02c"),
      ),
      xaxis_title="材料布氏硬度 BHN (無因次)",
      yaxis_title="Wear 壓力 K 值 (N/mm²)",
      template="plotly_dark",
      height=400,
      margin=dict(l=40, r=20, t=65, b=30),
      xaxis=dict(
          showgrid=True,
          gridcolor="#333333",
          gridwidth=1,
          zeroline=True,
          zerolinecolor="#444444",
          dtick=50,
      ),
      yaxis=dict(
          showgrid=True,
          gridcolor="#333333",
          gridwidth=1,
          zeroline=True,
          zerolinecolor="#444444",
      ),
  )
  st.plotly_chart(fig2, use_container_width=True)
  st.caption(
      "📌 **圖二說明**：此曲線代表齒面承受接觸應力的**磨耗壽命安全界線**。硬度越高，$K$ 值越大，代表齒面越能抵抗表面磨耗與膠合破壞。"
  )
