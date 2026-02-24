import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

st.set_page_config(page_title="GEC Thrissur ECE - T20 Leaderboard", layout="wide")
st.title("🏏 GEC Thrissur ECE - T20 Prediction Leaderboard")

EXCEL_FILE = "points.xlsx"  # or "data/points.xlsx" if in a subfolder

if os.path.exists(EXCEL_FILE):
    df_original = pd.read_excel(EXCEL_FILE)
else:
    st.error(f"Excel file '{EXCEL_FILE}' not found in the repo!")
    st.stop() # Stop execution if file is not found

# First column = Name
name_col = df_original.columns[0]
df_original = df_original.rename(columns={name_col: "Name"})
game_columns = df_original.columns[1:]

# ===============================
# 🏆 Calculate Total Points and Rank
# ===============================
df = df_original.copy()
df["Total Points"] = df[game_columns].sum(axis=1)

# --- MODIFIED SORTING LOGIC ---
# Sort by Total Points (desc), then by Name (asc) for tie-breaking
df = df.sort_values(by=["Total Points", "Name"], ascending=[False, True])
# --- END OF MODIFICATION ---

# Use rank(method='min') to handle ties correctly for the rank number
df["Rank"] = df["Total Points"].rank(method="min", ascending=False).astype(int)


# Add medal emojis
def medal(rank):
    if rank == 1:
        return "🥇"
    elif rank == 2:
        return "🥈"
    elif rank == 3:
        return "🥉"
    else:
        return ""

df["Medal"] = df["Rank"].apply(medal)

# ===============================
# 🏆 OVERALL LEADERBOARD WITH MEDALS
# ===============================
st.header("🏆 Overall Leaderboard")

# Re-order columns for display
leaderboard_display = df[["Rank", "Medal", "Name", "Total Points"]]

fig_table = go.Figure(data=[go.Table(
    columnwidth=[50, 50, 250, 120],
    header=dict(
        values=["Rank", "Medal", "Name", "Total Points"],
        fill_color="#1f2937",
        font=dict(color="white", size=14),
        align="center"
    ),
    cells=dict(
        values=[
            leaderboard_display["Rank"],
            leaderboard_display["Medal"],
            leaderboard_display["Name"],
            leaderboard_display["Total Points"]
        ],
        fill_color="white",
        align="center",
        height=30,
        font=dict(size=12)
    )
)])

fig_table.update_layout(height=500)
st.plotly_chart(fig_table, use_container_width=True)

# ===============================
# 📈 TOP 7 – LAST 5 GAMES – CUMULATIVE
# ===============================
st.header("📈 Title Race – Top 7 (Last 5 Games)")

top7_names = df.head(7)["Name"]
race_df = df_original[df_original["Name"].isin(top7_names)].copy()

# Set Name as index to easily perform cumulative sum on game columns
race_df = race_df.set_index("Name")
race_df[game_columns] = race_df[game_columns].cumsum(axis=1)
race_df = race_df.reset_index() # Reset index back to default

last_5_games = list(game_columns[-5:])

fig_chart = go.Figure()

for _, row in race_df.iterrows():
    fig_chart.add_trace(go.Scatter(
        x=last_5_games,
        y=row[last_5_games],
        mode='lines+markers',
        name=row["Name"]
    ))

fig_chart.update_layout(
    title="Top 7 Cumulative Points – Last 5 Games",
    xaxis_title="Prediction Games",
    yaxis_title="Cumulative Points",
    height=700,
    template="plotly_white",
    hovermode="x unified"
)
st.plotly_chart(fig_chart, use_container_width=True)
