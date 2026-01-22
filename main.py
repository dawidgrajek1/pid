"""
PCR Thermocycler Simulation Dashboard
Interactive web application for simulating PCR thermocycler with PID control.
"""

import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from fuzzy_controller import FuzzyController

from thermal_model import ThermalModel
from pid_controller import PIDController
from pcr_simulator import PCRSimulator
import config


# Initialize Dash app with Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "PCR Thermocycler Simulator"


# Layout
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1("PCR Thermocycler Simulator", className="text-center mb-4 mt-4")
        ])
    ]),
    
    # Parameter Cards Row 1
    dbc.Row([
        # Thermal System Parameters
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("Thermal System")),
                dbc.CardBody([
                    dbc.Label("Heat Capacity (J/K)"),
                    dbc.Input(
                        id="heat-capacity",
                        type="number",
                        value=config.THERMAL_HEAT_CAPACITY,
                        min=config.HEAT_CAPACITY_MIN,
                        max=config.HEAT_CAPACITY_MAX,
                        step=10,
                    ),
                    html.Small("Total heat capacity of block + samples", className="text-muted d-block mb-2"),
                    
                    dbc.Label("Heating Power (W)", className="mt-3"),
                    dbc.Input(
                        id="heating-power",
                        type="number",
                        value=config.HEATING_POWER,
                        min=config.POWER_MIN,
                        max=config.POWER_MAX,
                        step=10,
                    ),
                    html.Small("Maximum heating power", className="text-muted d-block mb-2"),
                    
                    dbc.Label("Cooling Power (W)", className="mt-3"),
                    dbc.Input(
                        id="cooling-power",
                        type="number",
                        value=config.COOLING_POWER,
                        min=config.POWER_MIN,
                        max=config.POWER_MAX,
                        step=10,
                    ),
                    html.Small("Maximum cooling power", className="text-muted d-block mb-2"),
                    
                    dbc.Label("Heat Loss Coefficient (W/K)", className="mt-3"),
                    dbc.Input(
                        id="heat-loss",
                        type="number",
                        value=config.HEAT_LOSS_COEF,
                        min=config.HEAT_LOSS_MIN,
                        max=config.HEAT_LOSS_MAX,
                        step=0.1,
                    ),
                    html.Small("Heat loss to ambient", className="text-muted d-block mb-2"),
                    
                    dbc.Label("Ambient Temperature (°C)", className="mt-3"),
                    dbc.Input(
                        id="ambient-temp",
                        type="number",
                        value=config.AMBIENT_TEMP,
                        min=0,
                        max=40,
                        step=1,
                    ),
                    html.Small("Room temperature", className="text-muted d-block"),
                ]),
            ], className="mb-3"),
        ], md=3),

        # Sample Properties
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("Sample Properties")),
                dbc.CardBody([
                    dbc.Label("Volume (mL)"),
                    dbc.Input(
                        id="sample-volume",
                        type="number",
                        value=round(config.SAMPLE_VOLUME * 1e6, 1),  # Convert to mL
                        min=round(config.VOLUME_MIN * 1e6, 1),
                        max=round(config.VOLUME_MAX * 1e6, 1),
                        step=0.1,
                        inputMode="decimal",
                        persistence=True,
                    ),
                    html.Small("Total sample volume", className="text-muted d-block mb-2"),
                    
                    dbc.Label("Density (kg/m³)", className="mt-3"),
                    dbc.Input(
                        id="sample-density",
                        type="number",
                        value=config.SAMPLE_DENSITY,
                        min=800,
                        max=1200,
                        step=10,
                    ),
                    html.Small("Typically ~1000 for aqueous solutions", className="text-muted d-block mb-2"),
                    
                    dbc.Label("Specific Heat (J/(kg·K))", className="mt-3"),
                    dbc.Input(
                        id="sample-specific-heat",
                        type="number",
                        value=config.SAMPLE_SPECIFIC_HEAT,
                        min=2000,
                        max=5000,
                        step=100,
                    ),
                    html.Small("Typically ~4100 for water-based PCR mix", className="text-muted d-block"),
                ]),
            ], className="mb-3"),
        ], md=3),

        # PID Parameters
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("PID Controller")),
                dbc.CardBody([
                    dbc.Label("Proportional Gain (Kp)"),
                    dbc.Input(
                        id="pid-kp",
                        type="number",
                        value=config.PID_KP,
                        min=config.PID_KP_MIN,
                        max=config.PID_KP_MAX,
                        step=1,
                    ),
                    html.Small("Proportional gain (typical: 50-150)", className="text-muted d-block mb-2"),
                    
                    dbc.Label("Integration Time Ti (s)", className="mt-3"),
                    dbc.Input(
                        id="pid-ti",
                        type="number",
                        value=config.PID_TI,
                        min=config.PID_TI_MIN,
                        max=config.PID_TI_MAX,
                        step=0.1,
                    ),
                    html.Small("Integration time constant (typical: 0.5-5)", className="text-muted d-block mb-2"),
                    
                    dbc.Label("Derivative Time Td (s)", className="mt-3"),
                    dbc.Input(
                        id="pid-td",
                        type="number",
                        value=config.PID_TD,
                        min=config.PID_TD_MIN,
                        max=config.PID_TD_MAX,
                        step=1,
                    ),
                    html.Small("Derivative time constant (typical: 10-50)", className="text-muted d-block"),
                ]),
            ], className="mb-3"),
        ], md=3),

        # Add Fuzzy Controller Parameters
        dbc.Col([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Fuzzy Controller (PD)")),
                    dbc.CardBody([
                        dbc.Label("Proportional Gain (Kp)"),
                        dbc.Input(
                            id="fuzzy-param-1",
                            type="number",
                            value=0.5,  # Default value
                            min=0,
                            max=1,
                            step=0.1,
                        ),
                        html.Small("Proportional gain (typical: 50-150)", className="text-muted d-block mb-2"),

                        dbc.Label("Derivative Time Td (s)"),
                        dbc.Input(
                            id="fuzzy-param-2",
                            type="number",
                            value=1.0,  # Default value
                            min=0,
                            max=2,
                            step=0.1,
                        ),
                        html.Small("Derivative time constant (typical: 10-50)", className="text-muted d-block mb-2"),
                    ]),
                ], className="mb-3"),
            ], md=12),
        ], md=3),
    ]),
    

    # PCR Protocol Card
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("PCR Protocol")),
                dbc.CardBody([
                    # Initial Denaturation
                    html.H6("Initial Denaturation", className="mt-2"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Temperature (°C)"),
                            dbc.Input(
                                id="initial-temp",
                                type="number",
                                value=config.PCR_INITIAL_DENATURATION[0],
                                min=config.TEMP_MIN,
                                max=config.TEMP_MAX,
                                step=1,
                            ),
                        ], md=6),
                        dbc.Col([
                            dbc.Label("Duration (s)"),
                            dbc.Input(
                                id="initial-duration",
                                type="number",
                                value=config.PCR_INITIAL_DENATURATION[1],
                                min=config.DURATION_MIN,
                                max=config.DURATION_MAX,
                                step=10,
                            ),
                        ], md=6),
                    ]),
                    
                    # Cycling
                    html.H6("Cycling Parameters", className="mt-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Number of Cycles"),
                            dbc.Input(
                                id="num-cycles",
                                type="number",
                                value=config.PCR_CYCLES,
                                min=config.CYCLES_MIN,
                                max=config.CYCLES_MAX,
                                step=1,
                            ),
                        ], md=12),
                    ]),
                    
                    # Denaturation
                    html.H6("Denaturation", className="mt-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Temperature (°C)"),
                            dbc.Input(
                                id="denat-temp",
                                type="number",
                                value=config.PCR_DENATURATION[0],
                                min=config.TEMP_MIN,
                                max=config.TEMP_MAX,
                                step=1,
                            ),
                        ], md=6),
                        dbc.Col([
                            dbc.Label("Duration (s)"),
                            dbc.Input(
                                id="denat-duration",
                                type="number",
                                value=config.PCR_DENATURATION[1],
                                min=config.DURATION_MIN,
                                max=config.DURATION_MAX,
                                step=5,
                            ),
                        ], md=6),
                    ]),
                    
                    # Annealing
                    html.H6("Annealing", className="mt-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Temperature (°C)"),
                            dbc.Input(
                                id="anneal-temp",
                                type="number",
                                value=config.PCR_ANNEALING[0],
                                min=config.TEMP_MIN,
                                max=config.TEMP_MAX,
                                step=1,
                            ),
                        ], md=6),
                        dbc.Col([
                            dbc.Label("Duration (s)"),
                            dbc.Input(
                                id="anneal-duration",
                                type="number",
                                value=config.PCR_ANNEALING[1],
                                min=config.DURATION_MIN,
                                max=config.DURATION_MAX,
                                step=5,
                            ),
                        ], md=6),
                    ]),
                    
                    # Extension
                    html.H6("Extension", className="mt-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Temperature (°C)"),
                            dbc.Input(
                                id="extension-temp",
                                type="number",
                                value=config.PCR_EXTENSION[0],
                                min=config.TEMP_MIN,
                                max=config.TEMP_MAX,
                                step=1,
                            ),
                        ], md=6),
                        dbc.Col([
                            dbc.Label("Duration (s)"),
                            dbc.Input(
                                id="extension-duration",
                                type="number",
                                value=config.PCR_EXTENSION[1],
                                min=config.DURATION_MIN,
                                max=config.DURATION_MAX,
                                step=5,
                            ),
                        ], md=6),
                    ]),
                    
                    # Final Extension
                    html.H6("Final Extension", className="mt-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Temperature (°C)"),
                            dbc.Input(
                                id="final-temp",
                                type="number",
                                value=config.PCR_FINAL_EXTENSION[0],
                                min=config.TEMP_MIN,
                                max=config.TEMP_MAX,
                                step=1,
                            ),
                        ], md=6),
                        dbc.Col([
                            dbc.Label("Duration (s)"),
                            dbc.Input(
                                id="final-duration",
                                type="number",
                                value=config.PCR_FINAL_EXTENSION[1],
                                min=config.DURATION_MIN,
                                max=config.DURATION_MAX,
                                step=10,
                            ),
                        ], md=6),
                    ]),
                ]),
            ], className="mb-3"),
        ]),
    ]),
    
    # Run Simulation Button
    dbc.Row([
        dbc.Col([
            dbc.Button(
                "Run Simulation",
                id="run-button",
                color="primary",
                size="lg",
                className="w-100",
            ),
        ], md=12),
    ], className="mb-4"),
    
    # Results Section
    dbc.Row([
        dbc.Col([
            dcc.Loading(
                id="loading",
                type="default",
                children=[
                    dcc.Graph(id="results-graph", style={"height": "800px"}),
                ],
            ),
        ]),
    ]),
    
], fluid=True)


# Callback for simulation
@app.callback(
    Output("results-graph", "figure"),
    Input("run-button", "n_clicks"),
    State("heat-capacity", "value"),
    State("heating-power", "value"),
    State("cooling-power", "value"),
    State("heat-loss", "value"),
    State("ambient-temp", "value"),
    State("pid-kp", "value"),
    State("pid-ti", "value"),
    State("pid-td", "value"),
    State("fuzzy-param-1", "value"),
    State("fuzzy-param-2", "value"),
    State("sample-volume", "value"),
    State("sample-density", "value"),
    State("sample-specific-heat", "value"),
    State("initial-temp", "value"),
    State("initial-duration", "value"),
    State("denat-temp", "value"),
    State("denat-duration", "value"),
    State("anneal-temp", "value"),
    State("anneal-duration", "value"),
    State("extension-temp", "value"),
    State("extension-duration", "value"),
    State("num-cycles", "value"),
    State("final-temp", "value"),
    State("final-duration", "value"),
    prevent_initial_call=True,
)
def run_simulation(
    n_clicks,
    heat_capacity,
    heating_power,
    cooling_power,
    heat_loss,
    ambient_temp,
    pid_kp,
    pid_ti,
    pid_td,
    fuzzy_param_1,
    fuzzy_param_2,
    sample_volume,
    sample_density,
    sample_specific_heat,
    initial_temp,
    initial_duration,
    denat_temp,
    denat_duration,
    anneal_temp,
    anneal_duration,
    extension_temp,
    extension_duration,
    num_cycles,
    final_temp,
    final_duration,
):
    """Run PCR simulation and generate results plot."""
    
    # Validate all inputs are not None
    required_params = {
        'heat_capacity': heat_capacity,
        'heating_power': heating_power,
        'cooling_power': cooling_power,
        'heat_loss': heat_loss,
        'ambient_temp': ambient_temp,
        'pid_kp': pid_kp,
        'pid_ti': pid_ti,
        'pid_td': pid_td,
        'fuzzy_param_1': fuzzy_param_1,
        'fuzzy_param_2': fuzzy_param_2,
        'sample_volume': sample_volume,
        'sample_density': sample_density,
        'sample_specific_heat': sample_specific_heat,
        'initial_temp': initial_temp,
        'initial_duration': initial_duration,
        'denat_temp': denat_temp,
        'denat_duration': denat_duration,
        'anneal_temp': anneal_temp,
        'anneal_duration': anneal_duration,
        'extension_temp': extension_temp,
        'extension_duration': extension_duration,
        'num_cycles': num_cycles,
        'final_temp': final_temp,
        'final_duration': final_duration,
    }
    
    # Check for None values
    missing = [name for name, value in required_params.items() if value is None]
    if missing:
        # Return empty figure with error message
        fig = go.Figure()
        fig.add_annotation(
            text=f"Error: Missing values for: {', '.join(missing)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="red")
        )
        return fig
    
    # Create thermal model
    thermal_model = ThermalModel(
        heat_capacity=heat_capacity,
        heating_power=heating_power,
        cooling_power=cooling_power,
        heat_loss_coef=heat_loss,
        ambient_temp=ambient_temp,
        sample_volume=sample_volume * 1e-6,  # Convert mL to m³
        sample_density=sample_density,
        sample_specific_heat=sample_specific_heat,
        initial_temp=ambient_temp,
    )
    
    # Create controllers
    pid_controller = PIDController(
        kp=pid_kp,
        ti=pid_ti,
        td=pid_td,
        output_min=-cooling_power,
        output_max=heating_power,
    )

    fuzzy_controller = FuzzyController(
        param1=fuzzy_param_1,
        param2=fuzzy_param_2,
        output_min=-cooling_power,
        output_max=heating_power,
    )

    # Run simulations for both controllers
    pid_simulator = PCRSimulator(thermal_model, pid_controller)
    fuzzy_simulator = PCRSimulator(thermal_model, fuzzy_controller)

    pid_results = pid_simulator.simulate(
        initial_temp=initial_temp,
        initial_duration=initial_duration,
        denat_temp=denat_temp,
        denat_duration=denat_duration,
        anneal_temp=anneal_temp,
        anneal_duration=anneal_duration,
        extension_temp=extension_temp,
        extension_duration=extension_duration,
        num_cycles=num_cycles,
        final_temp=final_temp,
        final_duration=final_duration,
    )

    fuzzy_results = fuzzy_simulator.simulate(
        initial_temp=initial_temp,
        initial_duration=initial_duration,
        denat_temp=denat_temp,
        denat_duration=denat_duration,
        anneal_temp=anneal_temp,
        anneal_duration=anneal_duration,
        extension_temp=extension_temp,
        extension_duration=extension_duration,
        num_cycles=num_cycles,
        final_temp=final_temp,
        final_duration=final_duration,
    )

    # Create subplots
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=(
            "Temperature vs Time",
            "Power Balance over Time"
        ),
        vertical_spacing=0.12,
        horizontal_spacing=0.10,
    )

    # Temperature plot
    fig.add_trace(
        go.Scatter(
            x=pid_results['time'],
            y=pid_results['temperature'],
            mode='lines',
            name='PID Temperature',
            line=dict(color='green'),
        ),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(
            x=fuzzy_results['time'],
            y=fuzzy_results['temperature'],
            mode='lines',
            name='Fuzzy Temperature',
            line=dict(color='blue'),
        ),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(
            x=pid_results['time'],
            y=pid_results['setpoint'],
            mode='lines',
            name='Setpoint',
            line=dict(color='red', dash='dash'),
        ),
        row=1, col=1
    )

    # Power balance plot
    fig.add_trace(
        go.Scatter(
            x=pid_results['time'],
            y=pid_results['control'],
            mode='lines',
            name='PID Power Balance',
            line=dict(color='green'),
        ),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(
            x=fuzzy_results['time'],
            y=fuzzy_results['control'],
            mode='lines',
            name='Fuzzy Power Balance',
            line=dict(color='blue'),
        ),
        row=2, col=1
    )

    # Update axes labels
    fig.update_xaxes(title_text="Time (s)", row=1, col=1)
    fig.update_xaxes(title_text="Time (s)", row=2, col=1)

    fig.update_yaxes(title_text="Temperature (°C)", row=1, col=1)
    fig.update_yaxes(title_text="Power (W)", row=2, col=1)

    # Update layout
    fig.update_layout(
        title_text="PCR Simulation Results",
        showlegend=True,
        hovermode='x unified',
        height=800,
    )
    
    return fig


def main():
    """Run the Dash application."""
    app.run(debug=True, host='127.0.0.1', port=8050)


if __name__ == "__main__":
    main()
