from nicegui import ui
import numpy as np
from matplotlib import pyplot as plt

from simple_ui.config import MAX_INPUT_ARTICLE_CHARS, MAX_INPUT_EVIDENCES_CHARS

from simple_ui.states import CurrentAnalysisState

from caes_module import CEASservice

state = CurrentAnalysisState()
caes_analyzer = CEASservice()

def warning_beginning():
    with ui.dialog() as dialog, ui.card():
        ui.label('Warning: Your analysis will not be saved. Continue ?')
        with ui.row():
            ui.button('Yes', on_click=lambda: ui.open(init_page), color="green")
            ui.button('No', on_click=dialog.close, color="red")
    dialog.open()

def validate_int(text_int):
    try:
        val = int(text_int.replace("\n"))
        return True
    except:
        return False

def run_claims():

    hyp_result = caes_analyzer.get_claims(
        input_dict={"text": state.article_text}
    )
    state.set_claims(hyp_result)

def run_analysis():
    analysis_result = caes_analyzer.analyze(
        input_dict={
            "hypothesis": state.hypothesis,
            "manual_evidences": state.evidences,
            "min_alignment_limit": state.min_alignment_limit,
            "max_alignment_limit": state.max_alignment_limit
        }
    )
    state.set_analysis_result(analysis_result)
    ui.open(analysis_viz)

def plot_hypothesis_scores():
    ui.button('How to read the results ?',
              on_click=lambda: ui.open("/how_to_read_results", new_tab=True))


    with ui.pyplot(figsize=(7, 7)):
        idx = list(range(len(state.analysis_result["ordered_hypothesises_scores"])))
        plt.bar(idx,
                state.analysis_result["ordered_hypothesises_scores"], tick_label=idx)
        plt.xlabel("Claim ID")
        plt.ylabel("Claim Score (+1 accepted, -1 rejected)")
        plt.title("Claim Acceptance/Rejection Scoring")

        columns = [
            {'name': 'claim_num_id', 'label': 'Claim ID.', 'field': 'claim_num_id', 'required': True, 'align': 'left'},
            {'name': 'hypothesis', 'label': 'Claims', 'field': 'hypothesis', 'required': True, 'align': 'left'},
            {'name': 'score_hypothesis', 'label': 'Scores', 'field': 'score_hypothesis', 'required': True, 'align': 'left'},
        ]
        rows = [
            {'hypothesis': hyp, "claim_num_id": claim_num_id, "score_hypothesis": state.analysis_result["ordered_hypothesises_scores"][claim_num_id]} for claim_num_id, hyp in enumerate(state.analysis_result["ordered_hypothesises"])
        ]
        ui.table(columns=columns, rows=rows, row_key='claim_num_id')


def plot_evidence_matrix():
    # A[A == NDV] = numpy.nan
    scoring_matrix = np.array(state.analysis_result["full_scoring_matrix"])
    scoring_matrix[scoring_matrix==-1000] = np.nan

    with ui.pyplot(figsize=(10, 10)):
        plt.imshow(
            scoring_matrix, cmap='Wistia'
        )
        plt.colorbar()
        plt.xlabel("Evidence ID")
        plt.ylabel("Claim ID")
        plt.title("Claim-Evidence Influence Colourmap")
        from pprint import pprint
        pprint(state.analysis_result)
        xticks = list(range(len(scoring_matrix)))
        yticks = list(range(scoring_matrix.shape[1]))
        plt.xticks(xticks)
        plt.yticks(yticks)

        for i in range(len(scoring_matrix)):
            for j in range(scoring_matrix.shape[1]):
                text = plt.text(j, i, scoring_matrix[i, j],
                               ha="center", va="center", color="b")

    columns = [
        {'name': 'ev_num_id', 'label': 'Evid. Num.', 'field': 'ev_num_id', 'required': True, 'align': 'left'},
        {'name': 'evidences', 'label': 'Evidences', 'field': 'evidences', 'required': True, 'align': 'left'},
    ]
    rows = [
        {'evidences': ev, "ev_num_id": ev_num_id} for ev_num_id, ev in
        enumerate(state.analysis_result["full_ordered_evidences"])
    ]
    ui.table(columns=columns, rows=rows, row_key='ev_num_id')


@ui.page("/how_to_set_limits")
def how_to_set_limits():
    with ui.card().classes('center'):
        ui.label('The limits are needed to filter irrelevant evidences. Evidence is considered irrelevant if it supports too many of too few '
                 'claims, according to ACH theory. We set the following limits:\n'
                 'Min. Alignment Limit (MiAL): if evidence if aligned with less than MiAL claims, it will not be considered in the analysis.\n'
                 'Max. Alignment Limit (MaAL): if evidence if aligned with more than MaAL claims, it will not be considered in the analysis.\n\n'
                 'If either of those conditions is true, the evidence will be considered irrelevant.')


@ui.page("/how_to_read_results")
def how_to_read_results():
    with ui.card().classes('center'):
        ui.label('The first image represents a claim-score matrix. Every claim was evaluated automatically by the system based on provided '
                 'evidences, and the final conclusion is represented here. The score is in range of [-1, +1]. The closer a score to -1, the less'
                 'likely is that the claim can be accepted in the opinion of the system. The closer score value to +1, the more likely for system to '
                 'select the hypothesis. See image for more details.')
        ui.image('https://picsum.photos/id/377/640/360')
        ui.label(
            "The table below the graph shows the mapping of the claim ID in the graph to the claim text."
        )
        ui.separator()


        ui.label(
            'The second image represents an analysis of evidence importance per claim. Columns represent claims and rows represent evidences.'
            'The scores are presented as a colourmap in range of [-1, +1]. '
            'The closer a score to -1, the more influence has the evidence towards the claim to reject it. The closer it to +1,'
            'the more influence has the evidence towards the claim to support it. If the claim is nan '
            'it was not considered during the decision making due to the rules of filtering of irrelevant evidences. The evidence is considered to '
            'be irrelevant if it supports less than minimum limit or more than maximum limit of hypothesis.')
        ui.image('https://picsum.photos/id/377/640/360')
        ui.label(
            "The table below the graph shows the mapping of the evidence ID in the graph to the evidence text."
        )


@ui.page("/analysis")
def analysis_viz():
    with ui.card().classes('center'):
        plot_hypothesis_scores()
        plot_evidence_matrix()

    ui.button('Go to the beginning',
                  on_click=warning_beginning
              )



@ui.page('/add_evidences')
def add_evidences_page():
    run_claims()
    with ui.card():
        columns = [
            {'name': 'hypothesis', 'label': 'Claims', 'field': 'hypothesis', 'required': True, 'align': 'left'},
        ]
        rows = [
            {'hypothesis': hyp} for hyp in state.hypothesis
        ]
        ui.table(columns=columns, rows=rows, row_key='hypothesis')

        ui.textarea(label='Add Evidences (split by new line)',
                 placeholder='Start typing',
                 on_change=lambda e: state.set_evidences(e.value),
                 validation={'Input too long': lambda value: len(value) < MAX_INPUT_EVIDENCES_CHARS}
                    ).classes('w-[800px] mx-auto').classes('h-[200px]')
        with ui.row():
            ui.button('How to set limits',
                      on_click=lambda: ui.open("/how_to_set_limits", new_tab=True))
            ui.input(label='Min. Alignment Limit', placeholder='integer value',
                     on_change=lambda e: state.set_min_alignment_limit(e.value),
                     value="-1",
                     validation={'Provide correct integer value': lambda value: validate_int(value)})
            ui.input(label='Max. Alignment Limit', placeholder='integer value',
                     value="-1",
                     on_change=lambda e: state.set_max_alignment_limit(e.value),
                     validation={'Provide correct integer value': lambda value: validate_int(value)})


        with ui.row():
            ui.button('Run Analysis',
                        on_click=run_analysis)
            ui.link("If the button does not work, please click here to redirect to the next step", analysis_viz)


@ui.page('/')
def init_page():
    with ui.card():
        element = ui.textarea(label='Article text',
                 placeholder='Start typing',
                 on_change=lambda e: state.set_article(e.value),
                 validation={'Input too long': lambda value: len(value) < MAX_INPUT_ARTICLE_CHARS})
        element.classes('w-[800px] mx-auto').classes('h-[500px]')

        with ui.row():

            ui.button('Get claims',
                      on_click=lambda: ui.open(add_evidences_page))
            ui.link("If the button does not work, please click here to redirect to the next step", add_evidences_page)

ui.run(port=8080, title="Automatic ACH Fact-Checking System (Pre-BETA)")

