import dash
from dash import dcc, html, Input, Output, callback, no_update
import plotly.express as px
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import plotly.io as pio

# Set Plotly template
pio.templates.default = 'plotly_dark'

try:
    # Try local CSV first (UCI format uses ; separator)
    df = pd.read_csv('student-mat.csv', sep=';')
except FileNotFoundError:
    # Fallback to online
df = pd.read_csv('https://raw.githubusercontent.com/dashee87/decision-trees-repo/master/student-mat.csv', sep=';')

# Data prep
df['G3'] = pd.to_numeric(df['G3'], errors='coerce')
df = df.dropna(subset=['G3'])

# App with suppress_callback_exceptions for dynamic
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Custom CSS for glassmorphism, futuristic effects
app.index_string = '''
<!DOCTYPE html>
<html>
<head>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Outfit:wght@400;600;800&display=swap" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    {%metas%}
    <title>Nexus Analytics</title>
    {%favicon%}
    {%css%}
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Inter', sans-serif; 
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%); 
            min-height: 100vh; 
            overflow-x: hidden;
            perspective: 1000px;
        }
        .glass { 
            background: rgba(255,255,255,0.05); 
            backdrop-filter: blur(20px); 
            border: 1px solid rgba(255,255,255,0.1); 
            box-shadow: 0 25px 45px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.2);
        }
        .glow-border { 
            box-shadow: 0 0 20px rgba(99, 102, 241, 0.4), 0 0 40px rgba(99, 102, 241, 0.2); 
            transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        }
        .glow-border:hover { 
            box-shadow: 0 0 30px rgba(99, 102, 241, 0.6), 0 0 60px rgba(99, 102, 241, 0.4), inset 0 1px 0 rgba(255,255,255,0.3);
            transform: translateY(-5px) scale(1.02);
        }
        .kpi-number { 
            background: linear-gradient(135deg, #6366f1, #8b5cf6); 
            -webkit-background-clip: text; 
            -webkit-text-fill-color: transparent; 
            background-clip: text;
            animation: countUp 2s ease-out;
        }
        @keyframes float { 
            0%, 100% { transform: translateY(0px) rotateX(0deg); } 
            50% { transform: translateY(-10px) rotateX(2deg); } 
        }
        .float { animation: float 6s ease-in-out infinite; }
        .fade-in { animation: fadeIn 1s ease-out; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
        .navbar { 
            background: linear-gradient(90deg, rgba(15,15,35,0.95), rgba(26,26,46,0.95)); 
            backdrop-filter: blur(30px); 
        }
        .sidebar { 
            background: rgba(26,26,46,0.9); 
            backdrop-filter: blur(20px); 
            transform: translateX(-100%); 
            transition: transform 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        }
        .sidebar.open { transform: translateX(0); }
        .dcc-control { 
            background: rgba(255,255,255,0.05) !important; 
            border: 1px solid rgba(255,255,255,0.1) !important; 
            border-radius: 12px !important; 
            color: white !important; 
            padding: 12px 16px !important; 
            font-weight: 500;
            transition: all 0.3s ease;
        }
        .dcc-control:hover { background: rgba(255,255,255,0.1) !important; }
        @media (max-width: 768px) { .grid-cols-3 { grid-template-columns: 1fr !important; } }
    </style>
</head>
<body>
    {%app_entry%}
    <footer>
        {%config%}
        {%scripts%}
        {%renderer%}
    </footer>
</body>
</html>
'''

app.layout = html.Div([
    # Futuristic Navbar
    html.Nav(className="navbar px-6 py-4 border-b border-white/10 sticky top-0 z-50 glass glow-border", children=[
        html.Div(className="max-w-7xl mx-auto flex items-center justify-between", children=[
            html.Div(className="flex items-center space-x-4", children=[
                html.Button(id="sidebar-toggle", className="p-2 glass rounded-xl glow-border hover:bg-white/10", children=[
                    html.I(className="fas fa-bars text-xl text-indigo-400")
                ]),
                html.Div(className="glass p-3 rounded-2xl glow-border", children=[
                    html.I(className="fas fa-chart-line text-2xl text-indigo-400 mr-3")
                ]),
                html.Div(children=[
                    html.H1("NEXUS ANALYTICS", className="text-2xl md:text-3xl font-bold bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent tracking-tight"),
                    html.P("Student Performance Intelligence Platform", className="text-white/60 text-sm font-medium")
                ])
            ]),
            html.Div(className="hidden md:flex items-center space-x-2 text-sm text-white/70", children=[
                html.Span("Live Data"),
                html.Div(className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse")
            ])
        ])
    ]),

    # Main Container
    html.Div(className="relative max-w-7xl mx-auto p-6 md:p-8 pb-20 space-y-8", children=[
        
        # Sidebar Filters
        html.Div(id="sidebar", className="sidebar fixed inset-y-0 left-0 z-40 w-80 glass p-8 pt-20 md:pt-8 float", children=[
            html.H3("Advanced Filters", className="text-xl font-bold mb-8 pb-4 border-b border-white/20"),
            html.Label("School", className="block text-sm font-semibold mb-2 text-white/90 uppercase tracking-wider"),
            dcc.Dropdown(id='school-filter', options=[
                {'label': 'All Schools', 'value': 'all'},
                {'label': 'Gabriel Pereira (GP)', 'value': 'GP'},
                {'label': 'Mousinho da Silveira (MS)', 'value': 'MS'}
            ], value='all', className='dcc-control w-full mb-6'),
            html.Label("Gender", className="block text-sm font-semibold mb-2 text-white/90 uppercase tracking-wider"),
            dcc.Dropdown(id='sex-filter', options=[
                {'label': 'All', 'value': 'all'},
                {'label': 'Female (F)', 'value': 'F'},
                {'label': 'Male (M)', 'value': 'M'}
            ], value='all', className='dcc-control w-full mb-6'),
            html.Label("Age Range", className="block text-sm font-semibold mb-2 text-white/90 uppercase tracking-wider"),
            dcc.RangeSlider(id='age-filter', min=14, max=25, step=1, value=[14, 25], 
                           marks={i: str(i) for i in range(14,26,2)}, className='dcc-control w-full h-3 mb-2',
                           tooltip={'placement': 'bottom', 'always_visible': True}),
            html.Div(id='filter-info', className='text-xs text-white/70 mt-4')
        ]),

        # Overlay for sidebar on mobile
        html.Div(id="overlay", className="fixed inset-0 bg-black/50 z-30 hidden md:hidden"),

        # Hero Title
        html.Div(className="text-center fade-in glass p-12 rounded-3xl glow-border float", children=[
            html.H2("Premium Student Performance Dashboard", className="text-4xl md:text-5xl font-black bg-gradient-to-r from-white via-indigo-100 to-purple-100 bg-clip-text text-transparent mb-4 tracking-tight"),
            html.P("Ultra-modern interactive analytics platform with real-time synchronized visualizations and glassmorphism design", className="text-xl text-white/70 max-w-2xl mx-auto leading-relaxed")
        ]),

        # KPI Cards Grid
        html.Div(className="grid grid-cols-1 md:grid-cols-3 gap-6 fade-in", children=[
            html.Div(id='kpi-total', className="glass p-8 rounded-3xl glow-border cursor-pointer"),
            html.Div(id='kpi-avg-g3', className="glass p-8 rounded-3xl glow-border cursor-pointer"),
            html.Div(id='kpi-avg-study', className="glass p-8 rounded-3xl glow-border cursor-pointer"),
        ]),

        # Charts Grid
        html.Div(className="grid grid-cols-1 lg:grid-cols-2 gap-8 fade-in", children=[
            html.Div(className="glass p-8 rounded-3xl glow-border", children=[
                html.H3("Final Grade Distribution (G3)", className="text-2xl font-bold mb-6 flex items-center"),
                html.I(className="fas fa-chart-histogram ml-3 text-indigo-400"),
                dcc.Graph(id='hist-g3', config={'displayModeBar': False})
            ]),
            html.Div(className="glass p-8 rounded-3xl glow-border", children=[
                html.H3("Study Time vs Final Grade", className="text-2xl font-bold mb-6 flex items-center"),
                html.I(className="fas fa-graduation-cap ml-3 text-purple-400"),
                dcc.Graph(id='scatter-study', config={'displayModeBar': False})
            ]),
            html.Div(className="glass p-8 rounded-3xl glow-border", children=[
                html.H3("Performance by Gender", className="text-2xl font-bold mb-6 flex items-center"),
                html.I(className="fas fa-venus-mars ml-3 text-pink-400"),
                dcc.Graph(id='box-gender', config={'displayModeBar': False})
            ]),
            html.Div(className="glass p-8 rounded-3xl glow-border", children=[
                html.H3("Absences vs Final Grade", className="text-2xl font-bold mb-6 flex items-center"),
                html.I(className="fas fa-clock ml-3 text-emerald-400"),
                dcc.Graph(id='bubble-absences', config={'displayModeBar': False})
            ]),
        ]),

        # Heatmap
        html.Div(className="glass p-8 rounded-3xl glow-border fade-in", children=[
            html.H3("Correlation Matrix", className="text-2xl font-bold mb-6 flex items-center"),
            html.I(className="fas fa-table-cells ml-3 text-yellow-400"),
            dcc.Graph(id='heatmap-corr', config={'displayModeBar': False})
        ]),

        # Data Insights
        html.Details(className="glass p-8 rounded-3xl glow-border fade-in", children=[
            html.Summary(className="text-xl font-bold mb-4 cursor-pointer p-4 rounded-2xl hover:bg-white/5", children=[
                html.I(className="fas fa-database mr-3 text-cyan-400"), "Dataset Insights & Statistics"
            ]),
            html.Div(id='data-insights')
        ])
    ]),

    # Footer
    html.Footer(className="glass p-8 mt-20 border-t border-white/10 text-center text-white/40 text-xs tracking-widest", children=[
        html.Div(className="max-w-7xl mx-auto", children=[
            html.P("© 2024 Nexus Analytics Platform | Powered by Dash & Plotly")
        ])
    ])
])

# Master callback for all updates
@callback(
    [Output('kpi-total', 'children'),
     Output('kpi-avg-g3', 'children'),
     Output('kpi-avg-study', 'children'),
     Output('hist-g3', 'figure'),
     Output('scatter-study', 'figure'),
     Output('box-gender', 'figure'),
     Output('bubble-absences', 'figure'),
     Output('heatmap-corr', 'figure'),
     Output('data-insights', 'children'),
     Output('filter-info', 'children')],
    [Input('school-filter', 'value'),
     Input('sex-filter', 'value'),
     Input('age-filter', 'value')]
)
def update_all(school, sex, age_range):
    filtered_df = df.copy()
    
    if school != 'all':
        filtered_df = filtered_df[filtered_df['school'] == school]
    if sex != 'all':
        filtered_df = filtered_df[filtered_df['sex'] == sex]
    if age_range:
        filtered_df = filtered_df[(filtered_df['age'] >= age_range[0]) & (filtered_df['age'] <= age_range[1])]

    n = len(filtered_df)
    if n == 0:
        return [html.H3("No data", className="text-4xl font-black text-gray-500 text-center py-20")] * 9 + ["No matches"]

    # KPIs
    total = n
    avg_g3 = filtered_df['G3'].mean()
    avg_study = filtered_df['studytime'].mean()

    def kpi_card(title, value, icon, color):
        return html.Div([
            html.Div(className="flex items-center justify-between mb-4", children=[
                html.Span(className="text-white/70 font-semibold uppercase tracking-wider text-sm", children=title),
                html.I(className=f"fas {icon} text-2xl text-{color}-400")
            ]),
            html.Div(value, className="kpi-number text-4xl md:text-5xl font-black mb-2"),
            html.Div(f"{value:.1f}", className="text-white/50 text-xl")
        ])

    # Custom theme
    theme_layout = {
        'margin': {'t': 20, 'b': 20, 'l': 20, 'r': 20},
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'font': {'family': 'Inter, sans-serif', 'color': '#e2e8f0'},
        'hoverlabel': {'bgcolor': 'rgba(99,102,241,0.9)', 'font': {'color': 'white'}}
    }

    # 1. Histogram with animation
    fig_hist = px.histogram(filtered_df, x='G3', nbins=25, 
                           color_discrete_sequence=['#6366f1'],
                           title="Interactive Distribution")
    fig_hist.update_traces(animation_frame=None)
    fig_hist.update_layout(**theme_layout, title_font_size=14)

    # 2. Scatter with trendline animation
    fig_scatter = px.scatter(filtered_df, x='studytime', y='G3', 
                            size='absences', color='sex',
                            trendline='ols', trendline_color_override='#10b981',
                            color_discrete_map={'F': '#f472b6', 'M': '#6366f1'},
                            title="Study vs Performance")
    fig_scatter.update_layout(**theme_layout, title_font_size=14)

    # 3. Boxplot violin
    fig_box = px.box(filtered_df, x='sex', y='G3', color='sex',
                     color_discrete_map={'F': '#f472b6', 'M': '#6366f1'},
                     title="Gender Performance")
    fig_box.update_traces(type='violin')
    fig_box.update_layout(**theme_layout, title_font_size=14)

    # 4. Bubble 3D effect
    fig_bubble = px.scatter(filtered_df, x='absences', y='G3', size='failures', 
                           color='G3', size_max=40,
                           color_continuous_scale='Viridis',
                           title="Absences Impact")
    fig_bubble.update_traces(marker=dict(line=dict(width=1, color='white')))
    fig_bubble.update_layout(**theme_layout, title_font_size=14)

    # 5. Full numeric corr heatmap
    numeric_cols = ['age', 'studytime', 'failures', 'absences', 'G1', 'G2', 'G3']
    corr = filtered_df[numeric_cols].corr()
    fig_heat = px.imshow(corr, color_continuous_scale='RdBu_r', aspect='auto',
                        title="Feature Correlations")
    fig_heat.update_layout(**theme_layout, title_font_size=14)

    # Data insights
    info = filtered_df.info()
    missing = filtered_df.isnull().sum().to_dict()
    stats = filtered_df.describe().round(2).to_html(classes='table-auto w-full text-xs')

    insights = html.Div([
        html.Div([
            html.P(f"Records: {n} | Columns: {len(filtered_df.columns)}", className="text-lg font-bold mb-4"),
            html.P(f"Missing values: {sum(filtered_df.isnull().sum())}", className="text-emerald-400 mb-6")
        ]),
        html.Details([html.Summary("Statistics", className="mb-4 cursor-pointer font-medium"), 
                     html.Div(html.Table(dangerously_set_innerHTML={'__html': stats}), className="overflow-x-auto")]),
        html.Details([html.Summary("Data Types"), 
                     html.Pre(str(filtered_df.dtypes), className="text-xs bg-black/20 p-4 rounded-xl mt-2 overflow-auto max-h-40")])
    ], className="space-y-4")

    filter_text = f"Showing {n} students (Age {age_range[0]}-{age_range[1]})"

    return (
        kpi_card("Total Students", total, "fa-users", "indigo"),
        kpi_card("Avg Final Grade", avg_g3, "fa-star", "purple"),
        kpi_card("Avg Study Hours", avg_study, "fa-book", "emerald"),
        fig_hist, fig_scatter, fig_box, fig_bubble, fig_heat,
        insights, filter_text
    )

# Sidebar toggle
@callback(
    [Output('sidebar', 'className'),
     Output('overlay', 'className')],
    [Input('sidebar-toggle', 'n_clicks')],
    prevent_initial_call=True
)
def toggle_sidebar(n):
    if n % 2 == 1:
        return "sidebar fixed inset-y-0 left-0 z-40 w-80 glass p-8 pt-20 md:pt-8 float open", "fixed inset-0 bg-black/50 z-30"
    return "sidebar fixed inset-y-0 left-0 z-40 w-80 glass p-8 pt-20 md:pt-8 float", "fixed inset-0 bg-black/50 z-30 hidden md:hidden"

if __name__ == '__main__':
    app.run_server(debug=False, host='127.0.0.1', port=8050)

