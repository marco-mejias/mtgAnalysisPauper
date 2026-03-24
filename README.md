# 🧠 Pauper AI: MTG Meta Evaluator & ML Classifier

A custom-built full-stack application and algorithmic evaluation engine in Python. 
I built this project to apply **Natural Language Processing (NLP)**, **Feature Engineering** and **Machine Learning Classification** on a real-world scenario: *Magic: The Gathering* deckbuilding and metagame analysis. 
The system reads the unstructured "Oracle text" of a card, extracts its features, and uses a dual architecture (a deterministic rule-based manager and a probabilistic ML classifier) to predict its viability across competitive Pauper archetypes.

⚠ THIS PROJECT IS STILL ON PROGRESS. THE LIST OF IMPROVEMENT FEATURES ARE (hopefully) GOING TO BE RESOLVED ⚠

### 📦 Technologies

**Backend & Data Science**
* **Python 3** (Core Object-Oriented Logic)
* **Scikit-Learn / Pandas / NumPy** (Data manipulation, feature vectorization, and Machine Learning model training)
* **Regex / Custom Lexers** (Natural Language Processing for card text)
* **Pickle / Joblib** (Model persistence and state saving)
* **Flask** (RESTful API backend routing)

**Frontend & Integration**
* **JavaScript** (Asynchronous API handling, JSON parsing, Dynamic DOM manipulation)
* **HTML5 / CSS3** (Responsive design, custom UI/UX with CSS variables and Flexbox)
* **Scryfall REST API** (Real-time data fetching and fuzzy search debouncing)

### ⚙️ Features

Here's what the application does under the hood through its interactive web interface:

* **Dual Evaluation Architecture:** Combines a deterministic rule-based engine (`ArchetypeManager`) with a probabilistic Machine Learning model (`MLEngine`) to provide a multi-layered evaluation of every card.
* **ML Probability Predictor:** Utilizes a trained Machine Learning classifier to calculate the exact probability of a card successfully fitting into a specific deck based on historical color, mana curve and other textual relationships.
* **NLP Text Parsing Engine:** A custom lexical analyzer (`TextParser`) reads raw card text and translates it into structured data, extracting keywords, triggers, and mechanical actions (like *Spellslinger*, *Cantrip*, *Graveyard Hate*).
* **Heuristic Scoring System:** Calculates a raw "Base Power Score" (`CardEvaluator`) using a weighted mathematical formula based on the card's Mana Value (CMC), power/toughness ratios and the value of its extracted abilities.
* **Contextual Meta Classification:** Evaluates the card against a dataset of competitive decks applying hard constraints (Color Identity, Parasitic Mechanics) and calculating a final compatibility score using synergy multipliers.
* **Real-time Data Fetching:** Connected to the Scryfall API, it features a fuzzy search to instantly fetch accurate card data, JSON schemas, and images without overloading the server.
* **Explainable AI UI:** The frontend dynamically generates an **Audit Log**. It provides a step-by-step mathematical breakdown of how the algorithm reached its conclusion, displaying synergy bonuses, curve penalties, and exact reasons for strict rejections.

### 👩🏽‍🍳 The Process & Architecture

I built this project separating the logic into independent modules to understand how data flows from raw text to a final algorithmic decision:

1. **Data Gathering & Preprocessing:** I utilized datasets of competitive Pauper decks, cleaning and organizing archetypes into profiles containing their average mana curves, color dominances, and highly weighted mechanical needs.
2. **Feature Extraction:** I implemented pattern matching and regex to identify specific phrases and mechanics, effectively turning natural language into a boolean and numerical array of features ready for algorithmic processing.
3. **Algorithmic Weighting:** I created a scoring matrix where every mechanic has a base value, dynamically adjusted based on the card's mana cost to penalize expensive, slow cards and reward efficient interaction.
4. **Deterministic Rule Engine:** I built an evaluation engine that cross-references the card's features against archetype profiles. It uses strict logic to filter out impossible fits (like a Mono Red deck rejecting a Blue card) and applies multipliers for tribal or mechanical synergies.
5. **Statistical Machine Learning:** I trained a predictive model on historical deck data. This engine calculates the statistical probability of a card belonging to an archetype, acting as a second opinion alongside the deterministic Manager.
6. **Full-Stack Integration:** I wrapped the Python engines in a Flask API and built a responsive frontend. The biggest challenge was implementing Explainable AI principles: refactoring the backend to return an internal log of its decision-making process to the frontend so the user can see exactly why a card was rejected or accepted.

### 📚 What I Learned

* **Applied Machine Learning:** I learned how to train, test, save (`.pkl`), and deploy predictive classification models that evaluate historical datasets to output real-time inclusion probabilities.
* **Feature Engineering & NLP:** I learned how to transform raw, unstructured text strings into quantifiable data points that an algorithm can process and score effectively.
* **Algorithm Design:** I learned how to balance strict algorithmic filtering (like color identity constraints) with fluid scoring systems (like synergy weight multipliers) to create a robust decision engine.
* **Explainable AI Implementation:** I learned the crucial importance of transparency in AI. Building the Audit Log taught me how to store and expose backend algorithmic steps gracefully to the end-user.
* **Asynchronous Web Architecture:** I improved my skills in bridging Python backends with JavaScript frontends using RESTful APIs, JSON payloads, async/await functions, and debounced API calls.
* **Software Architecture:** I learned the importance of the Separation of Concerns principle, keeping the Parser, Evaluator, Meta Manager, ML Engine, and Web Routing strictly modular.

### ⚠️ Limitations & Edge Cases

* **Subjective Feature Weighting:** The baseline numerical values and weights assigned to specific mechanics (like deciding how much a "Cantrip" is worth compared to "Graveyard Hate") were manually defined by me. Therefore, the heuristic engine inherently carries some of my own personal bias and MTG design philosophy, which may influence the final scores.
* **Frontend Abstraction:** While the Explainable AI (XAI) UI provides a robust Audit Log, it does not illustrate the entirety of the complex backend pipeline. 
* **Contextual Blindness:** Because the parsing engine looks for specific keywords and established mechanics, it struggles to evaluate completely unique, highly specific two-card combos that don't rely on standard game terminology.
* **Dataset Dependency:** The classification engine relies on a pre-loaded CSV of the current metagame. If the meta shifts dramatically or a new archetype emerges, the algorithm cannot classify cards for that new deck until the training dataset is updated.
* **Text Ambiguity:** Older cards with outdated or highly unusual phrasing can sometimes bypass the pattern-matching logic of the parser, resulting in missed mechanical tags.
* **ML Overfitting Risks:** If the training dataset contains an overwhelming amount of a specific archetype (like too many Affinity decks), the Machine Learning model might overvalue certain features, creating skewed probabilities.
  
### 💭 How can it be improved?

* **Deep Learning Integration:** Evolve the current traditional Machine Learning algorithms into a Neural Network or Transformer-based architecture (like Word Embeddings) to grasp the complex *semantic intent* of a card, rather than just relying on feature extraction probabilities.
* **Automated Web Scraping Pipeline:** Implement a Python scraper (using `BeautifulSoup` or `Selenium`) to automatically fetch, parse, and clean top-performing decklists from MTG tournament sites on a weekly basis, keeping the ML training dataset and Archetype CSV permanently up to date without manual intervention.
* **User Decklist Evaluation:** Add a feature allowing users to upload their own custom decklists (via `.txt` or URL). The AI could then evaluate a specific card against the user's personal list, suggesting optimal cuts and additions.
* **Format Expansion:** Scale the data infrastructure to handle much larger, more complex formats like Modern, Pioneer, or Commander (EDH).

### 🚦 Running the Project

To run the project in your local environment, follow these steps:

1. Clone the repository to your local machine.
2. Ensure you have Python 3 installed.
3. Open a terminal in the project directory and create a virtual environment (optional but recommended).
4. Run `pip install flask requests pandas scikit-learn` (and any other dependencies listed in `requirements.txt`).
5. Ensure your datasets (`data/archetypes_review.csv` and your ML `.pkl` model) are correctly placed in the root or data directories.
6. Run `python app.py` to start the Flask backend.
7. Open your web browser and navigate to `http://127.0.0.1:5000` to interact with the UI.
