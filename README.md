# 📁 File & Capyion AI Tools

A smart and lightweight **Flask web application** that allows users to:
- 🔄 Convert file formats (PDF ↔️ DOCX, PNG ↔️ JPG, etc.)
- 🎬 Upload videos and automatically generate **captions/subtitles** using AI-based speech recognition

> 🚀 One platform, multiple utilities — fast, simple, and powerful.

---

## 🌟 Features

✅ **File Format Conversion**  
- Convert between `.docx`, `.pdf`, `.png`, `.jpg`, `.txt`, and more

✅ **Video Captioning**  
- Upload video files (`.mp4`, `.mov`, etc.)
- Automatically extract and transcribe audio into subtitles using speech recognition

✅ **Multi-File Upload Support**  
✅ **Clean UI with Instant Feedback**  
✅ **Offline & Privacy-Friendly** – Runs locally without needing external APIs

---

## 🛠️ Tech Stack

**Frontend**:
- HTML, CSS (Jinja2 templating)

**Backend**:
- Python (Flask)

**Libraries Used**:
- `moviepy` – For audio/video processing  
- `speech_recognition` – For speech-to-text  
- `PyDub` – Audio format handling  
- `PyPDF2`, `python-docx`, `Pillow` – File conversions

---

## 🚀 How to Run Locally

```bash
# 1. Clone the Repository
git clone https://github.com/MohammedRayan11/SmartFileVideoProcessor.git
cd SmartFileVideoProcessor

# 2. Create a Virtual Environment
python -m venv venv
# Activate the virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. Install Required Packages
pip install -r requirements.txt

# 4. Run the Flask App
python app.py
```

Open your browser and go to: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 📁 Folder Structure

```
SmartFileVideoProcessor/
├── app.py
├── requirements.txt
├── static/
│   └── style.css
├── templates/
│   ├── index.html
│   ├── result.html
├── uploads/
└── README.md
```

---

## 💡 Use Cases

- 🎓 Students converting and submitting assignments
- 📹 Content creators generating captions for videos
- 🧑‍💼 Professionals managing various file types with ease

---

## 🤝 Contributing

Pull requests are welcome! Feel free to fork this repo and submit improvements or additional features like:
- 📄 Real-time downloadable subtitle files
- 📁 Support for more formats (e.g., `.xlsx`, `.pptx`)
- 🖼️ Drag and drop UI enhancements

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

> Developed with 💻 and 🔥 by Mohammed Rayan  
> Let’s simplify file processing with intelligence.

