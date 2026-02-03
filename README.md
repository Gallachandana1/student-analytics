# Edulytics AI - Student Success Platform 🎓📊

**Edulytics AI** is an intelligent student performance prediction and analytics platform designed to help educators identify at-risk students and improve retention rates using Machine Learning.

![Edulytics AI Logo](frontend/img/logo.svg)

## 🚀 Features

-   **AI Performance Prediction**: Uses a Random Forest classifier to predict student success probabilities in real-time.
-   **Interactive Dashboard**: Visualizes key metrics like attendance, study hours, and performance distributions.
-   **Risk Assessment**: Automatically categorizes students into Low, Medium, and High risk groups.
-   **Data Management**: Supports CSV uploads and exports for large student datasets.
-   **Factor Analysis**: Visualizes feature importance to understand what drives student success.

## 🛠️ Tech Stack

-   **Frontend**: HTML5, CSS3, JavaScript (Vanilla), Chart.js
-   **Backend**: Python, Flask, Pandas, NumPy, Scikit-learn
-   **Database**: SQLite
-   **AI/ML**: Random Forest Classifier

## 📦 Installation & Setup

1.  **Clone the repository**
    ```bash
    git clone https://github.com/yourusername/edulytics-ai.git
    cd edulytics-ai
    ```

2.  **Install Dependencies**
    ```bash
    pip install flask flask-cors pandas numpy scikit-learn
    ```

3.  **Run the Application**
    ```bash
    cd backend
    python app.py
    ```

4.  **Access the Dashboard**
    Open your browser and navigate to `http://localhost:5000`

## 📊 Enhancements

-   **Smart Alerts**: Intelligent insights based on prediction inputs (e.g., "Low attendance detected").
-   **Modern UI**: Clean, responsive interface with glassmorphism effects.
-   **Data Persistence**: SQLite database integration for reliable data storage.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---
_Developed by [Your Name]_
