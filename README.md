📁 Smart File & Video Processor
A smart and lightweight Flask web application that lets you:

🔄 Convert file formats (PDF ↔️ DOCX, PNG ↔️ JPG, etc.)

🎬 Upload videos and automatically generate captions/subtitles using AI-based speech recognition

🚀 One platform, multiple utilities — fast, simple, and powerful.

🌟 Features
✅ File Format Conversion
Convert between document types like:

.docx, .pdf, .png, .jpg, .txt

✅ Video Captioning

Upload a video file (.mp4, .mov, etc.)

Audio is extracted and converted to text using speech recognition

Captions are displayed instantly or downloadable

✅ Multi-File Upload Support
✅ Clean UI with Instant Feedback
✅ No External API Required – Fully works offline (locally)

🛠️ Tech Stack
Frontend:

HTML, CSS (Jinja2 templates)

Backend:

Python Flask

Libraries Used:

moviepy – Video and audio processing

speech_recognition – Speech-to-text conversion

PyDub – Audio format conversion

python-docx, PyPDF2, Pillow – File manipulation

🚀 How to Run Locally
Clone the Repository

bash
Copy
Edit
git clone https://github.com/MohammedRayan11/SmartFileVideoProcessor.git
cd SmartFileVideoProcessor
Create a Virtual Environment

bash
Copy
Edit
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install Dependencies

bash
Copy
Edit
pip install -r requirements.txt
Run the App

bash
Copy
Edit
python app.py
Open in browser:
http://127.0.0.1:5000

📂 Folder Structure
cpp
Copy
Edit
├── static/
│   └── style.css
├── templates/
│   ├── index.html
│   ├── result.html
├── uploads/
├── app.py
├── requirements.txt
└── README.md
🎯 Use Cases
✅ Students converting and submitting files in correct formats

✅ Content creators auto-generating captions for their videos

✅ Professionals managing documents and media from one tool

🤝 Contributing
Pull requests are welcome! If you’d like to add features (like real-time caption download or support for more formats), feel free to fork and collaborate.

📄 License
This project is open-source and available under the MIT License.
