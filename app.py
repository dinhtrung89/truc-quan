import streamlit as st
import pandas as pd

# Fix for pandas_datareader and pandas >= 3.0 missing deprecate_kwarg
try:
    from pandas.util._decorators import deprecate_kwarg
except ImportError:
    def deprecate_kwarg(old_arg_name, new_arg_name, mapping=None, stacklevel=2):
        def _deprecate_kwarg(func):
            return func
        return _deprecate_kwarg
    import pandas.util._decorators
    pandas.util._decorators.deprecate_kwarg = deprecate_kwarg

from pandas_datareader import wb
import plotly.express as px

# Thiết lập trang cho Web Dashboard
st.set_page_config(page_title="Macroeconomic Dashboard", layout="wide", page_icon="📈")

st.title("📈 Dashboard Kinh tế Vĩ mô - VN Stock")
st.markdown("Dữ liệu được lấy trực tiếp từ Ngân hàng Thế giới (World Bank) từ năm 2010 đến 2024.")

# Định nghĩa các định danh
indicators_map = {
    'NY.GDP.MKTP.KD.ZG': 'GDP', 
    'FM.LBL.BMNY.GD.ZS': 'M2',
    'FP.CPI.TOTL.ZG': 'INF',
    'FR.INR.RINR': 'R',
    'NE.TRD.GNFS.ZS': 'TRADE'
}

@st.cache_data
def load_data():
    try:
        # Load parameters based on the notebook
        df = wb.download(indicator=list(indicators_map.keys()), 
                         country=['VNM','CHN','LAO','THA','SGP'], 
                         start=2010, end=2024)
        df.columns = ['GDP', 'M2', 'INF', 'R', 'TRADE']
        df.reset_index(inplace=True)
        
        # Numeric fillna based on the notebook implementation
        numeric_cols = ['GDP', 'M2', 'INF', 'R', 'TRADE']
        for col in numeric_cols:
            df[col] = df[col].fillna(df[col].mean())
            
        df['year'] = df['year'].astype(int)
        df = df.sort_values(by=['country', 'year'])
        return df
    except Exception as e:
        st.error(f"Lỗi khi tải dữ liệu từ World Bank: {e}")
        return pd.DataFrame()

with st.spinner("Đang tải dữ liệu từ World Bank API..."):
    data = load_data()

if not data.empty:
    st.sidebar.header("Tùy chọn hiển thị")
    
    # Filter selection
    countries_list = data['country'].unique()
    selected_countries = st.sidebar.multiselect("Chọn Quốc gia", options=countries_list, default=['Viet Nam', 'China', 'Thailand'])
    selected_indicator = st.sidebar.selectbox("Chọn Chỉ số để so sánh", options=['GDP', 'M2', 'INF', 'R', 'TRADE'])
    
    filtered_data = data[data['country'].isin(selected_countries)]
    
    # Metric cards for the latest year
    st.subheader(f"Tổng quan chỉ số {selected_indicator} năm mới nhất")
    latest_year = filtered_data['year'].max()
    metric_cols = st.columns(len(selected_countries) if len(selected_countries) > 0 else 1)
    
    for idx, country in enumerate(selected_countries):
        country_data = filtered_data[(filtered_data['country'] == country) & (filtered_data['year'] == latest_year)]
        if not country_data.empty:
            value = country_data.iloc[0][selected_indicator]
            with metric_cols[idx]:
                st.metric(label=f"{country} ({latest_year})", value=f"{value:.2f}")

    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f"Biểu đồ đường - Xu hướng {selected_indicator}")
        if not filtered_data.empty:
            fig_line = px.line(filtered_data, x="year", y=selected_indicator, color="country", markers=True)
            st.plotly_chart(fig_line, use_container_width=True)
            
    with col2:
        st.subheader(f"Biểu đồ thanh - So sánh {selected_indicator}")
        if not filtered_data.empty:
            fig_bar = px.bar(filtered_data, x="year", y=selected_indicator, color="country", barmode="group")
            st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")
    st.subheader("Dữ liệu chi tiết (Bảng)")
    st.dataframe(filtered_data, use_container_width=True)
else:
    st.warning("Không có dữ liệu.")
