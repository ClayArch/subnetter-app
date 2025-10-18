# Subnetter

A fast, accurate IPv4 subnet calculator built with Python and Streamlit.

**Live App:** https://subnetter.streamlit.app

## Features

- Calculate subnet information from IP address + CIDR/dotted mask
- View network address, broadcast address, host range, and usable hosts
- Support for special cases (/31 point-to-point links, /32 single hosts)
- Download results as CSV
- Reference guide with common subnet masks and info
- Clean, responsive UI

## Getting Started

### Prerequisites

- Python 3.8+
- pip

### Installation

1. Clone the repository:
```bash
git clone https://github.com/ClayArch/subnetter-app.git
cd subnetter-app
```

2. Create a virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Mac/Linux
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running Locally

```bash
streamlit run subnetter/ui/app.py
```

The app will open at `http://localhost:8501`

## Project Structure

```
subnetter-app/
├── subnetter/
│   ├── core/
│   │   └── calculator.py       # Subnet calculation logic
│   └── ui/
│       └── app.py              # Streamlit UI
├── tests/                       # Unit tests
├── .streamlit/
│   └── config.toml             # Streamlit configuration
├── requirements.txt            # Python dependencies
└── README.md
```

## Usage

1. Enter an IP address (with or without CIDR notation)
2. If needed, enter a subnet mask
3. Click "Calculate"
4. View results across three categories: Network Info, Host Range, and Additional Info
5. Download results as CSV if needed

## Examples

- `192.168.1.0/24`
- `192.168.1.10 255.255.255.0`
- `10.0.0.0/8`
- `172.16.0.1 /16`

## Development

### Creating a Feature Branch

```bash
git checkout -b feature/your-feature
# Make changes, commit, and push
git push origin feature/your-feature
```

Create a pull request to merge into `develop`, then `main` for production.

### Dependencies

- `streamlit` — Web UI framework
- `pandas` — Data manipulation for results table

## Deployment

This app is deployed on Streamlit Cloud. Push changes to `main` branch to trigger automatic deployment.

## License

MIT License

## Contributing

Feel free to open issues or submit pull requests for improvements.