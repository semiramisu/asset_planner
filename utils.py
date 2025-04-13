import os
import json
import streamlit as st

# 万円単位で入力して円に変換する関数
def convert_to_yen(value):
    """万円を円に変換する"""
    return int(value * 10000)

# 数値を日本語の単位（万、億）で表示する関数
def format_japanese_yen(value):
    """金額を日本語の単位（万円、億円）で表示する"""
    if value >= 100000000:  # 1億円以上
        return f"{value/100000000:.1f}億円"
    elif value >= 10000:  # 1万円以上
        return f"{value/10000:.1f}万円"
    else:
        return f"{value:,.0f}円"

# 設定を保存する関数
def save_config(config_path, config):
    """設定をJSONファイルに保存する"""
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

# 設定を読み込む関数
def load_config(config_path):
    """設定をJSONファイルから読み込む"""
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            st.warning(f"設定ファイルの読み込みに失敗しました: {e}")
    return {}

# Y軸の目盛り値とテキストを作成する関数
def create_y_axis_ticks(max_value):
    """Y軸の目盛りを作成する"""
    if max_value >= 100000000:  # 1億円以上の場合
        tick_step = 50000000  # 5000万円ごと
        max_tick = (max_value // tick_step + 1) * tick_step
        tickvals = list(range(0, int(max_tick) + tick_step, tick_step))
        ticktext = []
        for x in tickvals:
            if x == 0:
                ticktext.append("0")
            elif x >= 100000000:
                if x % 100000000 == 0:
                    ticktext.append(f"{int(x/100000000)}億円")
                else:
                    ticktext.append(f"{x/100000000:.1f}億円")
            else:
                ticktext.append(f"{int(x/10000)}万円")
    elif max_value >= 10000000:  # 1000万円以上の場合
        tick_step = 5000000  # 500万円ごと
        max_tick = (max_value // tick_step + 1) * tick_step
        tickvals = list(range(0, int(max_tick) + tick_step, tick_step))
        ticktext = ["0" if x == 0 else f"{int(x/10000)}万円" for x in tickvals]
    elif max_value >= 1000000:  # 100万円以上の場合
        tick_step = 1000000  # 100万円ごと
        max_tick = (max_value // tick_step + 1) * tick_step
        tickvals = list(range(0, int(max_tick) + tick_step, tick_step))
        ticktext = ["0" if x == 0 else f"{int(x/10000)}万円" for x in tickvals]
    else:  # 100万円未満の場合
        tick_step = 100000  # 10万円ごと
        max_tick = (max_value // tick_step + 1) * tick_step
        tickvals = list(range(0, int(max_tick) + tick_step, tick_step))
        ticktext = ["0" if x == 0 else f"{int(x/10000)}万円" for x in tickvals]
    
    return tickvals, ticktext