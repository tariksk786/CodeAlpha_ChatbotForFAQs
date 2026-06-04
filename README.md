# AI-Powered FAQ Chatbot using NLP and Flask

A production-ready, highly interactive AI chatbot application designed to answer questions by matching them with stored FAQs. The engine uses Natural Language Processing (NLP) techniques: TF-IDF vectorization, Cosine Similarity, and fuzzy string matching, styled with a premium glassmorphic UI.

---

## Key Features

- **Hybrid NLP Matcher**: Integrates TF-IDF vectorization with Cosine Similarity and falls back to character-level fuzzy sequence matching (`difflib.SequenceMatcher`) for typo resilience.
- **Intent Detection**: Instantly catches greetings, farewells, gratitude, and bot identity requests with random human-like responses.
- **Voice Assistant**: Integrated Speech-to-Text input using the HTML5 Web Speech API and Text-to-Speech synthesis for audio output.
- **Admin Dashboard**: Full CRUD management of FAQ data, bulk upload parsing for CSV/JSON files, and search filters.
- **Analytics Dashboard**: Dynamic metrics counters and Chart.js graphics showing query volumes, confidence scores, and category distribution logs.
- **Data Portability**: Allows conversation exporting in pure browser TXT and PDF layouts, and FAQ importing/exporting.
- **Session Security**: Admin dashboard protected via hashed passwords (using SHA-256) and Flask cookie sessions.

---

## Tech Stack

- **Backend**: Python, Flask (Blueprint Architecture), SQLite 3.
- **NLP Library**: NLTK, Scikit-Learn.
- **Frontend**: HTML5, CSS3, ES6 JavaScript, Bootstrap 5, Font Awesome, Chart.js, SweetAlert2, jsPDF.
- **DevOps**: Docker, Gunicorn.

---

## Folder Structure

```
faq-chatbot/
├── app.py                     # Main application entrypoint
├── config.py                  # Core configuration file
├── requirements.txt           # Python packages dependencies
├── faq.json                   # Default seeding FAQs database
├── Dockerfile                 # Docker build file
├── render.yaml                # Render Blueprint deployment
├── Procfile                   # Process file for WSGI gunicorn
├── README.md                  # System documentation
│
├── routes/
│   ├── chat_routes.py         # Chat endpoints
│   ├── faq_routes.py          # FAQ CRUD REST endpoints
│   ├── admin_routes.py        # Authentication & rendering templates
│   └── analytics_routes.py    # Metric endpoints & views
│
├── services/
│   ├── faq_service.py         # Coordinating NLP & database models
│   ├── analytics_service.py   # Aggregating database activity logs
│   └── export_service.py      # Parsing CSV & JSON files
│
├── models/
│   └── faq_model.py           # SQLite connection & CRUD operations
│
├── nlp/
│   ├── preprocess.py          # NLTK cleaning pipeline
│   ├── vectorizer.py          # TF-IDF training & transformations
│   ├── matcher.py             # Cosine & fuzzy matcher
│   └── intent.py              # Rule-based conversational intents
│
├── static/
│   ├── css/
│   │   ├── style.css          # Main styles & glassmorphism
│   │   ├── dashboard.css      # Tables & panels layout
│   │   └── animations.css     # Glowing blobs & typing dots
│   └── js/
│       ├── chatbot.js         # Chat UI and exporters
│       ├── admin.js           # FAQ CRUD list operations
│       ├── analytics.js       # Chart.js visual configurations
│       └── voice.js           # Speech Synthesis / Recognition
│
└── templates/
    ├── index.html             # Landing page
    ├── chatbot.html           # Conversation screen
    ├── login.html             # Admin portal sign-in
    ├── admin.html             # FAQ Management page
    ├── analytics.html         # Live logs and trends chart
    ├── about.html             # Architecture specification
    ├── 404.html               # Page Not Found
    └── 500.html               # Internal Server Error
```

---

## Local Setup & Installation

### Prerequisites
- Python 3.8 or higher installed on your local computer.

### Step-by-Step Setup
1. **Clone or copy this project folder**:
   ```bash
   cd c:\Users\Tarik\Desktop\CHATBOT222
   ```

2. **Create and Activate a Virtual Environment** (Recommended):
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   *Note: NLTK resources (`punkt`, `stopwords`, `wordnet`, `omw-1.4`) will be downloaded automatically on the first run.*

4. **Launch the Application**:
   ```bash
   python app.py
   ```
   *The console will show that the SQLite database has been initialized, seed data has been imported, and the NLP vectorizer is trained.*

5. **Open in Browser**:
   Navigate to `http://localhost:5000` to interact with the application.

---

## Administrator Credentials

- **Default Username**: `admin`
- **Default Password**: `admin123`
*You can configure custom values using environment variables or by editing the `config.py` file.*

---

## Deployment Guide

### 1. Docker Setup
To run the application locally inside a containerized Docker container:
```bash
# Build the image
docker build -t faq-chatbot .

# Run the container mapping port 5000
docker run -p 5000:5000 --name faq-chatbot-container -e SECRET_KEY="your-custom-key" faq-chatbot
```

### 2. Pushing to GitHub
1. Create a new repository on your GitHub account.
2. Run the following commands in the project folder root:
   ```bash
   git init
   git add .
   git commit -m "Initial commit of FAQ Chatbot"
   git branch -M main
   git remote add origin https://github.com/your-username/your-repo-name.git
   git push -u origin main
   ```

### 3. Deploying to Render
1. Connect your GitHub account to [Render](https://render.com).
2. Click **New +** and select **Blueprint**.
3. Link your chatbot repository. Render will automatically parse the `render.yaml` file and provision the web service.
4. If deploying manually as a **Web Service**:
   - Environment: `Python`
   - Build Command: `pip install -r requirements.txt && python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('omw-1.4')"`
   - Start Command: `gunicorn app:app`

### 4. Deploying to Railway
1. Sign in to [Railway](https://railway.app).
2. Click **New Project** -> **Deploy from GitHub repo**.
3. Select your chatbot repository. Railway will detect the `Dockerfile` or the `Procfile` automatically and deploy.
4. Set required variables in the **Variables** tab (e.g. `PORT` = `8080`, `SECRET_KEY`).

---

## Custom Domain & SSL Setup

### Setting Custom Domains
On Render or Railway:
1. Navigate to the **Settings** tab of your deployed Web Service.
2. Look for **Custom Domains** and click **Add Custom Domain**.
3. Input your domain name (e.g., `chatbot.yourdomain.com`).
4. Configure DNS records on your domain registrar (e.g., GoDaddy, Cloudflare, Namecheap):
   - Add a `CNAME` record pointing to the Render/Railway default URL (e.g., `faq-chatbot.onrender.com`).
   - If using a root domain, add an `A` record pointing to the destination IP address provided by the host.

### SSL Encryption
Both Render and Railway offer **automated, free SSL certificates** via Let's Encrypt. Once your DNS records propagate (which can take anywhere from 10 minutes to 24 hours), your custom domain will automatically serve requests securely over HTTPS (`https://chatbot.yourdomain.com`).
