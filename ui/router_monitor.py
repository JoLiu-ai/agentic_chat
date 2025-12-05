"""
Router监控仪表盘 - 可视化路由决策
运行: streamlit run router_monitor.py
"""
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# 页面配置
st.set_page_config(
    page_title="Router监控仪表盘",
    page_icon="🔀",
    layout="wide"
)

API_BASE = "http://localhost:8000/api/v1/router"

st.title("🔀 Router监控仪表盘")
st.markdown("实时查看Agent路由决策和统计信息")

# 刷新按钮
col1, col2 = st.columns([6, 1])
with col2:
    if st.button("🔄 刷新数据"):
        st.rerun()

# 获取统计数据
try:
    stats_response = requests.get(f"{API_BASE}/routes/stats")
    if stats_response.status_code == 200:
        stats = stats_response.json()
        
        # 显示关键指标
        st.markdown("## 📊 路由统计")
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        
        with metric_col1:
            st.metric("总路由数", stats["total_routes"])
        with metric_col2:
            st.metric("Researcher", f"{stats['researcher_count']} ({stats['researcher_percentage']}%)")
        with metric_col3:
            st.metric("Coder", f"{stats['coder_count']} ({stats['coder_percentage']}%)")
        with metric_col4:
            st.metric("General", f"{stats['general_count']} ({stats['general_percentage']}%)")
        
        # 饼图：Agent分布
        if stats["total_routes"] > 0:
            st.markdown("## 📈 Agent使用分布")
            
            fig = go.Figure(data=[go.Pie(
                labels=['Researcher', 'Coder', 'General'],
                values=[stats['researcher_count'], stats['coder_count'], stats['general_count']],
                marker=dict(colors=['#3498db', '#2ecc71', '#95a5a6']),
                hole=0.3
            )])
            fig.update_layout(
                title="Agent路由分布",
                showlegend=True
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.error(f"无法获取统计数据: {stats_response.status_code}")
except Exception as e:
    st.error(f"连接API失败: {str(e)}")
    st.info("请确保后端服务已启动: `uvicorn app.main:app --reload`")

# 获取路由历史
st.markdown("## 📜 路由历史记录")

limit = st.slider("显示记录数", 10, 100, 50)

try:
    history_response = requests.get(f"{API_BASE}/routes/history?limit={limit}")
    if history_response.status_code == 200:
        history = history_response.json()
        
        if history:
            # 转换为DataFrame
            df = pd.DataFrame(history)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # 过滤器
            col1, col2 = st.columns(2)
            with col1:
                agent_filter = st.multiselect(
                    "筛选Agent",
                    options=["researcher", "coder", "general_assistant"],
                    default=["researcher", "coder", "general_assistant"]
                )
            
            filtered_df = df[df['routed_to'].isin(agent_filter)]
            
            # 显示表格
            st.dataframe(
                filtered_df[['timestamp', 'user_message', 'routed_to', 'reasoning']],
                use_container_width=True,
                hide_index=True
            )
            
            # 详细查看
            st.markdown("### 🔍 详细查看")
            selected_id = st.selectbox(
                "选择记录ID",
                options=filtered_df['id'].tolist(),
                format_func=lambda x: f"ID {x} - {filtered_df[filtered_df['id']==x]['user_message'].values[0][:50]}..."
            )
            
            if selected_id:
                record = filtered_df[filtered_df['id'] == selected_id].iloc[0]
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**用户消息:**")
                    st.info(record['user_message'])
                    
                with col2:
                    st.markdown("**路由决策:**")
                    st.success(f"Agent: {record['routed_to']}")
                    st.markdown("**推理过程:**")
                    st.write(record['reasoning'])
                    
                st.markdown(f"**时间:** {record['timestamp']}")
                st.markdown(f"**会话ID:** {record['session_id']}")
        else:
            st.info("暂无路由历史记录")
    else:
        st.error(f"无法获取历史记录: {history_response.status_code}")
except Exception as e:
    st.error(f"加载历史记录失败: {str(e)}")

# 测试Router
st.markdown("---")
st.markdown("## 🧪 测试Router")

test_message = st.text_input("输入测试消息", "今天天气如何？")
if st.button("测试路由"):
    with st.spinner("路由中..."):
        try:
            # 调用chat API来触发路由
            response = requests.post(
                "http://localhost:8000/api/v1/chat",
                json={
                    "message": test_message,
                    "session_id": "router_test",
                    "user_id": "test_user"
                }
            )
            if response.status_code == 200:
                st.success("路由成功！刷新页面查看最新记录。")
            else:
                st.error(f"路由失败: {response.text}")
        except Exception as e:
            st.error(f"测试失败: {str(e)}")
