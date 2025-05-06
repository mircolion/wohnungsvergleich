import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import datetime
import os

# CSV mit Bezirken & Preisen laden
bezirke_df = pd.read_csv("bezirke_ag_so_immobilienpreise.csv")
bezirksnamen = bezirke_df["Bezirk"].sort_values().tolist()

# Sanierungsmaßnahmen und deren geschätzte Wertsteigerung in Prozent
sanierungsmassnahmen = {
    'Küche': 5,
    'Bad': 10,
    'Fenster': 5,
    'Heizung': 5,
    'Dach': 5,
    'Fassade': 5
}

# Aktuelles Jahr einmal speichern
current_year = datetime.datetime.now().year

# App initialisieren
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Wohnungsvergleich"

background_style = {
    "backgroundImage": "url('https://raw.githubusercontent.com/mircolion/wohnungsvergleichmodica/main/woods.jpg')",
    "backgroundSize": "cover",
    "backgroundRepeat": "no-repeat",
    "backgroundPosition": "center",
    "minHeight": "100vh",
    "padding": "30px",
    "fontFamily": "Arial Narrow",
    "backgroundColor": "rgba(255, 255, 255, 0.25)",
    "backgroundBlendMode": "lighten"
}

# App Layout
app.layout = html.Div(style=background_style, children=[
    html.Div(style={
        "backgroundColor": "rgba(255,255,255,0.85)",
        "borderRadius": "12px",
        "padding": "20px"
    }, children=[
        dbc.Container([
            html.H1("Wohnungsbewertung"),
            html.Hr(),

            dbc.Row([
                dbc.Col([
                    dbc.Label("Bezirk wählen"),
                    dcc.Dropdown(
                        id='bezirk',
                        options=[{"label": name, "value": name} for name in bezirksnamen],
                        placeholder="Bezirk auswählen"
                    )
                ])
            ]),

            html.Br(),

            dbc.Row([
                dbc.Col([
                    dbc.Label("Zimmeranzahl"),
                    dcc.Dropdown(
                        id='zimmer',
                        options=[{"label": str(z), "value": z} for z in [1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5]],
                        value=2.5,
                        placeholder="Zimmeranzahl auswählen"
                    )
                ]),
                dbc.Col([
                    dbc.Label("Fläche (m²)"),
                    dbc.Input(id='flaeche', type='number', value=60)
                ])
            ]),

            html.Br(),

            dbc.Row([
                dbc.Col([dbc.Label("Baujahr"), dbc.Input(id='baujahr', type='number', value=1980)]),
                dbc.Col([
                    dbc.Label("Glasfaser vorhanden"),
                    dbc.Checklist(
                        options=[{"label": "Ja", "value": 1}],
                        value=[], id="glasfaser", switch=True
                    )
                ]),
                dbc.Col([dbc.Label("Anzahl Eigentümer"), dbc.Input(id='eigentumer', type='number', value=10)])
            ]),

            html.Br(),

            dbc.Row([
                dbc.Col([dbc.Label("Renovationsfonds (CHF)"), dbc.Input(id='renovationsfonds', type='number', value=0)])
            ]),

            html.Br(),

            dbc.Row([
                dbc.Col([
                    dbc.Label("Waschküche"),
                    dcc.Dropdown(
                        id='waschkueche',
                        options=[
                            {"label": "In Wohnung individuell", "value": "wohnung"},
                            {"label": "Geteilte Waschküche", "value": "geteilt"},
                            {"label": "Eigene Waschküche", "value": "eigen"}
                        ],
                        placeholder="Waschküche auswählen"
                    )
                ]),
                dbc.Col([
                    dbc.Label("Parkplatzsituation"),
                    dcc.Dropdown(
                        id='parkplatz',
                        options=[
                            {"label": "Kein Parkplatz", "value": "kein"},
                            {"label": "Tiefgaragenparkplatz", "value": "tiefgarage"},
                            {"label": "Aussenparkplatz", "value": "aussen"}
                        ],
                        placeholder="Parkplatz auswählen"
                    )
                ])
            ]),

            html.Br(),

            dbc.Row([
                dbc.Col([
                    dbc.Label("Kellerabteil"),
                    dcc.Dropdown(
                        id='keller',
                        options=[
                            {"label": "Kein Kellerabteil", "value": "kein"},
                            {"label": "Geteilt und abgegrenzt", "value": "geteilt"},
                            {"label": "Eigenes Kellerabteil", "value": "eigen"}
                        ],
                        placeholder="Kellerabteil auswählen"
                    )
                ]),
                dbc.Col([
                    dbc.Label("Estrich"),
                    dcc.Dropdown(
                        id='estrich',
                        options=[
                            {"label": "Kein Estrich", "value": "kein"},
                            {"label": "Estrich vorhanden", "value": "vorhanden"}
                        ],
                        placeholder="Estrich auswählen"
                    )
                ])
            ]),

            html.Hr(),
            html.H4("Sanierungsmaßnahmen"),

            html.Div([
                dbc.Row([
                    dbc.Col([
                        dbc.Checklist(
                            options=[{"label": maßnahme, "value": maßnahme}],
                            value=[], id=f"{maßnahme.lower()}_check", inline=True
                        ),
                        dbc.Input(
                            id=f"{maßnahme.lower()}_jahr", type='number',
                            placeholder='Jahr', min=1900, max=current_year
                        )
                    ], width=6)
                    for maßnahme in sanierungsmassnahmen.keys()
                ])
            ]),

            html.Br(),
            dbc.Button("Preis berechnen", id='berechne', color='success', style={"fontFamily": "Arial Narrow"}),
            html.Br(), html.Br(),
            html.Div(id='ergebnis')
        ])
    ])
])

@app.callback(
    Output('ergebnis', 'children'),
    Input('berechne', 'n_clicks'),
    State('bezirk', 'value'),
    State('zimmer', 'value'),
    State('flaeche', 'value'),
    State('baujahr', 'value'),
    State('glasfaser', 'value'),
    State('eigentumer', 'value'),
    State('renovationsfonds', 'value'),
    State('waschkueche', 'value'),
    State('parkplatz', 'value'),
    State('keller', 'value'),
    State('estrich', 'value'),
    *[State(f"{maßnahme.lower()}_check", 'value') for maßnahme in sanierungsmassnahmen.keys()],
    *[State(f"{maßnahme.lower()}_jahr", 'value') for maßnahme in sanierungsmassnahmen.keys()]
)
def berechne_preis(n_clicks, bezirk, zimmer, flaeche, baujahr, glasfaser, eigentumer, renovationsfonds,
                   waschkueche, parkplatz, keller, estrich, *args):

    if not n_clicks or bezirk is None:
        return ""

    if flaeche is None or flaeche <= 0:
        return html.Div("⚠️ Fläche muss grösser als 0 sein.")

    if baujahr is None or baujahr < 1800 or baujahr > current_year:
        return html.Div("⚠️ Ungültiges Baujahr.")

    zeile_df = bezirke_df[bezirke_df["Bezirk"] == bezirk]
    if zeile_df.empty:
        return html.Div("⚠️ Bezirk nicht gefunden.")

    basispreis = zeile_df["Preis pro m² (CHF)"].values[0]
    alter = current_year - baujahr
    abzug = 0.2 if alter > 30 else 0
    glasfaser_bonus = 0.05 if glasfaser else 0

    sanierungsboni = 0
    for i, maßnahme in enumerate(sanierungsmassnahmen.keys()):
        check = args[i]
        jahr = args[i + len(sanierungsmassnahmen)]
        if check and jahr:
            alter_sanierung = current_year - jahr
            if alter_sanierung <= 10:
                sanierungsboni += sanierungsmassnahmen[maßnahme] / 100

    fonds_bonus = min(renovationsfonds / 10000, 0.1)

    zusatz_bonus = 0
    if waschkueche == "wohnung":
        zusatz_bonus += 0.05
    elif waschkueche == "eigen":
        zusatz_bonus += 0.03

    if parkplatz == "tiefgarage":
        zusatz_bonus += 0.05
    elif parkplatz == "aussen":
        zusatz_bonus += 0.02

    if keller == "eigen":
        zusatz_bonus += 0.03
    elif keller == "geteilt":
        zusatz_bonus += 0.01

    if estrich == "vorhanden":
        zusatz_bonus += 0.02

    zimmer_bonus = 0.01 * (zimmer - 2.5)  # z. B. +1% je Zimmer über 2.5

    gesamt_bonus = -abzug + glasfaser_bonus + sanierungsboni + fonds_bonus + zusatz_bonus + zimmer_bonus
    preis_pro_m2 = basispreis * (1 + gesamt_bonus)
    gesamtpreis = preis_pro_m2 * flaeche

    return html.Div([
        html.H5(f"Geschätzter Preis pro m²: {preis_pro_m2:.2f} CHF"),
        html.H5(f"Geschätzter Gesamtpreis: {gesamtpreis:.2f} CHF")
    ])

# App starten
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 8050)))
