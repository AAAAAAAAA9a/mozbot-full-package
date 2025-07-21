# Mozbot Full Package

A comprehensive chatbot platform with multiple components including admin panel, widget, backend API, and WordPress plugin integration.

## Project Structure

```
mozbot-full-package/
├── .gitignore                          # Main Git ignore file
├── setup_and_run.sh                   # Setup and deployment script  
├── README.md                           # This file
└── mozbot-project/
    └── mozbot-platform-configured/
        └── home/ubuntu/upload/
            ├── mozbot-admin/           # React admin dashboard
            ├── mozbot-backend/         # Python Flask API
            ├── mozbot-widget/          # React widget component  
            └── mozbot-wordpress-plugin/ # WordPress plugin
```

## Components

### 🎛️ Mozbot Admin (`mozbot-admin/`)
- **Tech Stack**: React 19, Vite, TailwindCSS, Radix UI
- **Purpose**: Administrative dashboard for managing chatbots
- **Package Manager**: pnpm
- **Key Features**: 
  - Chatbot management
  - Analytics dashboard  
  - User interface components

### 🤖 Mozbot Widget (`mozbot-widget/`)
- **Tech Stack**: React 19, Vite, TailwindCSS
- **Purpose**: Embeddable chat widget
- **Package Manager**: pnpm
- **Key Features**:
  - Responsive chat interface
  - Customizable themes
  - Easy website integration

### 🔧 Mozbot Backend (`mozbot-backend/`)
- **Tech Stack**: Python, Flask, SQLAlchemy, JWT
- **Purpose**: REST API and database management
- **Key Features**:
  - User authentication
  - Chatbot configuration API
  - Conversation management
  - Automation services

### 🔌 Mozbot WordPress Plugin (`mozbot-wordpress-plugin/`)
- **Tech Stack**: PHP, WordPress
- **Purpose**: WordPress integration plugin
- **Key Features**:
  - Easy WordPress integration
  - Admin interface
  - Analytics tracking

## Getting Started

### Prerequisites
- Node.js (v18+)
- Python (v3.8+)
- pnpm package manager
- Git

### Quick Setup
```bash
# Clone the repository
git clone <your-repo-url>
cd mozbot-full-package

# Run the setup script
chmod +x setup_and_run.sh
./setup_and_run.sh
```

### Manual Setup

#### Frontend (Admin & Widget)
```bash
# Navigate to admin
cd mozbot-project/mozbot-platform-configured/home/ubuntu/upload/mozbot-admin
pnpm install
pnpm dev

# Navigate to widget  
cd ../mozbot-widget
pnpm install
pnpm dev
```

#### Backend
```bash
# Navigate to backend
cd mozbot-project/mozbot-platform-configured/home/ubuntu/upload/mozbot-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python src/main.py
```

## Development

### Frontend Development
- Both admin and widget use **Vite** for fast development
- **TailwindCSS** for styling with custom components
- **Radix UI** for accessible component primitives
- **React Router** for navigation

### Backend Development  
- **Flask** with SQLAlchemy ORM
- **JWT** authentication
- **CORS** enabled for frontend integration
- **Modular architecture** with services and routes

### WordPress Plugin
- Standard WordPress plugin structure
- Admin interface integration
- Hook-based architecture

## Deployment

The project includes a `setup_and_run.sh` script for automated deployment. This script:
- Sets up all required dependencies
- Configures the database
- Starts all services
- Handles environment configuration

## Environment Variables

Create `.env` files in the respective directories:

**Backend** (`mozbot-backend/.env`):
```env
FLASK_ENV=development
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///instance/mozbot.db
JWT_SECRET_KEY=your-jwt-secret
```

**Frontend** (`.env.local`):
```env
VITE_API_URL=http://localhost:5000
VITE_APP_TITLE=Mozbot Admin
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is private and proprietary.

## Support

For support and questions, please contact the development team.
