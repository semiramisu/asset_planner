import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils import format_japanese_yen, create_y_axis_ticks

def create_asset_growth_chart(df, current_total_assets, current_stock, current_bond, current_savings):
    """資産推移グラフを作成する"""
    fig = make_subplots()
    
    # 資産種類別の推移
    fig.add_trace(go.Scatter(x=df['日付'], y=df['株式'], name='株式', line=dict(color='#FF6B6B')))
    fig.add_trace(go.Scatter(x=df['日付'], y=df['債券'], name='債券', line=dict(color='#4ECDC4')))
    fig.add_trace(go.Scatter(x=df['日付'], y=df['預金'], name='預金', line=dict(color='#45B7D1')))
    fig.add_trace(go.Scatter(x=df['日付'], y=df['総資産'], name='総資産', line=dict(color='#F9A826', width=3)))
    
    # 現在の総資産表示ライン
    if current_total_assets > 0:
        fig.add_shape(
            type="line",
            x0=df['日付'].min(),
            y0=current_total_assets,
            x1=df['日付'].max(),
            y1=current_total_assets,
            line=dict(color="red", width=2, dash="dash"),
        )
        fig.add_annotation(
            x=df['日付'].max(),
            y=current_total_assets,
            text=f"現在の総資産: {format_japanese_yen(current_total_assets)}",
            showarrow=True,
            arrowhead=1
        )
        
        # 現在の資産構成の割合を計算
        if current_total_assets > 0:
            stock_percent = current_stock/current_total_assets*100
            bond_percent = current_bond/current_total_assets*100
            savings_percent = current_savings/current_total_assets*100
            
            # アノテーションを追加
            fig.add_annotation(
                x=df['日付'].min(),
                y=current_total_assets,
                text=(
                    f"現在の資産構成: "
                    f"株式 {format_japanese_yen(current_stock)} ({stock_percent:.1f}%)、"
                    f"債券 {format_japanese_yen(current_bond)} ({bond_percent:.1f}%)、"
                    f"預金 {format_japanese_yen(current_savings)} ({savings_percent:.1f}%)"
                ),
                showarrow=False,
                yshift=-30,
                xshift=0,
                align="left",
                xanchor="left"
            )
    
    # Y軸の表示形式を日本語の単位に変更
    max_value = df['総資産'].max()
    tickvals, ticktext = create_y_axis_ticks(max_value)
    
    fig.update_layout(
        title="資産推移シミュレーション",
        xaxis_title="年月",
        yaxis_title="金額",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=500,
        yaxis=dict(
            tickvals=tickvals,
            ticktext=ticktext
        )
    )
    
    # ホバー表示も日本語表記に
    fig.update_traces(
        hovertemplate='%{y:,.0f}円'
    )
    
    return fig

def create_contribution_pie_chart(final_investment, final_return, final_initial, years):
    """積立額と運用益の円グラフを作成する"""
    labels = ['積立合計', '運用益', '初期資産']
    values = [final_investment, final_return, final_initial]
    colors = ['#4ECDC4', '#FF6B6B', '#F9A826']
    
    # 0以下の値があれば除外
    filtered_labels = []
    filtered_values = []
    filtered_colors = []
    
    for i, value in enumerate(values):
        if value > 0:
            filtered_labels.append(labels[i])
            filtered_values.append(value)
            filtered_colors.append(colors[i])
    
    fig = go.Figure(data=[go.Pie(
        labels=filtered_labels,
        values=filtered_values,
        hole=.4,
        marker_colors=filtered_colors,
        text=[format_japanese_yen(val) for val in filtered_values],
        hoverinfo='label+text+percent'
    )])
    
    fig.update_layout(
        title=f"{years}年後の資産構成",
        height=500
    )
    
    return fig

def create_yearly_bar_chart(bar_data):
    """年別積み上げ棒グラフを作成する"""
    fig = go.Figure()
    
    # 資産クラス毎に棒を追加（積み上げ方式）
    fig.add_trace(go.Bar(
        x=bar_data['経過年数'],
        y=bar_data['株式'],
        name='株式',
        marker_color='#FF6B6B',
        hovertemplate='株式: %{y:,.0f}円 (' + bar_data['株式'].apply(format_japanese_yen) + ')<extra></extra>'
    ))
    
    fig.add_trace(go.Bar(
        x=bar_data['経過年数'],
        y=bar_data['債券'],
        name='債券',
        marker_color='#4ECDC4',
        hovertemplate='債券: %{y:,.0f}円 (' + bar_data['債券'].apply(format_japanese_yen) + ')<extra></extra>'
    ))
    
    fig.add_trace(go.Bar(
        x=bar_data['経過年数'],
        y=bar_data['預金'],
        name='預金',
        marker_color='#45B7D1',
        hovertemplate='預金: %{y:,.0f}円 (' + bar_data['預金'].apply(format_japanese_yen) + ')<extra></extra>'
    ))
    
    # 積み上げ設定
    fig.update_layout(
        barmode='stack',
        title='年別資産構成の推移',
        xaxis=dict(
            title='経過年数',
            tickmode='linear',
            tick0=0,
            dtick=5  # 5年ごとに目盛りを表示
        ),
        yaxis=dict(
            title='資産額'
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=500
    )
    
    # Y軸の表示形式を日本語の単位に変更
    max_value = bar_data['総資産'].max()
    tickvals, ticktext = create_y_axis_ticks(max_value)
    
    # Y軸の設定を適用
    fig.update_layout(
        yaxis=dict(
            tickvals=tickvals,
            ticktext=ticktext
        )
    )
    
    return fig

def create_asset_distribution_chart(values, title):
    """資産分布の円グラフを作成する"""
    labels = ['株式', '債券', '預金']
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=.4,
        marker_colors=colors,
        text=[format_japanese_yen(val) for val in values],
        hoverinfo='label+text+percent'
    )])
    
    fig.update_layout(
        title=title,
        height=400
    )
    
    return fig