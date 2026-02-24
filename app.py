import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

st.set_page_config(page_title="GEC Thrissur ECE - T20 Leaderboard", layout="wide")
st.title("🏏 GEC Thrissur ECE - T20 Prediction Leaderboard")

EXCEL_FILE = "points.xlsx"

if os.path.exists(EXCEL_FILE):
    df_original = pd.read_excel(EXCEL_FILE)
else:
    st.error(f"Excel file '{EXCEL_FILE}' not found. Please add it to the repository.")
    st.stop()

# --- Data Preparation ---
name_col = df_original.columns[0]
df_original = df_original.rename(columns={name_col: "Name"})
game_columns = df_original.columns[1:]

if game_columns.empty:
    st.warning("The Excel file does not contain any game data columns.")
    st.stop()

df = df_original.copy()
df["Total Points"] = df[game_columns].sum(axis=1)

# Sort by Total Points (desc), then by Name (asc) for tie-breaking
df = df.sort_values(by=["Total Points", "Name"], ascending=[False, True])

# Use rank(method='min') to handle ties correctly for the rank number
df["Rank"] = df["Total Points"].rank(method="min", ascending=False).astype(int)

def medal(rank):
    if rank == 1: return "🥇"
    if rank == 2: return "🥈"
    if rank == 3: return "🥉"
    return ""

df["Medal"] = df["Rank"].apply(medal)


# ===============================
# 🏆 OVERALL LEADERBOARD
# ===============================
st.header("🏆 Overall Leaderboard")
leaderboard_display = df[["Rank", "Medal", "Name", "Total Points"]]
fig_table = go.Figure(data=[go.Table(
    columnwidth=[50, 50, 250, 120],
    header=dict(values=["Rank", "Medal", "Name", "Total Points"], fill_color="#1f2937", font=dict(color="white", size=14), align="center"),
    cells=dict(values=[leaderboard_display["Rank"], leaderboard_display["Medal"], leaderboard_display["Name"], leaderboard_display["Total Points"]], fill_color="white", align="center", height=30, font=dict(size=12))
)])
fig_table.update_layout(height=500, margin=dict(l=10, r=10, t=5, b=5))
st.plotly_chart(fig_table, use_container_width=True)


# =================================================================
# 🔥 TRACKER – RECENT PERFORMANCE (Last 5 Games)
# =================================================================
st.header("🔥 Tracker – Recent Performance")

# Determine the last 5 games, or fewer if not enough data
num_games = min(5, len(game_columns)) # <<< CHANGED FROM 3 to 5
last_n_games = game_columns[-num_games:]

if num_games == 0:
    st.warning("No game data available to show recent performance.")
else:
    # Get the names of the top 7 players
    top7_names = df.head(7)["Name"]
    
    # Filter the original dataframe for top 7 players and last 5 games
    heatmap_df = df_original[df_original["Name"].isin(top7_names)].copy()
    heatmap_df = heatmap_df[["Name"] + list(last_n_games)]
    
    # Calculate the total points for the last 5 games
    heatmap_df["Total"] = heatmap_df[last_n_games].sum(axis=1)
    
    # Sort the dataframe by the new 'Total' column
    heatmap_df = heatmap_df.sort_values(by="Total", ascending=False)
    
    # Set 'Name' as the index for better display
    heatmap_df = heatmap_df.set_index("Name")

    # Style the dataframe to create the heatmap
    styled_df = heatmap_df.style.background_gradient(
        cmap='Greens',
        subset=last_n_games
    ).format(
        '{:.0f}' # Format all numbers as integers
    )
    
    # Display the styled dataframe
    st.dataframe(styled_df, use_container_width=True)
    st.caption(f"Color shows performance in the last {num_games} games. Higher scores are darker green.")

