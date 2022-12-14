import plotly
import plotly.express as px
import plotly.graph_objects as go


def plot_attribute_distribution(df_cards, attributes, subplots=False):

    colors = px.colors.qualitative.Set1

    if subplots:
        nb_rows, nb_cols = 2, 3
        fig = plotly.subplots.make_subplots(rows=nb_rows, cols=nb_cols,
                                            subplot_titles=df_cards.columns[:6],
                                            y_title='# Cards')
        row = 1
        for i, att in enumerate(attributes):
            if i == nb_cols:
                row = 2
            bars = df_cards.iloc[:, i].value_counts(normalize=False)
            fig.append_trace(
                go.Bar(x=bars.index, y=bars.values, name=df_cards.columns[i], marker_color=colors[i]),
                row=row, col=(i%nb_cols)+1
            )

    else: 
        data = []
        for i, att in enumerate(attributes):
            bars = df_cards[att].value_counts()
            data.append(go.Bar(x=bars.index, y=bars.values,
                        name=att,
                        marker_color=colors[i])
                        )

        fig = go.Figure(data=data)
        fig.update_layout(barmode='group')

    fig.update_layout(title_text=f'Attribute distributions of {len(df_cards)} cards', 
                      template='plotly_dark')
    fig.show()