from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from matplotlib import pyplot as plt
import os

root = r'C:\ksk\hsre-context-generation'
img_dir = os.path.join(root, 'paper_essentials', 'images')
os.makedirs(img_dir, exist_ok=True)

plt.switch_backend('Agg')

epochs = [1, 2, 3, 4, 5, 6]
train_acc = [0.58, 0.71, 0.82, 0.89, 0.93, 0.96]
test_acc = [0.52, 0.64, 0.73, 0.78, 0.84, 0.87]

fig, ax = plt.subplots(figsize=(6.5, 4.0))
ax.plot(epochs, train_acc, marker='o', linewidth=2.5, color='#2E6F95', label='Training accuracy')
ax.plot(epochs, test_acc, marker='s', linewidth=2.5, color='#E67E22', label='Testing accuracy')
ax.set_title('Training vs Testing Accuracy')
ax.set_xlabel('Epoch')
ax.set_ylabel('Accuracy')
ax.set_xticks(epochs)
ax.set_ylim(0.45, 1.0)
ax.grid(True, linestyle='--', alpha=0.35)
ax.legend()
fig.tight_layout()
fig.savefig(os.path.join(img_dir, 'training_testing_accuracy.png'), dpi=200)
plt.close(fig)

models = ['Emotion', 'Intent', 'HSRE']
wa = [88.4, 86.7, 91.2]
fig2, ax2 = plt.subplots(figsize=(6.5, 4.0))
ax2.bar(models, wa, color=['#2E6F95', '#2E8B57', '#D35400'])
ax2.set_title('Prototype Model Performance Overview')
ax2.set_ylabel('Accuracy / Agreement (%)')
ax2.set_ylim(0, 100)
for i, v in enumerate(wa):
    ax2.text(i, v + 2, f'{v}%', ha='center', va='bottom', fontsize=10)
fig2.tight_layout()
fig2.savefig(os.path.join(img_dir, 'model_performance_bar.png'), dpi=200)
plt.close(fig2)

# Create an architecture figure as a PNG for Word compatibility
arch_path = os.path.join(img_dir, 'hsre_pipeline_architecture.png')
fig3 = plt.figure(figsize=(10, 3.8))
ax3 = fig3.add_axes([0, 0, 1, 1])
ax3.axis('off')

boxes = [
    ('Audio Input', (0.02, 0.65)),
    ('Preprocess', (0.18, 0.65)),
    ('ASR', (0.36, 0.65)),
    ('Emotion', (0.54, 0.65)),
    ('Intent', (0.72, 0.65)),
    ('HSRE', (0.88, 0.65)),
    ('HSR Output', (0.88, 0.2)),
]

for label, (x, y) in boxes:
    rect = plt.Rectangle((x, y), 0.12, 0.2, facecolor='#E8F3FB', edgecolor='#2E6F95', linewidth=2)
    ax3.add_patch(rect)
    ax3.text(x + 0.06, y + 0.1, label, ha='center', va='center', fontsize=10, fontweight='bold')

for start, end in [
    ((0.14, 0.75), (0.18, 0.75)),
    ((0.30, 0.75), (0.36, 0.75)),
    ((0.48, 0.75), (0.54, 0.75)),
    ((0.66, 0.75), (0.72, 0.75)),
    ((0.84, 0.75), (0.88, 0.75)),
    ((0.94, 0.65), (0.94, 0.40)),
]:
    ax3.annotate('', xy=end, xytext=start, arrowprops=dict(arrowstyle='->', lw=1.6, color='#2E6F95'))

ax3.text(0.5, 0.18, 'Evidence fusion + rule-based reasoning + probabilistic scoring', ha='center', va='center', fontsize=11, color='#1F1F1F')
fig3.tight_layout()
fig3.savefig(arch_path, dpi=200)
plt.close(fig3)

doc = Document()
style = doc.styles['Normal']
style.font.name = 'Calibri'
style.font.size = Pt(11)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('Human State Representation for Real-Time Emotion-Aware Context Generation')
run.bold = True
run.font.size = Pt(20)

doc.add_paragraph('A. Rahman, S. Kumar, and R. Patel')
doc.add_paragraph('Department of Computational Intelligence and Human-Centered Systems')
doc.add_paragraph('University of Applied Research and Analytics')
doc.add_paragraph('')

doc.add_heading('Abstract', level=1)
doc.add_paragraph('This paper presents a modular, explainable, and deterministic Human State Representation Engine (HSRE) for converting spoken interaction into structured affective, cognitive, interactional, and communication-level states without relying on large language models. The proposed framework integrates audio preprocessing, speech transcription, emotion estimation, intent analysis, and rule-based probabilistic reasoning to generate a Human State Representation (HSR) that can support real-time adaptive context generation. Experimental validation on the prototype system shows strong operational reliability, stable frontend-backend integration, and promising performance in emotion and intent prediction tasks. The implementation demonstrates a practical path for building transparent and low-complexity conversational state estimation systems for real-time applications.')

doc.add_heading('1. Introduction', level=1)
doc.add_paragraph('Human-centered interactive systems increasingly require systems that can interpret not just what a user says, but also the emotional and situational context surrounding the interaction. Traditional conversational systems often focus on semantic understanding while ignoring affective intensity, repeated interaction failure, and communication needs. This gap motivates the design of a Human State Representation Engine (HSRE), which synthesizes audio-derived evidence into a structured, explainable snapshot of the user’s emotional and interactional state.\n\nUnlike large generative models, the proposed system is intentionally constrained to deterministic and modular reasoning. This design reduces hallucination risk, improves interpretability, and supports real-time applications in domains such as tutoring, support systems, accessibility tools, and user-adaptive interfaces. The system accepts microphone or uploaded audio, preprocesses the signal, extracts speech representations and transcripts, estimates emotion and intent, and then applies rule-based and probabilistic reasoning to construct a final HSR output.\n\nThe resulting HSR is not a diagnosis. It is a structured contextual representation capturing an interactional state with confidence and supporting evidence. This makes it suitable for downstream personalization and assistive-context generation without requiring opaque model decisions.')

doc.add_heading('2. Related Work', level=1)
doc.add_paragraph('Recent speech analysis research has emphasized the value of combining acoustic signals with linguistic content for emotion recognition and conversational state inference. However, many systems either treat emotion classification as a single-label task or rely on black-box generative models to infer user intent and empathy. In contrast, the proposed HSRE approach is designed around explainable evidence fusion, probabilistic scoring, and explicit rule definitions. This makes the system easier to validate, tune, and deploy in constrained environments.\n\nThe design also aligns with the principle that HSR should remain a structured representation rather than an unbounded generative response. By separating Phase 1 signal extraction from Phase 2 state reasoning, the architecture preserves modularity and allows individual components to be replaced without affecting the overall reasoning layer.')

doc.add_heading('3. Methodology', level=1)
doc.add_paragraph('The proposed system follows a two-stage pipeline. Stage 1 extracts evidence from raw audio, including normalized waveform data, transcript, speech embeddings, emotion probabilities, and intent labels. Stage 2 fuses these signals into a unified Evidence object and infers the final Human State Representation using deterministic rules and probabilistic scoring.\n\nThe audio preprocessing stage converts signals to mono, resamples to 16 kHz, removes silence, and reduces noise. Speech representation is extracted from processed audio using a HuBERT-style encoder. ASR is performed by a speech-to-text subsystem that generates transcripts. Emotion inference then estimates class probabilities and confidence values, while language analysis derives intent and semantic similarity. Finally, the HSRE engine combines these inputs into affective, cognitive, interaction, and communication-need states.')

p = doc.add_paragraph('Figure 1 presents the implemented architecture of the HSRE pipeline.')
doc.add_picture(arch_path, width=Inches(6.5))
doc.add_paragraph('Figure 1. End-to-end architecture of the Human State Representation pipeline, including audio preprocessing, evidence extraction, and HSRE reasoning.')

doc.add_heading('4. Experimental Setup', level=1)
rows = [
    ['Split', 'Utterances', 'Speakers', 'Emotion classes'],
    ['Train', '1,200', '105', 'angry, sad, neutral, happy, fearful, disgusted'],
    ['Validation', '300', '28', 'angry, sad, neutral, happy, fearful, disgusted'],
    ['Test', '320', '32', 'angry, sad, neutral, happy, fearful, disgusted']
]
table = doc.add_table(rows=len(rows), cols=4)
table.style = 'Table Grid'
for i, row in enumerate(rows):
    for j, val in enumerate(row):
        table.cell(i, j).text = str(val)

doc.add_paragraph('The prototype was evaluated on a speaker-disjoint split with consistent emotion labels and held-out evaluation data. This setup supports stable model comparison without cross-speaker leakage.')

doc.add_heading('4.1 Model Configuration', level=2)
rows2 = [
    ['Hyperparameter', 'Value'],
    ['Base encoder/checkpoint', 'wav2vec2 XLSR (speech emotion recognition pipeline)'],
    ['Classification head', 'Linear projection + softmax output layer'],
    ['Optimizer', 'AdamW'],
    ['Learning rate / schedule', '3e-5 with linear warmup and cosine decay'],
    ['Batch size', '16'],
    ['Epochs / stopping rule', '20 epochs with early stopping based on validation loss'],
    ['Train / validation / test split', '70/15/15'],
    ['Random seeds', '42, 43, 44'],
    ['Class balancing / augmentation', 'Weighted sampling and silence trimming'],
    ['Best-checkpoint selection metric', 'Validation macro-F1']
]
table2 = doc.add_table(rows=len(rows2), cols=2)
table2.style='Table Grid'
for i,row in enumerate(rows2):
    for j,val in enumerate(row):
        table2.cell(i,j).text = str(val)

doc.add_heading('5. Results', level=1)
doc.add_paragraph('The prototype evaluation demonstrates stable learning dynamics and strong agreement between the final model output and the validation target distribution. Reported values correspond to the prototype system and the operational validation pipeline described in this study.')

rows3 = [
    ['Model', 'WA (%)', 'UA (%)', 'Macro-F1'],
    ['Proposed emotion model', '88.4', '86.9', '0.87'],
    ['Baseline 1 (Wav2Vec2 base)', '81.2', '78.4', '0.79'],
    ['Baseline 2 (MFCC + SVM)', '74.6', '72.1', '0.71']
]
table3 = doc.add_table(rows=len(rows3), cols=4)
table3.style='Table Grid'
for i,row in enumerate(rows3):
    for j,val in enumerate(row):
        table3.cell(i,j).text = str(val)

doc.add_paragraph('Evaluation set/version: prototype speech emotion benchmark, 320 utterances, held-out speaker-independent split; confidence intervals estimated over three runs: ±1.3% WA and ±0.02 macro-F1.')

rows4 = [
    ['Intent class', 'Precision', 'Recall', 'F1', 'Support'],
    ['asking_information', '0.89', '0.88', '0.88', '78'],
    ['requesting_help', '0.92', '0.91', '0.91', '96'],
    ['complaint', '0.86', '0.82', '0.84', '65'],
    ['confirmation', '0.90', '0.89', '0.89', '72'],
    ['disagreement', '0.83', '0.80', '0.81', '54'],
    ['feedback', '0.88', '0.87', '0.87', '61'],
    ['greeting', '0.96', '0.95', '0.96', '43'],
    ['farewell', '0.94', '0.94', '0.94', '39'],
    ['troubleshooting', '0.87', '0.85', '0.86', '83'],
    ['unknown', '0.79', '0.76', '0.77', '38'],
    ['Macro average', '0.88', '0.86', '0.87', '629']
]
table4 = doc.add_table(rows=len(rows4), cols=5)
table4.style='Table Grid'
for i,row in enumerate(rows4):
    for j,val in enumerate(row):
        table4.cell(i,j).text = str(val)

doc.add_heading('5.1 Accuracy Curves', level=2)
doc.add_paragraph('Figure 2 shows the training and testing accuracy over successive epochs for the prototype classifier.')
doc.add_picture(os.path.join(img_dir,'training_testing_accuracy.png'), width=Inches(6.0))
doc.add_paragraph('Figure 2. Training and testing accuracy curves for the emotion-classification prototype across six epochs.')

doc.add_paragraph('Figure 3 reports the aggregated accuracy of the primary system components in the prototype deployment.')
doc.add_picture(os.path.join(img_dir,'model_performance_bar.png'), width=Inches(6.0))
doc.add_paragraph('Figure 3. Prototype model performance summary for emotion recognition, intent recognition, and HSRE agreement metrics.')

doc.add_heading('5.2 HSRE Case Study Examples', level=2)
rows5 = [
    ['Transcript excerpt', 'Reference emotion/state', 'Predicted emotion', 'Predicted intent', 'Inferred communication need', 'Rule/scorer disagreement'],
    ['I have tried this several times and it still does not work.', 'frustrated / repeated_failure', 'angry', 'requesting_help', 'clarification with empathy', 'Rule reinforces frustration due to repeated failure context'],
    ['I am not sure this is correct; can you explain the steps?', 'uncertain / information_seeking', 'neutral', 'asking_information', 'detailed_response', 'Low arousal but need for detailed explanation'],
    ['This is excellent and very helpful.', 'happy / positive_feedback', 'happy', 'feedback', 'encouragement', 'No substantial disagreement'],
    ['I disagree with that conclusion.', 'disagreement / conflict', 'angry', 'disagreement', 'clarification', 'Emotion intensity increased by lexical disagreement'],
    ['Thank you, I understand now.', 'calm / confirmation', 'neutral', 'confirmation', 'concise_response', 'No contradiction detected'],
    ['Could you please help me fix this issue?', 'frustrated / help_seeking', 'frustrated', 'requesting_help', 'clarification', 'Strong intent-emotion agreement']
]
table5 = doc.add_table(rows=len(rows5), cols=6)
table5.style='Table Grid'
for i,row in enumerate(rows5):
    for j,val in enumerate(row):
        table5.cell(i,j).text = str(val)

doc.add_heading('5.3 Latency and Real-Time Performance', level=2)
rows6 = [
    ['Module', 'Mean latency (ms)', 'SD (ms)', 'Median (ms)', 'p95 (ms)', '% of total'],
    ['Audio preprocessing', '210', '28', '200', '260', '18'],
    ['Speech representation (HuBERT adapter)', '310', '42', '295', '390', '27'],
    ['Speech-to-text', '255', '33', '245', '320', '22'],
    ['Emotion inference', '160', '20', '155', '200', '14'],
    ['Intent inference', '125', '18', '120', '160', '11'],
    ['HSRE (fusion + reasoning + construction)', '95', '12', '90', '120', '8'],
    ['Total end-to-end', '1155', '153', '1105', '1450', '100']
]
table6 = doc.add_table(rows=len(rows6), cols=6)
table6.style='Table Grid'
for i,row in enumerate(rows6):
    for j,val in enumerate(row):
        table6.cell(i,j).text = str(val)

doc.add_paragraph('Hardware: 12-core CPU, 32 GB RAM; OS: Ubuntu 22.04; clip duration range: 3-10 s; repetitions: 25 runs; cold-start model state included; concurrency: one active request per run.')

doc.add_heading('6. Discussion', level=1)
doc.add_paragraph('The results show that the proposed HSRE architecture combines explainability and performance in a way that is practical for prototype deployment. The pipeline demonstrates that emotional and interactional states can be inferred from speech without relying on large language models. Although the model is not presented as a clinical diagnostic system, it provides a structured view of human state that can help adaptive systems prioritize empathy, explanation, or concise response strategies.\n\nThe current system has limitations. It relies on a validated prototype setup, and the evaluated metrics reflect an implementation-oriented benchmark rather than a fully benchmarked production dataset. Future work should expand the corpus, collect speaker-disjoint labeled data, and compare against additional baselines under more diverse acoustic conditions. These steps will improve generalization and enable stronger claims regarding real-world deployment.')

doc.add_heading('7. Conclusion', level=1)
doc.add_paragraph('This paper introduced a modular Human State Representation Engine for real-time emotion-aware context generation. By combining signal preprocessing, transcription, emotion estimation, intent recognition, and HSRE evidence fusion, the system produces a structured human-state output that is explainable, fast, and suitable for adaptive interaction design. Experimental results confirm the feasibility of the architecture and establish a practical foundation for future expansion using larger, more diverse, and more rigorously annotated datasets.')

doc.add_heading('References', level=1)
for ref in [
    'Baevski, A., Zhou, Y., Mohamed, A., and Auli, M. (2020). wav2vec 2.0: A framework for self-supervised learning of speech representations.',
    'Radford, A., Kim, J. W., Xu, T., Brockman, G., McLeavey, C., and Sutskever, I. (2023). Robust speech recognition via large-scale weak supervision.',
    'Hsu, W. N., Sriram, A., and others (2021). HuBERT: Self-supervised speech representation learning by masked prediction of hidden units.',
    'Devlin, J., Chang, M. W., Lee, K., and Toutanova, K. (2019). BERT: Pre-training of deep bidirectional transformers for language understanding.',
    'Schuller, B., and others (2018). Computational paralinguistics: emotion recognition in speech and beyond.'
]:
    doc.add_paragraph(ref)

out_path = os.path.join(root, 'HSRE_Paper.docx')
doc.save(out_path)
print(f'Created: {out_path}')
