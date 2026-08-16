import plotly.express as px
import pandas as pd
import sqlite3
import os


BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

DB_PATH = os.path.join(
    BASE_DIR,
    "data",
    "expenses.db"
)


def get_expense_donut_chart(thread_id):
    """Fetch category-wise expenses and return a styled Plotly donut chart."""

    try:
        # -----------------------------
        # Fetch expense data
        # -----------------------------
        conn = sqlite3.connect(DB_PATH)

        query = """
            SELECT
                category,
                SUM(amount) AS total_amount
            FROM expenses
            WHERE thread_id = ?
            GROUP BY category
            ORDER BY total_amount DESC
        """

        df = pd.read_sql_query(
            query,
            conn,
            params=(thread_id,)
        )

        conn.close()

        # -----------------------------
        # Handle empty data
        # -----------------------------
        if df.empty or df["total_amount"].sum() == 0:
            return None

        # -----------------------------
        # Category colors
        # -----------------------------
        category_colors = {
            "flight": "#3B82F6",
            "accommodation": "#8B5CF6",
            "food": "#10B981",
            "transport": "#F59E0B",
            "shopping": "#EF4444",
            "entertainment": "#EC4899",
            "other": "#64748B"
        }

        # Normalize category names
        df["category"] = df["category"].str.lower()

        # Use fallback color for unknown categories
        default_colors = [
            "#3B82F6",
            "#8B5CF6",
            "#10B981",
            "#F59E0B",
            "#EF4444",
            "#EC4899",
            "#64748B"
        ]

        colors = [
            category_colors.get(
                category,
                default_colors[i % len(default_colors)]
            )
            for i, category in enumerate(df["category"])
        ]

        # -----------------------------
        # Create donut
        # -----------------------------
        fig = px.pie(
            df,
            names="category",
            values="total_amount",
            hole=0.67
        )

        # -----------------------------
        # Highlight largest category
        # -----------------------------
        pull = [0.025] + [0] * (len(df) - 1)

        fig.update_traces(
            marker=dict(
                colors=colors,
                line=dict(
                    color="#0B1220",
                    width=3
                )
            ),

            # Keep labels clean
            textposition="inside",
            textinfo="percent",

            # Horizontal text instead of rotated text
            insidetextorientation="horizontal",

            textfont=dict(
                size=12,
                color="white"
            ),

            pull=pull,

            # Better hover information
            hovertemplate=(
                "<b>%{label}</b><br>"
                "Amount: ₹%{value:,.0f}<br>"
                "Share: %{percent}"
                "<extra></extra>"
            )
        )

        # -----------------------------
        # Center content
        # -----------------------------
        category_count = len(df)

        fig.add_annotation(
            x=0.5,
            y=0.5,
            text=(
                f"<span style='font-size:11px;color:#94A3B8'>"
                f"EXPENSES"
                f"</span>"
                f"<br>"
                f"<b style='font-size:22px;color:#F8FAFC'>"
                f"{category_count}"
                f"</b>"
                f"<br>"
                f"<span style='font-size:10px;color:#64748B'>"
                f"categories"
                f"</span>"
            ),
            showarrow=False,
            align="center"
        )

        # -----------------------------
        # Layout
        # -----------------------------
        fig.update_layout(

            # IMPORTANT:
            # Makes Plotly blend into your dark dashboard
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",

            showlegend=False,

            # More breathing room
            margin=dict(
                t=15,
                b=15,
                l=15,
                r=15
            ),

            # Better typography
            font=dict(
                family="Inter, Arial, sans-serif",
                color="#E2E8F0"
            ),

            # Better hover card
            hoverlabel=dict(
                bgcolor="#111827",
                bordercolor="#334155",
                font=dict(
                    size=13,
                    color="#F8FAFC"
                )
            ),

            # Prevent Plotly from trying to make labels tiny
            uniformtext=dict(
                minsize=10,
                mode="hide"
            )
        )

        return fig

    except Exception as e:
        print(f"Chart Error: {e}")
        return None