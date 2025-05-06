import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import datetime

# App-Initialisierung mit Bootstrap-Theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Sanierungsmaßnahmen und deren geschätzte Wertsteigerung in Prozent
sanierungsmassnahmen = {
    'Küche': 5,
    'Bad': 10,
    'Fenster': 5,
    'Heizung': 5,
    'Dach': 5,
    'Fassade': 5
}

# Layout der App mit Formularfeldern und Checklisten
app.layout = dbc.Container([
    html.H1("Wohnungsvergleich mit Sanierungsbewertung"),
    html.Hr(),

    # Erste Eingabereihe: Ort, Zimmeranzahl, Fläche
    dbc.Row([
        dbc.Col([dbc.Label("Ort"), dbc.Input(id='ort', type='text', placeholder='z.B. Basel')]),
        dbc.Col([
            dbc.Label("Zimmeranzahl"),
            dcc.Slider(
                id='zimmer', min=1, max=3.5, step=0.5, value=2.5,
                marks={i: str(i) for i in [1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5]}
            )
        ]),
        dbc.Col([dbc.Label("Fläche (m²)"), dbc.Input(id='flaeche', type='number', value=60)])
    ]),

    html.Br(),

    # Zweite Eingabereihe: Baujahr, Glasfaser, Eigentümer
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

    html.Hr(),
    html.H4("Sanierungsmaßnahmen"),

    # Eingabe für jede Sanierungsmaßnahme: Checkbox + Jahr
    html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Checklist(
                    options=[{"label": maßnahme, "value": maßnahme}],
                    value=[], id=f"{maßnahme.lower()}_check", inline=True
                ),
                dbc.Input(
                    id=f"{maßnahme.lower()}_jahr", type='number',
                    placeholder='Jahr', min=1900, max=datetime.datetime.now().year
                )
            ]) for maßnahme in sanierungsmassnahmen.keys()
        ])
    ]),

    html.Br(),
    dbc.Button("Preis berechnen", id='berechne', color='primary'),
    html.Br(), html.Br(),
    html.Div(id='ergebnis')
])

# Callback-Funktion zur Preisberechnung bei Buttonklick
@app.callback(
    Output('ergebnis', 'children'),
    Input('berechne', 'n_clicks'),
    State('flaeche', 'value'),
    State('baujahr', 'value'),
    State('glasfaser', 'value'),
    State('eigentumer', 'value'),
    *[State(f"{maßnahme.lower()}_check", 'value') for maßnahme in sanierungsmassnahmen.keys()],
    *[State(f"{maßnahme.lower()}_jahr", 'value') for maßnahme in sanierungsmassnahmen.keys()]
)
def berechne_preis(n_clicks, flaeche, baujahr, glasfaser, eigentumer, *args):
    if n_clicks is None:
        return ""

    # Basispreis/m²
    basispreis = 4000

    # Alter berechnen
    alter = datetime.datetime.now().year - baujahr
    abzug = 0.2 if alter > 30 else 0  # Abschlag bei alten Wohnungen

    # Glasfaserbonus
    glasfaser_bonus = 0.05 if glasfaser else 0

    # Sanierungsboni berechnen
    sanierungsboni = 0
    for i, maßnahme in enumerate(sanierungsmassnahmen.keys()):
        check = args[i]
        jahr = args[i + len(sanierungsmassnahmen)]
        if check and jahr:
            alter_sanierung = datetime.datetime.now().year - jahr
            if alter_sanierung <= 10:
                sanierungsboni += sanierungsmassnahmen[maßnahme] / 100

    # Endpreis berechnen
    preis_pro_m2 = basispreis * (1 - abzug + glasfaser_bonus + sanierungsboni)
    gesamtpreis = preis_pro_m2 * flaeche

    return html.Div([
        html.H5(f"Geschätzter Preis pro m²: {preis_pro_m2:.2f} CHF"),
        html.H5(f"Geschätzter Gesamtpreis: {gesamtpreis:.2f} CHF")
    ])

# App starten
import os

if __name__ == '__main__':
    app.run(
        debug=False,
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 8050))
    )
