import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import plotly.graph_objs as go
import statsmodels.api as sm
import plotly.figure_factory as ff
import numpy as np
import json

mapbox_access_token = "pk.eyJ1IjoiYWxpY2hpbm8zNjkiLCJhIjoiY2t5OWtydWUwMDdmZzJxbzVlbXU5cW5yMiJ9.VAkAcACtyiKkMtEYydxdGg"

df = pd.read_excel('Data0113r.xls', dtype={"id": str})
df_scatter = pd.read_excel('Data0113r_c.xls', dtype={"id": str})

year_list = list(df['Year'].unique())
index_all_list = list(df.iloc[:, 1:31].columns)
index_all_list.remove("Alpha_code_2")
index_all_list.remove("Alpha_code_3")
index_list = ['Birth_rate_per_1K_people', 'CPI_(2010=100)', 'Freedom', 'Generosity', 'GDP_USD', 'GDP_per_capita_US$',
              'Gini', 'Health', 'Health_Life_Expectancy', 'Life_Expectancy', 'Life_Ladder', 'Log_GDP_per_capita_USD',
              'Negative_affect', 'Perceptions_of_Corruption', 'Population', 'Positive_affect', 'Sex_Ratio',
              'Social_Trust', 'Social_Support', 'Wage']
unity_list = ["EU", "G20", "APEC", "OECD", "Asia", "Europe", "Africa", "Oceania", "North America", "South America"]
# clusters = pd.read_csv("final_clusters.csv")
# box_cluster = pd.read_csv("box_cluster.csv")

with open("countries.geojson") as fdata:
    country_polygon = json.load(fdata)


layout = dict(
    autosize=True,
    # automargin=True,
    margin=dict(l=30, r=30, b=20, t=40),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation="h"),
    title="Satellite Overview",
    mapbox=dict(
        accesstoken=mapbox_access_token,
        style="light",
        # mapbox://styles/plotlymapbox/cjvprkf3t1kns1cqjxuxmwixz
        # center=dict(lon=-78.05, lat=42.54),
        zoom=5,
    ),
)

# design for mapbox
bgcolor = "#f3f3f1"  # mapbox light map land color
row_heights = [150, 500, 300]
template = {"layout": {"paper_bgcolor": bgcolor, "plot_bgcolor": bgcolor}}


def blank_fig(height):
    """
    Build blank figure with the requested height
    """
    return {
        "data": [],
        "layout": {
            "height": height,
            "template": template,
            "xaxis": {"visible": False},
            "yaxis": {"visible": False},
        },
    }


columns = df.iloc[:, 2:25].columns

# Create controls
# behaviour_options = [
#    dict(label=country, value=country)
#   for country in columns]

dropdown_index = dcc.Dropdown(
    # id='nutrition_types',
    id="index_type",
    options=[{'label': i, 'value': i} for i in index_list],
    value="Population",
    className="pretty_container eleven columns",
)

dropdown_index2 = dcc.Dropdown(
    # id='nutrition_types',
    id="index_type_sec2",
    options=[{'label': i, 'value': i} for i in index_list],
    value='Population',
    className="pretty_container sixish columns",
)

dropdown_year = dcc.Dropdown(
    # id='nutrition_types',
    id="year_selection",
    options=[{'label': i, 'value': i} for i in year_list],
    value=2020,
    className="pretty_container eleven columns",
)

dropdown_unity = dcc.Dropdown(
    # id='nutrition_types',
    id="unity_selection",
    options=[{'label': i, 'value': i} for i in unity_list],
    placeholder="Select Unity",
    className="pretty_container sixish columns",
    value='EU',
)

slider_year = dcc.Slider(
    id='year_slider',
    min=min(year_list),
    max=max(year_list),
    value=min(year_list),
    marks={
        str(year): {
            "label": str(year),
            "style": {"color": "#7fafdf"},
        }
        for year in year_list
    }
)

corr_options = [
    dict(label=country, value=country)
    for country in index_list]
cor_behav = dcc.Dropdown(
    id='cor_behave',
    options=corr_options,
    value="Gini"  # ,
    # labelStyle={'display': 'block', "text-align": "justify"}
)

app = dash.Dash(__name__)

# Create app layout
app.layout = html.Div(
    [
        dcc.Store(id="aggregate_data"),
        # empty Div to trigger javascript file for graph resizing
        html.Div(id="output-clientside"),
        html.Div(
            [
                html.Div(
                    [
                        html.Img(
                            src=app.get_asset_url("logo.png"),
                            id="plotly-image",
                            style={
                                "height": "60px",
                                "width": "auto",
                                "margin-bottom": "25px",
                            },
                        )
                    ],
                    className="one-third column",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H4(
                                    "Multiple Indicators of Countries by Year",
                                    style={"font-weight": "bold"},
                                ),
                                html.H5(
                                    "Analysis of the relationship between indicators and within the countries",
                                    style={"margin-top": "0px"}
                                ),
                            ]
                        )
                    ],
                    className="three column",
                    id="title",
                ),
                html.Div(
                    # create empty div for align center
                    className="one-third column",
                ),
            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "25px"},
        ),
        html.Div(
            [
                html.Div(
                    [

                        html.H6("Multiple Indicators",
                                style={"margin-top": "0", "font-weight": "bold", "text-align": "center"}),

                        html.P(
                            "Indicator can help us realizing the world better. "
                            "There are multiple indexes in our best-pick list. "
                            "Choose an Indicator and a Year to observe how the world is changing.",
                            className="control_label", style={"text-align": "justify"}
                        ),
                        html.P(),

                        html.Div([
                            html.P("Select a Year", className="control_label",
                                   style={"text-align": "center", "font-weight": "bold"}),
                            dropdown_year
                        ]),

                        html.Div([
                            html.P("Select an Indicator", className="control_label",
                                   style={"text-align": "center", "font-weight": "bold"}),
                            dropdown_index,
                            ]),
                    ],
                    className="pretty_container four columns",
                    id="cross-filter-options",
                    style={"text-align": "justify"},

                ),

                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.P(id="well_text"),
                                        html.P("Maximum", style={"text-align": "center", "font-weight": "bold"}),
                                        html.P(id="max_name", style={"text-align": "center"}),
                                        html.P(id="max_value", style={"text-align": "center"}),
                                    ],
                                    className="mini_container",
                                    id="wells",
                                ),
                                html.Div(
                                    [html.P(id="gasText"),
                                     html.P("Minimum", style={"text-align": "center", "font-weight": "bold"}),
                                     html.P(id="min_name", style={"text-align": "center"}),
                                     html.P(id="min_value", style={"text-align": "center"}),
                                     ],
                                    className="mini_container",
                                    id="gas"
                                ),
                                html.Div(
                                    [html.P(id="oilText"),
                                     html.P("Mean", style={"text-align": "center", "font-weight": "bold"}),
                                     html.P(id="mean", style={"text-align": "center"}),
                                     html.P("Standard deviation",
                                            style={"text-align": "center", "font-weight": "bold"}),
                                     html.P(id="st_dev", style={"text-align": "center"})],
                                    # ,
                                    className="mini_container",
                                    id="oil",
                                ),
                            ],
                            id="info-container",
                            className="row container-display",
                        ),
                        html.Div(
                            [dcc.Graph(id="choropleth")],
                            # id="countGraphContainer",
                            className="pretty_container",
                        ),
                    ],
                    id="right-column",
                    className="eight columns",
                ),
            ],
            className="row flex-display",
        ),

        html.Div(
            [
                html.H6("General Indicator information in different Union / Continent",
                        style={"margin-top": "0", "font-weight": "bold", "text-align": "center"}),
                html.P(
                    "We selected multiple union like Europe-Union, G20 and OECD etc. "
                    "Watch how histogram change with your selection! ",
                    className="control_label", style={"text-align": "center"}),
                html.P(id="slider-text", children="Drag the slider to change the year:",
                       style={"text-align": "center"}),
                slider_year,
                dropdown_index2,
                dropdown_unity,

                html.Div([dcc.Graph(id="histogram")], className="pretty_container twelve columns"),

            ],
            className="row pretty_container",
        ),

        html.Div(
            [
                html.Div(
                    # cor_behav,

                    [
                        html.H6("Exploring correlations",
                                style={"margin-top": "0", "font-weight": "bold", "text-align": "center"}),
                        html.P(
                            "In the heatmap below, the correlations in indicators can be explored.",
                            className="control_label", style={"text-align": "justify"}),
                        # html.P("""<br>"""),
                        html.P("Select an Indicator", style={"font-weight": "bold", "text-align": "center"}),
                        cor_behav,

                        html.Div([dcc.Graph(id="cor_ma")], className="pretty_container twelve columns"),
                    ],  # ,cor_behav,
                    className="pretty_container four columns",

                ),

                html.Div(
                    [html.H6("Analysing the correlations between Indicators",
                             style={"margin-top": "0", "font-weight": "bold", "text-align": "center"}),
                     html.P(
                         "Below, the correlations can be analysed in more detail. \
                         It is important to note that correlation in this case does not necessarily mean causation.",
                         className="control_label", style={"text-align": "justify"}),

                     html.Div([
                         html.P("Select an Indicator", className="control_label",
                                style={"font-weight": "bold", "text-align": "center"}),
                         dcc.Dropdown(
                             id='xaxis-column',
                             options=[{'label': i, 'value': i} for i in index_list],
                             value="Gini"  # ,className="pretty_container four columns",
                         ),
                         dcc.RadioItems(
                             id='xaxis-type',
                             options=[{'label': i, 'value': i} for i in ['Box', 'Violin']],
                             value='Box',
                             labelStyle={'display': 'inline-block'},  # ,className="pretty_container four columns",
                             style={"padding-left": "34%"}
                         ),
                     ], className="pretty_container sixish columns", ),

                     html.Div([
                         html.P("Select another Indicator", className="control_label",
                                style={"font-weight": "bold", "text-align": "center"}),
                         dcc.Dropdown(
                             id='yaxis-column',
                             options=[{'label': i, 'value': i} for i in index_list],
                             value='Social_Trust'
                         ),
                         dcc.RadioItems(
                             id='yaxis-type',
                             options=[{'label': i, 'value': i} for i in ['Box', 'Violin']],
                             value='Box',
                             labelStyle={'display': 'inline-block'},
                             style={"padding-left": "34%"}
                         ),
                     ], className="pretty_container sixish columns", ),

                     html.Div([
                         html.P("Select Scatter Indicator", className="control_label",
                                style={"font-weight": "bold", "text-align": "center"}),
                         dcc.Dropdown(
                             id="scatter_size",
                             options=[{'label': i, 'value': i} for i in index_list],
                             value='Population'
                         ),
                     ], className="pretty_container twelve columns", ),

                     html.Div([
                         dcc.Graph(id="indicator-graphic"),
                     ], className="pretty_container almost columns", ),
                     ],

                    className="pretty_container eight columns",
                ),

            ],
            className="row flex-display",
        ),
        html.Div(
            [
                html.H6("Authors", style={"margin-top": "0", "font-weight": "bold", "text-align": "center"}),

                html.P(
                    """
                    Authors: 09770004 Mr.Chen/ 09770006 Miss.Lo / 09770010 Miss.Kao/ 09770023 Mr.Haung/ 09770024 Mr.Lo
                    """,
                    style={"text-align": "center", "font-size": "12pt"}
                ),
                html.P(
                    "Organization: Development of Big Data Management, SooChow University",
                    style={"text-align": "center", "font-size": "12pt"},
                )

            ],
            className="row pretty_container",
        ),
    ],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"},
)

colors = ['#0d0887', '#46039f', '#7201a8', '#9c179e', '#bd3786', '#d8576b', '#ed7953', '#fb9f3a', '#fdca26', '#f0f921']
colors2 = ['#fdca26', '#ed7953', '#bd3786', '#7201a8', '#0d0887']


####
@app.callback(
    Output("choropleth", "figure"),
    [Input("year_selection", "value"), Input("index_type", "value")])
def display_choropleth(year, indextype):
    df_fig = df.loc[df['Year'] == year]
    fig = px.choropleth_mapbox(
        df_fig, geojson=country_polygon, color=indextype, featureidkey="properties.ISO_A3", # color_continuous_scale=,
        locations="Alpha_code_3",  hover_name="CountryName", opacity=0.7,  # hover_data = [],
        #center={"lat": 56.5, "lon": 11},
        zoom=1)
    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        mapbox_accesstoken=mapbox_access_token)

    return fig

# update histogram
@app.callback(
    Output("histogram", "figure"),
    [Input("index_type_sec2", "value"),
     Input("unity_selection", "value"),
     Input("year_slider", "value")])
def update_histogram(ind, uni, year):

    # [xVal, yVal, colorVal] = get_selection(monthPicked, dayPicked, selection)
    his_df_y = df.loc[df['Year'] == year]
    his_df_yu = his_df_y.loc[his_df_y[uni] == 1]
    his_df = his_df_yu[[ind, "CountryName"]]
    xval = his_df["CountryName"]
    yval = his_df[ind]

    layout = go.Layout(
        bargap=0.01,
        bargroupgap=0,
        barmode="group",
        margin=go.layout.Margin(l=10, r=0, t=0, b=50),
        showlegend=False,
        plot_bgcolor="white",
        paper_bgcolor="white",
        dragmode="select",
        font=dict(color="black"),
        xaxis=dict(
            range=[0, [len(his_df['CountryName'])+1]],
            showgrid=False,
            tickmode="auto",
            fixedrange=True,
        ),
        yaxis=dict(
            range=[0, [np.nanmax(his_df[ind])+5]],
            showticklabels=False,
            showgrid=False,
            fixedrange=True,
            rangemode="nonnegative",
            zeroline=False,
        ),
        #annotations=[
        #    dict(
        #        x=xi,
                #y=yi,
                #text=str(yi),
        #        xanchor="auto",
                #yanchor="auto",
        #        showarrow=False,
        #        font=dict(color="black"),
        #    )
        #    for xi, yi in zip(xval, yval)
        #],
    )

    return go.Figure(
        data=[
            go.Bar(x=xval, y=yval, hoverinfo="x+y", marker=dict(color='#7fafdf')),
            go.Scatter(
                opacity=0,
                x=xval,
                y=yval / 2,
                hoverinfo="none",
                mode="markers",
                marker=dict(color='#fdca26', symbol="square", size=40),
                visible=True,
            ),
        ],
        layout=layout,
    )


## FF ##
@app.callback(
    Output("cor_ma", "figure"),
    [Input("cor_behave", "value")])
def display_cor_ma(var):
    index_list = ['Birth_rate_per_1K_people', 'CPI_(2010=100)', 'Freedom', 'Generosity', 'GDP_USD',
                  'GDP_per_capita_US$', 'Gini', 'Health', 'Health_Life_Expectancy', 'Life_Expectancy', 'Life_Ladder',
                  'Log_GDP_per_capita_USD', 'Negative_affect', 'Perceptions_of_Corruption', 'Population',
                  'Positive_affect', 'Sex_Ratio', 'Social_Trust', 'Social_Support', 'Wage']

    index_listr = ['Wage', 'Social_Support', 'Social_Trust', 'Sex_Ratio', 'Positive_affect',
                   'Population', 'Perceptions_of_Corruption', 'Negative_affect', 'Log_GDP_per_capita_USD',
                   'Life_Ladder','Life_Expectancy', 'Health_Life_Expectancy', 'Health', 'Gini', 'GDP_per_capita_US$',
                   'GDP_USD', 'Generosity', 'Freedom', 'CPI_(2010=100)', 'Birth_rate_per_1K_people']

    df_corr_r = df_scatter[index_list]
    df_corr_round = df_corr_r.corr()[[var]].T[index_listr].T.round(2)
    fig_cor = ff.create_annotated_heatmap(
        z=df_corr_round.to_numpy(),
        x=df_corr_round.columns.tolist(),
        y=df_corr_round.index.tolist(),
        zmax=1, zmin=-1,
        showscale=True,
        hoverongaps=True,
        ygap=3,
    )
    fig_cor.update_layout(yaxis=dict(showgrid=False), xaxis=dict(showgrid=False),

                          legend=dict(
                              orientation="h",
                              yanchor="bottom",
                              y=1.02,
                              xanchor="right",
                              x=1
                          ))
    # fig_cor.update_layout(yaxis_tickangle=-45)
    fig_cor.update_layout(xaxis_tickangle=0)
    fig_cor.update_layout(title_text='', height=550)  #

    return fig_cor


## FF ##

@app.callback(
    [
        Output("max_name", "children"),
        Output("max_value", "children"),
        Output("min_name", "children"),
        Output("min_value", "children"),
        Output("mean", "children"),
        Output("st_dev", "children"),
    ],
    [
        Input("year_selection", "value"),
        Input("index_type", "value"),
    ]
)
def indicator(year, auswahl):
    df1 = df.loc[df["Year"] == year]
    max_id = df1[auswahl].idxmax()
    min_id = df1[auswahl].idxmin()

    max_value = df1[auswahl].max()
    max_value = str(max_value)

    max_name = df1.loc[max_id, 'CountryName']
    min_value = df1[auswahl].min()
    min_value = str(min_value)

    min_name = df1.loc[min_id, 'CountryName']
    mean = df1[auswahl].mean()
    st_dev = df1[auswahl].std()
    st_dev = round(st_dev, 2)
    st_dev = str(st_dev)
    mean = round(mean, 2)
    mean = str(mean)

    return "Country: " + max_name, max_value, \
           "Country: " + min_name, min_value, \
           mean + " per country", \
           st_dev + " per country"


@app.callback(
    Output('indicator-graphic', 'figure'),
    [
        Input('xaxis-column', 'value'),
        Input('yaxis-column', 'value'),
        Input('xaxis-type', 'value'),
        Input('yaxis-type', 'value'),
        Input('scatter_size', 'value'),
        # Input('sct_year_selection', 'value')
    ]
)
def update_graph(xaxis_column_name, yaxis_column_name, xaxis_type, yaxis_type, scattersize):
    # col_name = str(yaxis_column_name) + " (above Average)"
    # df_scatter_1 = df_scatter.loc[df_scatter['Year'] == year]
    df_scatter1 = df_scatter.dropna(subset=[xaxis_column_name, yaxis_column_name, scattersize])
    col_name = " "
    df_scatter1[col_name] = (df_scatter1[yaxis_column_name] > df_scatter1[yaxis_column_name].mean(skipna=True))

    def aa(inp):
        if inp == True:
            return yaxis_column_name + " above average"
        else:
            return yaxis_column_name + " below average"

    df_scatter1[col_name] = df_scatter1[col_name].apply(aa)

    if yaxis_type == "Box":
        type_y = "box"
    else:
        type_y = "violin"

    if xaxis_type == "Box":
        type_x = "box"
    else:
        type_x = "violin"

    fig = px.scatter(df_scatter1, x=xaxis_column_name, y=yaxis_column_name, size=scattersize, color=col_name,
                     hover_name="CountryName",
                     log_x=False, marginal_x=type_x, marginal_y=type_y, template="simple_white",
                     color_discrete_sequence=["#0d0887", "#9c179e"])

    # linear regression
    regline = sm.OLS(df_scatter1[yaxis_column_name], sm.add_constant(df_scatter1[xaxis_column_name])).fit().fittedvalues


    # add linear regression line for whole sample
    fig.add_traces(go.Scatter(x=df_scatter1[xaxis_column_name], y=regline,
                              mode='lines',
                              marker_color='#fb9f3a',
                              name='OLS Trendline')
                   )

    fig.update_layout(legend=dict(orientation="h", xanchor='center', x=0.5, yanchor='top', y=-0.2))

    fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')

    # fig.update_xaxes(title=xaxis_column_name,
    #                type='linear' if xaxis_type == 'Linear' else 'log')

    # fig.update_yaxes(title=yaxis_column_name,
    #                type='linear' if yaxis_type == 'Linear' else 'log')

    return fig


server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)





