# 📦 Inventory System v1.0.0

An enterprise-grade **Inventory & Sales Management System** built with **Python (CustomTkinter)** to help store owners efficiently manage products, track sales, and monitor profitability.

## 🌟 Features

- **Product Management**: Full CRUD operations for inventory items
- **Sales Tracking**: Record sales with automatic profit calculation
- **Dashboard**: Real-time metrics and alerts for low stock/expired items
- **Reporting**: Export sales and inventory reports to Excel
- **Data Integrity**: Automatic backups and migration system
- **Enterprise Ready**: Comprehensive logging, monitoring, and error handling

## 🏗️ Architecture

```
inventory_system/
│
├── app/
│   ├── ui/              # CustomTkinter UI components
│   ├── services/        # Business logic layer
│   ├── database/        # Database operations & migrations
│   ├── utils/           # Validators, helpers, logging
│   ├── config/          # Configuration management
│
├── tests/               # Comprehensive test suite
├── scripts/             # Build and deployment scripts
├── installer/           # Inno Setup installer
├── assets/              # Static assets
├── logs/                # Application logs (auto-generated)
├── backups/             # Database backups (auto-generated)
│
├── main.py              # Application entry point
├── requirements.txt     # Python dependencies
├── pyproject.toml      # Project configuration
├── .env.example        # Environment variables template
└── README.md           # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/mohammed91so/magazine-management-system
   cd magazine-management-system
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

## 📖 Usage

### Dashboard
- View real-time metrics (earnings, profit, investment)
- Monitor alerts for low stock and expired products
- Refresh data with one click

### Products
- Add new products with purchase/selling prices
- Update existing product information
- Delete products (with confirmation)
- View complete inventory list

### Sales
- Select products from dropdown
- Enter quantity to sell
- View profit preview before confirming
- Track sales history

### Reports
- Export sales reports to Excel
- Export inventory snapshots
- Generate combined reports

## 🔧 Development

### Running Tests

```bash
pytest --cov=. --cov-report=html
```

### Code Quality

```bash
# Format code
black .
isort .

# Lint code
pylint **/*.py
```

### Building Executable

```bash
python scripts/build.py
```

### Creating Installer

```bash
# Requires Inno Setup
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\inventory_system.iss
```

## 📊 Data Management

### Database

- **Location**: `inventory.db` (auto-created on first run)
- **Backups**: Automatic daily backups in `backups/` directory
- **Migrations**: Auto-applied on startup

### Logs

- **App Log**: `logs/app.log` (INFO level)
- **Error Log**: `logs/error.log` (ERROR level)
- **Rotation**: 10MB max, 5 backups retained

## 🔒 Security

- Input validation on all user inputs
- SQL injection prevention (parameterized queries)
- Graceful error handling
- Data integrity checks
- Automatic backups

## 📝 Configuration

Environment variables (`.env` file):

```env
ENVIRONMENT=development
DB_NAME=inventory.db
DB_BACKUP_DIR=backups
LOG_LEVEL=INFO
LOG_DIR=logs
APP_NAME=Inventory System
APP_VERSION=1.0.0
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

For issues, questions, or contributions, please open an issue on the repository.

## 🔄 Version History

- **v1.0.0** (2026) - Initial enterprise release
  - Full CRUD operations
  - Sales tracking
  - Dashboard with metrics
  - Excel reporting
  - Automated backups
  - Comprehensive testing
  - CI/CD pipeline

