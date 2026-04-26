"""
広報活動 データ登録アプリ
Streamlit + Supabase
"""

import streamlit as st
from datetime import date

# ============================================================
# ページ設定
# ============================================================
st.set_page_config(
    page_title="広報活動 記録登録",
    page_icon="📋",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ============================================================
# カスタムCSS（スマホ対応）
# ============================================================
st.markdown("""
<style>
  html, body, [class*="css"] {
    font-family: 'Hiragino Sans', 'Noto Sans JP', sans-serif;
  }
  .block-container {
    padding: 1.5rem 1rem 3rem;
    max-width: 600px;
  }
  .stButton > button {
    width: 100%;
    height: 3.2rem;
    font-size: 1.05rem;
    font-weight: 700;
    border-radius: 12px;
    margin-top: 0.4rem;
  }
  .stTextInput > div > div > input,
  .stNumberInput > div > div > input,
  .stSelectbox > div > div > div,
  .stDateInput > div > div > input {
    font-size: 1rem;
    border-radius: 10px;
    padding: 0.55rem 0.8rem;
  }
  .app-title {
    text-align: center;
    padding: 1.2rem 0 0.4rem;
    font-size: 1.4rem;
    font-weight: 800;
    color: #1a472a;
    letter-spacing: 0.04em;
  }
  .app-subtitle {
    text-align: center;
    font-size: 0.85rem;
    color: #666;
    margin-bottom: 1.6rem;
  }
  .login-box {
    background: #f4faf6;
    border: 1.5px solid #2d6a4f;
    border-radius: 16px;
    padding: 2rem 1.5rem 1.5rem;
    margin: 2rem auto;
    max-width: 360px;
  }
  .success-card {
    background: #f0faf4;
    border: 1.5px solid #2d6a4f;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin: 0.8rem 0;
    font-size: 0.95rem;
    line-height: 1.8;
  }
  div[data-testid="stTabs"] button {
    font-size: 1rem;
    font-weight: 600;
  }
</style>
""", unsafe_allow_html=True)


# ============================================================
# Supabase クライアント初期化
# ============================================================
@st.cache_resource
def get_supabase():
    try:
        from supabase import create_client
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"DB接続エラー: {e}")
        return None


# ============================================================
# セッション状態の初期化
# ============================================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False


# ============================================================
# タイトル
# ============================================================
st.markdown('<div class="app-title">📋 広報活動 記録登録</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="app-subtitle">チラシ配布・街頭活動の記録をスマホから登録できます</div>',
    unsafe_allow_html=True
)


# ============================================================
# 合言葉認証
# ============================================================
PASSPHRASE = "nora"

if not st.session_state.authenticated:
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown("#### 🔑 合言葉を入力してください")
    st.caption("このアプリを利用するには合言葉が必要です。")

    with st.form("login_form"):
        entered = st.text_input(
            "合言葉",
            type="password",
            placeholder="合言葉を入力",
            label_visibility="collapsed",
        )
        login_btn = st.form_submit_button("確認する", type="primary")

    if login_btn:
        if entered == PASSPHRASE:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("合言葉が違います。もう一度お試しください。")

    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()


# ============================================================
# 認証後：メインコンテンツ
# ============================================================
supabase = get_supabase()

# 資料種別の選択肢
MATERIAL_TYPES = ["チラシA", "チラシB", "ポスター", "リーフレット", "その他"]

tab1, tab2 = st.tabs(["📌 定点配布の記録", "🏘 戸別配布の記録"])


# ============================================================
# タブ1: 定点配布（pr_points）
# ============================================================
with tab1:
    st.markdown("##### 定点配布活動（駅前・交差点など）の記録")

    with st.form("form_points", clear_on_submit=True):

        activity_date_p = st.date_input(
            "実施日",
            value=date.today(),
            key="date_p",
        )

        material_type_p = st.selectbox(
            "資料種別",
            options=MATERIAL_TYPES,
            key="mat_p",
        )

        quantity_p = st.number_input(
            "配布数量（部）",
            min_value=0,
            max_value=99999,
            step=1,
            value=0,
            key="qty_p",
        )

        pic_p = st.text_input(
            "担当者名",
            placeholder="例: 山田 太郎",
            key="pic_p",
        )

        submitted_p = st.form_submit_button("📌 定点配布を登録する", type="primary")

    if submitted_p:
        errors = []
        if not pic_p.strip():
            errors.append("担当者名を入力してください。")
        if quantity_p <= 0:
            errors.append("配布数量は1以上を入力してください。")

        if errors:
            for err in errors:
                st.warning(err)
        elif supabase is None:
            st.error("データベースに接続できません。管理者にお問い合わせください。")
        else:
            payload = {
                "ActivityDate": activity_date_p.isoformat(),
                "MaterialType": material_type_p,
                "Quantity":     int(quantity_p),
                "PIC":          pic_p.strip(),
            }
            try:
                res = supabase.table("pr_points").insert(payload).execute()
                if res.data:
                    st.success("✅ 定点配布の記録を登録しました！")
                    st.markdown(
                        f'<div class="success-card">'
                        f'<b>実施日:</b> {activity_date_p.strftime("%Y年%m月%d日")}<br>'
                        f'<b>資料種別:</b> {material_type_p}<br>'
                        f'<b>配布数量:</b> {quantity_p:,} 部<br>'
                        f'<b>担当者名:</b> {pic_p.strip()}'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.error("登録に失敗しました。内容を確認して再度お試しください。")
            except Exception as e:
                st.error(f"登録中にエラーが発生しました: {e}")


# ============================================================
# タブ2: 戸別配布（pr_areas）
# ============================================================
with tab2:
    st.markdown("##### 戸別配布活動（住宅街・団地など）の記録")

    with st.form("form_areas", clear_on_submit=True):

        activity_date_a = st.date_input(
            "実施日",
            value=date.today(),
            key="date_a",
        )

        material_type_a = st.selectbox(
            "資料種別",
            options=MATERIAL_TYPES,
            key="mat_a",
        )

        quantity_a = st.number_input(
            "配布数量（部）",
            min_value=0,
            max_value=99999,
            step=1,
            value=0,
            key="qty_a",
        )

        pic_a = st.text_input(
            "担当者名",
            placeholder="例: 鈴木 花子",
            key="pic_a",
        )

        submitted_a = st.form_submit_button("🏘 戸別配布を登録する", type="primary")

    if submitted_a:
        errors = []
        if not pic_a.strip():
            errors.append("担当者名を入力してください。")
        if quantity_a <= 0:
            errors.append("配布数量は1以上を入力してください。")

        if errors:
            for err in errors:
                st.warning(err)
        elif supabase is None:
            st.error("データベースに接続できません。管理者にお問い合わせください。")
        else:
            payload = {
                "ActivityDate": activity_date_a.isoformat(),
                "MaterialType": material_type_a,
                "Quantity":     int(quantity_a),
                "PIC":          pic_a.strip(),
            }
            try:
                res = supabase.table("pr_areas").insert(payload).execute()
                if res.data:
                    st.success("✅ 戸別配布の記録を登録しました！")
                    st.markdown(
                        f'<div class="success-card">'
                        f'<b>実施日:</b> {activity_date_a.strftime("%Y年%m月%d日")}<br>'
                        f'<b>資料種別:</b> {material_type_a}<br>'
                        f'<b>配布数量:</b> {quantity_a:,} 部<br>'
                        f'<b>担当者名:</b> {pic_a.strip()}'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.error("登録に失敗しました。内容を確認して再度お試しください。")
            except Exception as e:
                st.error(f"登録中にエラーが発生しました: {e}")


# ============================================================
# フッター：ログアウト
# ============================================================
st.divider()
col1, col2, col3 = st.columns([2, 1, 2])
with col2:
    if st.button("ログアウト"):
        st.session_state.authenticated = False
        st.rerun()
