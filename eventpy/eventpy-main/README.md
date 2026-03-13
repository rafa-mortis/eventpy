# 🌍 Reciclagem REEE

Plataforma para gestão de pontos de recolha de Resíduos de Equipamentos Elétricos e Eletrónicos (REEE) em Lisboa.

## 🚀 Quick Start

### **Simple Setup (3 commands):**
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Setup database
python scripts/create_tables.py
python scripts/init_admin.py
python scripts/init_waste_types.py

# 3. Start application
python app.py
```

That's it! The application will be available at http://localhost:5000

## 📧 Email Configuration (Optional)

To enable email validation, edit `.env`:
```env
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
```

Create App Password: https://myaccount.google.com/apppasswords

## 🔑 Default Login

- **Email**: admin@reciclagem.pt
- **Password**: admin123

## 📁 Project Structure

```
eventpy-main/
├── 📄 app.py              # Main Flask application
├── 📄 models.py           # Database models
├── 📄 requirements.txt    # Python dependencies
├── 📄 .env               # Environment variables
├── 📁 config/            # Configuration files
├── 📁 scripts/           # Utility scripts
├── 📁 templates/         # HTML templates
├── 📁 static/           # Static files (CSS, JS, images)
├── 📁 data/             # Database file
└── 📁 docs/             # Documentation
```

## 🌐 Access

- **Application**: http://localhost:5000
- **Search**: http://localhost:5000/pesquisa
- **Admin**: http://localhost:5000/admin

## 🛠️ Features

- ✅ **Interactive Map** - 854+ collection points
- ✅ **Advanced Search** - Filter by location and waste type
- ✅ **User Registration** - Email validation
- ✅ **Admin Panel** - Manage points and users
- ✅ **Contact Form** - User feedback system
- ✅ **Responsive Design** - Works on all devices

## 📊 Database

- **SQLite** database (file-based, no server needed)
- **854 collection points** across Lisbon
- **10 waste types** for proper classification
- **User management** with validation

## 🔧 Development

```bash
# Test email configuration
python scripts/setup_email.py test

# Check database content
python scripts/check_data.py

# Create new admin user
python scripts/criar_admin.py
```

## 📝 Requirements

- **Python 3.8+**
- **pip** package manager
- **Web browser** (Chrome, Firefox, Safari, Edge)

## 🎯 About

This platform helps citizens in Lisbon find proper disposal locations for electronic waste, promoting environmental sustainability and proper recycling practices.

---

**Made with ❤️ for a greener Lisbon** 🌱
