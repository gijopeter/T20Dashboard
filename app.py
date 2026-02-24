import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

st.set_page_config(page_title="Global ECE - T20 Prediction", layout="wide")
st.title("🏏 Global ECE - T20 Prediction ")

st.markdown("---")

# =================================================================
# 📊 DATA LOADING
# =================================================================

CURRENT_FILE = "points.xlsx"
PREVIOUS_FILE = "points_previous.xlsx"

if not os.path.exists(CURRENT_FILE):
    st.error(f"Excel file '{CURRENT_FILE}' not found. Please add it to the repository.")
    st.stop()

df_original = pd.read_excel(CURRENT_FILE)

# --- Data Preparation ---
name_col = df_original.columns[0]
df_original = df_original.rename(columns={name_col: "Name"})
game_columns = df_original.columns[1:]

if game_columns.empty:
    st.warning("The Excel file does not contain any game data columns.")
    st.stop()

df = df_original.copy()
df["Total Points"] = df[game_columns].sum(axis=1)

# Sort by Total Points (desc), then Name (asc)
df = df.sort_values(by=["Total Points", "Name"], ascending=[False, True])
df["Rank"] = df["Total Points"].rank(method="min", ascending=False).astype(int)

# =================================================================
# 🔄 RANK CHANGE CALCULATION
# =================================================================

if os.path.exists(PREVIOUS_FILE):
    prev_df = pd.read_excel(PREVIOUS_FILE)
    prev_name_col = prev_df.columns[0]
    prev_df = prev_df.rename(columns={prev_name_col: "Name"})
    prev_game_columns = prev_df.columns[1:]

    prev_df["Total Points"] = prev_df[prev_game_columns].sum(axis=1)
    prev_df = prev_df.sort_values(by=["Total Points", "Name"], ascending=[False, True])
    prev_df["Prev Rank"] = prev_df["Total Points"].rank(method="min", ascending=False).astype(int)

    df = df.merge(prev_df[["Name", "Prev Rank"]], on="Name", how="left")
    df["Rank Change"] = df["Prev Rank"] - df["Rank"]

else:
    df["Rank Change"] = None

# =================================================================
# 🏆 OVERALL LEADERBOARD – LIGHT THEME, RANK + ARROWS + MEDALS
# =================================================================

st.header("🏆 Overall Leaderboard")

# Medal assignment
def medal(rank):
    if rank == 1: return "🥇"
    if rank == 2: return "🥈"
    if rank == 3: return "🥉"
    return ""

df["Medal"] = df["Rank"].apply(medal)

# Format Rank + Arrow
def formatted_rank(row):
    rank_number = f"<b>{row['Rank']}</b>"
    spacer = "&nbsp;"*6
    change = row.get("Rank Change", None)
    
    if pd.isna(change):
        arrow = ""
    elif change > 0:
        arrow = f'{spacer}<span style="color:green;">⬆ +{int(change)}</span>'
    elif change < 0:
        arrow = f'{spacer}<span style="color:red;">⬇ {int(change)}</span>'
    else:
        arrow = f'{spacer}<span style="color:gray;">→ 0</span>'
    
    return rank_number + arrow

df["Rank Display"] = df.apply(formatted_rank, axis=1)

# Build HTML table
html = "<table style='width:100%; border-collapse: collapse; font-size:14px; background-color:white; color:black;'>"
# Header
html += "<tr style='background-color:#1f2937; color:white;'>"
html += "<th style='padding:8px; text-align:center;'>Rank</th>"
html += "<th style='padding:8px; text-align:center;'>Medal</th>"
html += "<th style='padding:8px; text-align:left;'>Name</th>"
html += "<th style='padding:8px; text-align:center;'>Total Points</th>"
html += "</tr>"

# Rows
for _, row in df.iterrows():
    # Subtle background for top 3
    if row["Rank"] == 1:
        bg = "#FFD70020"  # Gold transparent
    elif row["Rank"] == 2:
        bg = "#C0C0C020"  # Silver
    elif row["Rank"] == 3:
        bg = "#CD7F3220"  # Bronze
    else:
        bg = "#f9f9f9"

    html += f"<tr style='border-bottom:1px solid #ddd; background-color:{bg};'>"
    html += f"<td style='padding:8px; text-align:center;'>{row['Rank Display']}</td>"
    html += f"<td style='padding:8px; text-align:center;'>{row['Medal']}</td>"
    html += f"<td style='padding:8px; text-align:left;'>{row['Name']}</td>"
    html += f"<td style='padding:8px; text-align:center;'>{row['Total Points']}</td>"
    html += "</tr>"

html += "</table>"

st.markdown(html, unsafe_allow_html=True)

# =================================================================
# 🔥 TRACKER – RECENT PERFORMANCE (Last 5 Games)
# =================================================================

st.header("🔥 Tracker – Recent Performance")

num_games = min(5, len(game_columns))
last_n_games = game_columns[-num_games:]

if num_games < 2:
    st.warning("Not enough game data to draw a trend line.")
else:
    top7_names = df.head(7)["Name"].tolist()

    tracker_df = df_original[df_original["Name"].isin(top7_names)].copy()
    tracker_df['Name'] = pd.Categorical(tracker_df['Name'], categories=top7_names, ordered=True)
    tracker_df = tracker_df.sort_values('Name')

    tracker_df[game_columns] = tracker_df[game_columns].cumsum(axis=1)

    fig_line_chart = go.Figure()

    for _, row in tracker_df.iterrows():
        fig_line_chart.add_trace(go.Scatter(
            x=last_n_games,
            y=row[last_n_games],
            mode='lines+markers',
            name=row["Name"]
        ))

    fig_line_chart.update_layout(
        title="Top 7 Cumulative Points – Last 5 Games",
        xaxis_title="Prediction Games",
        yaxis_title="Cumulative Points",
        height=600,
        template="plotly_white",
        hovermode="x unified"
    )

    st.plotly_chart(fig_line_chart, use_container_width=True)

# =================================================================
# 🔍 INDIVIDUAL PLAYER ANALYSIS
# =================================================================

st.header("🔍 Individual Player Analysis")

all_players = sorted(df_original["Name"].tolist())
selected_player = st.selectbox("Select a Player to Analyze", options=all_players)

if selected_player:
    player_data = df_original[df_original["Name"] == selected_player]
    player_scores = player_data[game_columns].T
    player_scores.columns = ["Points"]

    fig_bar_individual = go.Figure()

    fig_bar_individual.add_trace(go.Bar(
        x=player_scores.index,
        y=player_scores["Points"],
        text=player_scores["Points"],
        textposition='auto'
    ))

    fig_bar_individual.update_layout(
        title=f"Game-by-Game Performance for {selected_player}",
        xaxis_title="Prediction Game",
        yaxis_title="Points Scored",
        height=500,
        template="plotly_white"
    )

    st.plotly_chart(fig_bar_individual, use_container_width=True)