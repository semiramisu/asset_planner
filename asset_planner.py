import os
import json
import sys
import importlib

# パッケージのインポートを試みる、ローカル実行時のみ必要に応じてインストール
required_packages = [
    "streamlit",
    "pandas",
    "numpy",
    "matplotlib",
    "japanize_matplotlib",
    "plotly"
]

def install_missing_packages():
    """ローカル環境でのみ実行され、不足パッケージをインストールする"""
    # Streamlit Cloud環境ではスキップ
    if os.environ.get('STREAMLIT_SHARING') or os.environ.get('IS_STREAMLIT_CLOUD'):
        return
    
    import subprocess
    for package in required_packages:
        try:
            importlib.import_module(package)
        except ImportError:
            print(f"{package} がインストールされていません。インストールします...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"{package} のインストールが完了しました。")

# パッケージのインストールを確認
install_missing_packages()

# 以下、通常のインポート...

# パッケージのインポート部分
try:
    import streamlit as st
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import japanize_matplotlib
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import datetime
    import calendar
except ImportError as e:
    import streamlit as st
    st.error(f"""
    ## パッケージのインポートエラー
    必要なパッケージが見つかりません: {str(e)}
    
    このアプリを実行するには以下のパッケージが必要です:
    - streamlit
    - pandas
    - numpy
    - matplotlib
    - japanize_matplotlib
    - plotly
    
    ローカルで実行する場合は、`pip install <パッケージ名>` でインストールしてください。
    """)
    st.stop()
    
# 自作モジュールのインポート
from utils import (
    convert_to_yen, format_japanese_yen, 
    save_config, load_config
)
from visualizations import (
    create_asset_growth_chart, create_contribution_pie_chart,
    create_yearly_bar_chart, create_asset_distribution_chart
)

# 設定ファイルのパス
CONFIG_PATH = "asset_planner_config.json"

def main():
    # アプリ設定
    st.set_page_config(page_title="資産形成シミュレーター", layout="wide")
    
    st.title("資産形成シミュレーター")
    st.write("毎月の積立額や運用利回りから資産形成の予測を行います。")
    
    # 保存済みの設定を読み込み
    saved_config = load_config(CONFIG_PATH)
    
    # 入力値を取得
    input_values = get_user_inputs(saved_config)
    
    # データ変換
    transformed_data = transform_input_data(input_values)
    
    # シミュレーション計算
    df = run_simulation(transformed_data)
    
    # 可視化
    visualize_data(df, transformed_data, input_values)
    
    # データダウンロード機能
    provide_data_download(df)

def get_user_inputs(saved_config):
    """サイドバーから入力値を取得する"""
    inputs = {}
    
    with st.sidebar:
        st.header("シミュレーション条件")
        
        # シミュレーション期間の設定
        inputs['years'] = st.slider(
            "シミュレーション期間（年）", 
            1, 50, 
            saved_config.get('years', 30)
        )
        
        st.subheader("毎月の積立額（万円）")
        inputs['monthly_stock_man'] = st.number_input(
            "株式積立", 
            0.0, 100.0, 
            saved_config.get('monthly_stock_man', 3.0), 
            step=0.1, 
            format="%.1f"
        )
        inputs['monthly_bond_man'] = st.number_input(
            "債券積立", 
            0.0, 100.0, 
            saved_config.get('monthly_bond_man', 1.0), 
            step=0.1, 
            format="%.1f"
        )
        inputs['monthly_savings_man'] = st.number_input(
            "預金", 
            0.0, 100.0, 
            saved_config.get('monthly_savings_man', 1.0), 
            step=0.1, 
            format="%.1f"
        )
        
        # 年間利回り
        st.subheader("年間利回り")
        inputs['stock_return'] = st.slider(
            "株式利回り（％）", 
            -5.0, 20.0, 
            saved_config.get('stock_return_percent', 5.0), 
            0.1
        ) / 100
        
        inputs['bond_return'] = st.slider(
            "債券利回り（％）", 
            -3.0, 10.0, 
            saved_config.get('bond_return_percent', 1.0), 
            0.1
        ) / 100
        
        inputs['savings_return'] = st.slider(
            "預金利回り（％）", 
            0.0, 5.0, 
            saved_config.get('savings_return_percent', 0.1), 
            0.01
        ) / 100
        
        # 初期資産額の設定
        st.subheader("初期資産額（万円）")
        inputs['initial_stock_man'] = st.number_input(
            "株式初期額", 
            0.0, 10000.0, 
            saved_config.get('initial_stock_man', 0.0), 
            step=1.0, 
            format="%.1f"
        )
        inputs['initial_bond_man'] = st.number_input(
            "債券初期額", 
            0.0, 10000.0, 
            saved_config.get('initial_bond_man', 0.0), 
            step=1.0, 
            format="%.1f"
        )
        inputs['initial_savings_man'] = st.number_input(
            "預金初期額", 
            0.0, 10000.0, 
            saved_config.get('initial_savings_man', 0.0), 
            step=1.0, 
            format="%.1f"
        )
        
        # 現在の実際の総資産額（タイプ別に入力）
        st.subheader("現在の実際の資産額（万円）")
        inputs['current_stock_man'] = st.number_input(
            "現在の株式", 
            0.0, 100000.0, 
            saved_config.get('current_stock_man', 0.0), 
            step=1.0, 
            format="%.1f"
        )
        inputs['current_bond_man'] = st.number_input(
            "現在の債券", 
            0.0, 100000.0, 
            saved_config.get('current_bond_man', 0.0), 
            step=1.0, 
            format="%.1f"
        )
        inputs['current_savings_man'] = st.number_input(
            "現在の預金", 
            0.0, 100000.0, 
            saved_config.get('current_savings_man', 0.0), 
            step=1.0, 
            format="%.1f"
        )
        
        # 設定保存ボタン
        if st.button("現在の設定を保存"):
            config = {
                'years': inputs['years'],
                'monthly_stock_man': inputs['monthly_stock_man'],
                'monthly_bond_man': inputs['monthly_bond_man'],
                'monthly_savings_man': inputs['monthly_savings_man'],
                'stock_return_percent': inputs['stock_return'] * 100,
                'bond_return_percent': inputs['bond_return'] * 100,
                'savings_return_percent': inputs['savings_return'] * 100,
                'initial_stock_man': inputs['initial_stock_man'],
                'initial_bond_man': inputs['initial_bond_man'],
                'initial_savings_man': inputs['initial_savings_man'],
                'current_stock_man': inputs['current_stock_man'],
                'current_bond_man': inputs['current_bond_man'],
                'current_savings_man': inputs['current_savings_man']
            }
            save_config(CONFIG_PATH, config)
            st.success("設定を保存しました！")
    
    return inputs

def transform_input_data(inputs):
    """入力値を変換して計算用データを作成する"""
    data = {}
    
    # 万円を円に変換
    data['monthly_stock'] = convert_to_yen(inputs['monthly_stock_man'])
    data['monthly_bond'] = convert_to_yen(inputs['monthly_bond_man'])
    data['monthly_savings'] = convert_to_yen(inputs['monthly_savings_man'])
    
    data['initial_stock'] = convert_to_yen(inputs['initial_stock_man'])
    data['initial_bond'] = convert_to_yen(inputs['initial_bond_man'])
    data['initial_savings'] = convert_to_yen(inputs['initial_savings_man'])
    
    data['current_stock'] = convert_to_yen(inputs['current_stock_man'])
    data['current_bond'] = convert_to_yen(inputs['current_bond_man'])
    data['current_savings'] = convert_to_yen(inputs['current_savings_man'])
    
    # その他のデータをそのままコピー
    data['years'] = inputs['years']
    data['stock_return'] = inputs['stock_return']
    data['bond_return'] = inputs['bond_return']
    data['savings_return'] = inputs['savings_return']
    
    # 現在の総資産額を計算
    data['current_total_assets'] = data['current_stock'] + data['current_bond'] + data['current_savings']
    data['initial_total'] = data['initial_stock'] + data['initial_bond'] + data['initial_savings']
    
    return data

def run_simulation(data):
    """資産形成のシミュレーションを実行する"""
    months = data['years'] * 12
    df = pd.DataFrame(index=range(months + 1))
    
    # 初期値の設定
    df.loc[0, '株式'] = data['initial_stock']
    df.loc[0, '債券'] = data['initial_bond']
    df.loc[0, '預金'] = data['initial_savings']
    df.loc[0, '総資産'] = data['initial_stock'] + data['initial_bond'] + data['initial_savings']
    df.loc[0, '積立合計'] = 0
    
    # 運用シミュレーション
    for i in range(1, months + 1):
        # 前月の資産に利回りを適用（月次）
        df.loc[i, '株式'] = df.loc[i-1, '株式'] * (1 + data['stock_return']/12) + data['monthly_stock']
        df.loc[i, '債券'] = df.loc[i-1, '債券'] * (1 + data['bond_return']/12) + data['monthly_bond']
        df.loc[i, '預金'] = df.loc[i-1, '預金'] * (1 + data['savings_return']/12) + data['monthly_savings']
        df.loc[i, '総資産'] = df.loc[i, '株式'] + df.loc[i, '債券'] + df.loc[i, '預金']
        
        # 積立合計額の累計
        df.loc[i, '積立合計'] = df.loc[i-1, '積立合計'] + data['monthly_stock'] + data['monthly_bond'] + data['monthly_savings']
    
    # 列を追加：運用益（総資産 - 積立合計 - 初期資産）
    df['運用益'] = df['総資産'] - df['積立合計'] - data['initial_total']
    
    # 日付の追加
    add_date_columns(df, months)
    
    return df

def add_date_columns(df, months):
    """日付関連の列を追加する"""
    # 月末ベースで日付のインデックスを作成
    start_date = datetime.datetime.now()
    date_index = []
    current_date = start_date
    
    for i in range(months + 1):
        date_index.append(current_date)
        # 次の月を正確に計算（月末の日付を計算）
        if i < months:
            # 現在の月に1を加え、日付は月末に設定
            next_month = current_date.month + 1
            next_year = current_date.year
            if next_month > 12:
                next_month = 1
                next_year += 1
            # その月の最終日を取得
            last_day = calendar.monthrange(next_year, next_month)[1]
            current_date = datetime.datetime(next_year, next_month, last_day)
    
    df['日付'] = date_index
    df['年月'] = [d.strftime('%Y年%m月') for d in date_index]

def visualize_data(df, data, inputs):
    """データの可視化を行う"""
    # 資産推移と積立額・運用益のグラフを表示
    cols1, cols2 = st.columns(2)
    
    with cols1:
        st.subheader("資産推移")
        
        fig = create_asset_growth_chart(
            df, 
            data['current_total_assets'], 
            data['current_stock'], 
            data['current_bond'], 
            data['current_savings']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with cols2:
        st.subheader("積立額と運用益")
        
        months = data['years'] * 12
        final_investment = df.loc[months, '積立合計']
        final_return = df.loc[months, '運用益']
        final_initial = data['initial_total']
        
        if final_investment + final_return + final_initial > 0:
            fig = create_contribution_pie_chart(
                final_investment, 
                final_return, 
                final_initial, 
                inputs['years']
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("表示するデータがありません")
    
    # 年別サマリーテーブル
    display_yearly_summary(df)
    
    # 年別積み上げ棒グラフ
    display_yearly_bar_chart(df)
    
    # 進捗状況とアセット配分比較を表示
    if data['current_total_assets'] > 0:
        display_progress(df, data)

def display_yearly_summary(df):
    """年別サマリーテーブルを表示する"""
    st.subheader("年別サマリー")
    
    # 1年ごとのデータを抽出
    yearly_data = df.iloc[::12].copy()
    yearly_data['経過年数'] = yearly_data.index // 12
    yearly_data = yearly_data.set_index('経過年数')
    
    # 表示するデータを選択
    display_data = yearly_data[['日付', '株式', '債券', '預金', '総資産', '積立合計', '運用益']].copy()
    display_data['日付'] = [d.strftime('%Y年%m月') for d in display_data['日付']]
    
    # 数値を整形
    for col in ['株式', '債券', '預金', '総資産', '積立合計', '運用益']:
        display_data[col] = display_data[col].map(format_japanese_yen)
    
    st.dataframe(display_data, use_container_width=True)

def display_yearly_bar_chart(df):
    """年別積み上げ棒グラフを表示する"""
    st.subheader("年別資産構成の推移")
    
    # 棒グラフ用のデータ準備
    bar_data = df.iloc[::12].copy()  # 1年毎のデータ
    bar_data['経過年数'] = bar_data.index // 12
    
    fig = create_yearly_bar_chart(bar_data)
    st.plotly_chart(fig, use_container_width=True)

def display_progress(df, data):
    """進捗状況と資産構成比較を表示する"""
    st.subheader("資産形成の進捗状況")
    
    months = data['years'] * 12
    # 現在の総資産がシミュレーション上でどの時点に相当するかを計算
    progress_point = df[df['総資産'] >= data['current_total_assets']].index[0] if any(df['総資産'] >= data['current_total_assets']) else months
    progress_years = progress_point / 12
    
    # 進捗率の計算（最終予測額に対する割合）
    progress_percentage = (data['current_total_assets'] / df.loc[months, '総資産']) * 100
    
    cols3, cols4 = st.columns(2)
    
    with cols3:
        st.metric(
            "シミュレーション上の進捗点", 
            f"{progress_years:.1f}年目", 
            f"全体の{progress_years/data['years']*100:.1f}%"
        )
    
    with cols4:
        st.metric(
            "最終予測額に対する現在の割合", 
            f"{progress_percentage:.1f}%", 
            f"目標額 {format_japanese_yen(df.loc[months, '総資産'])}"
        )
    
    # 進捗バーの表示
    st.progress(min(progress_percentage / 100, 1.0))
    
    # 資産構成比較
    display_asset_distribution_comparison(df, data, months)

def display_asset_distribution_comparison(df, data, months):
    """資産構成の比較を表示する"""
    st.subheader("現在の資産構成と目標構成の比較")
    
    cols5, cols6 = st.columns(2)
    
    with cols5:
        # 現在の資産構成
        current_values = [data['current_stock'], data['current_bond'], data['current_savings']]
        fig = create_asset_distribution_chart(current_values, "現在の資産構成")
        st.plotly_chart(fig, use_container_width=True)
    
    with cols6:
        # 最終目標の資産構成
        final_values = [df.loc[months, '株式'], df.loc[months, '債券'], df.loc[months, '預金']]
        fig = create_asset_distribution_chart(final_values, f"{data['years']}年後の目標資産構成")
        st.plotly_chart(fig, use_container_width=True)

def provide_data_download(df):
    """シミュレーション結果のダウンロード機能"""
    st.subheader("データダウンロード")
    csv = df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="シミュレーション結果をCSVでダウンロード",
        data=csv,
        file_name=f'資産形成シミュレーション_{datetime.datetime.now().strftime("%Y%m%d")}.csv',
        mime='text/csv',
    )

if __name__ == "__main__":
    main()