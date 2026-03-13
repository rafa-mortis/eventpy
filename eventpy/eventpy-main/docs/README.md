# EventPy - Event Management System

A Flask-based event management and ticketing system built with Python.

## Features

- Event creation and management
- User registration and authentication
- Ticket purchasing with different pricing tiers
- Shopping cart functionality
- PDF invoice generation
- QR code ticket generation
- Admin dashboard
- Email notifications

## Installation

### Prerequisites

- Python 3.8+
- pip package manager

### Setup Instructions

1. **Clone or download the project**
   ```bash
   cd eventpy-main
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` file with your configuration:
   ```
   SECRET_KEY=your-secret-key-here-change-this-in-production
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-password
   ```

4. **Initialize the database**
   ```bash
   python create_tables.py
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   Open your browser and navigate to: `http://127.0.0.1:5000`

## Project Structure

```
eventpy-main/
├── app.py              # Main Flask application
├── models.py           # Database models and CLI tools
├── database.py         # Database configuration
├── create_tables.py    # Database initialization script
├── test_app.py        # Application testing script
├── requirements.txt    # Python dependencies
├── .env.example      # Environment variables template
├── templates/         # HTML templates
│   ├── base.html     # Base template
│   ├── index.html    # Homepage
│   ├── eventos.html  # Events listing
│   ├── login.html    # User login
│   ├── registro.html # User registration
│   └── ...
├── static/           # Static files (CSS, JS, images)
└── data/            # SQLite database files
```

## Available Routes

- `/` - Homepage
- `/eventos` - Events listing with filters
- `/login` - User login
- `/registro` - User registration
- `/utilizador` - User dashboard
- `/carrinho` - Shopping cart
- `/admin` - Admin dashboard (requires admin privileges)

## Testing

Run the test suite to verify installation:

```bash
python test_app.py
```

This will test:
- All required imports
- Database connection and basic operations

## Database Management

The application includes a CLI tool for database management:

```bash
python models.py
```

Options:
1. List Events
2. Create New Event
3. Manage Seats/Stock
4. Exit

## Configuration

### Email Setup

To enable email functionality:
1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password
3. Update `.env` file with your credentials

### Database

The application uses SQLite by default. Database file is stored in `data/eventos.db`.

## Dependencies

- Flask - Web framework
- Flask-Bootstrap - UI components
- Flask-Mail - Email functionality
- Peewee - ORM
- python-dotenv - Environment variables
- xhtml2pdf - PDF generation
- qrcode - QR code generation
- Pillow - Image processing

## Troubleshooting

### Common Issues

1. **Bootstrap not loading**: Ensure you have internet connection for CDN links
2. **Database errors**: Run `python create_tables.py` to initialize
3. **Import errors**: Install dependencies with `pip install -r requirements.txt`
4. **Email not working**: Check Gmail App Password setup

### Port Already in Use

If port 5000 is occupied, modify `app.py`:

```python
if __name__ == "__main__":
    app.run(debug=True, port=5001)  # Change port here
```

## License

This project is for educational purposes.
