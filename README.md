# 🌱 GrowGuide — Smart Crop Advisor

> AI-powered crop recommendation system that helps farmers choose the right crop based on soil and climate conditions.

🔗 **Live Demo:** [growguide-1.onrender.com](https://growguide-1.onrender.com)

---

## 📖 About

GrowGuide is an intelligent agricultural assistant designed to bridge the gap between farming knowledge and technology. Whether you're a seasoned farmer or just starting out, GrowGuide helps you make data-driven crop decisions by analyzing key soil and climate parameters — either through plain English descriptions or precise numeric values.

---

## ✨ Features

### 🌾 Smart Crop Recommendation
- **Natural Language Input** — Describe your farm in plain English (e.g., *"my soil is slightly acidic and I get moderate rainfall"*) and GrowGuide extracts the relevant features automatically.
- **Manual Value Entry** — Enter exact values for Nitrogen (N), Phosphorus (P), Potassium (K), Temperature, Humidity, Soil pH, and Rainfall.
- **Top 3 Recommendations** — Get ranked crop suggestions with confidence scores.

### 💬 Agriculture Chat Assistant
- Ask questions about crops, soil health, irrigation, fertilizers, and pest control.
- Context-aware responses tailored to farming needs.
- Example prompts:
  - *"Best crop for January?"*
  - *"How to improve soil nitrogen?"*
  - *"Irrigation tips for rice?"*
  - *"How to control pests organically?"*

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python (Flask / FastAPI) |
| ML Model | Scikit-learn (Crop Recommendation Model) |
| AI Assistant | Claude / LLM API |
| Deployment | Render |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/PranoyRoy2004/GrowGuide.git
cd GrowGuide

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

The app will be available at `http://localhost:5000`.

---

## 🧪 How It Works

### Crop Advisor
1. Choose between **Natural Language** or **Manual Input** mode.
2. Describe your farm conditions or enter numeric values for soil & climate parameters.
3. The ML model analyses the data and returns the **top recommended crop** along with 2 alternatives.
4. Click through to the Chat Assistant to learn more about the recommended crop.

### Input Parameters (Manual Mode)

| Parameter | Range |
|-----------|-------|
| Nitrogen (N) | 0 – 140 |
| Phosphorus (P) | 5 – 145 |
| Potassium (K) | 5 – 205 |
| Temperature (°C) | Variable |
| Humidity (%) | Variable |
| Soil pH | 3.5 – 9.9 |
| Rainfall (mm) | Variable |

---

## 📁 Project Structure

```
GrowGuide/
├── static/
│   ├── css/
│   └── js/
├── templates/
│   ├── index.html       # Crop Advisor page
│   └── chat.html        # Chat Assistant page
├── model/
│   └── crop_model.pkl   # Trained ML model
├── app.py               # Main application entry point
├── requirements.txt
└── README.md
```

---

## 🌍 Deployment

This project is deployed on **Render**. To deploy your own instance:

1. Push your code to GitHub.
2. Create a new **Web Service** on [render.com](https://render.com).
3. Connect your GitHub repository.
4. Set the build command to `pip install -r requirements.txt` and start command to `python app.py`.
5. Deploy!

---

## 🤝 Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

## 👨‍💻 Author

**Pranoy Roy**
- GitHub: [@PranoyRoy2004](https://github.com/PranoyRoy2004)

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

<p align="center">Made with ❤️ for farmers and the future of agriculture</p>
