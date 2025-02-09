# Warframe Data Scraper

A Python script that scrapes detailed weapon information from the Warframe Wiki and generates structured JSON data.

## Description

This tool automatically extracts weapon information from the [Warframe Wiki](https://wiki.warframe.com), including:
- Basic weapon details (name, mastery rank, weapon type, etc.)
- Acquisition methods
- Foundry requirements
- Prime part drop locations (for Prime weapons)

### Coming Soon:
- Prime Grid
- Warframes Data

## Prerequisites

- Python 3.6+
- pip (Python package installer)

## Installation

1. Clone this repository:

```bash
git clone https://github.com/yourusername/warframe-weapon-scraper.git
cd warframe-weapon-scraper
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

```bash
python3 src/scrape_weapons.py
```

## Output

The script will create a JSON file in the `data` directory with the following structure:

```json
{
    "weapons": [
        {
            "name": "Name of the weapon",
            "mastery": "Mastery rank of the weapon",
            "weapon_type": "Type of weapon",
            "max_rank": "Maximum rank of the weapon",
            "slot": "Slot of the weapon",
            "acq_text": "Acquisition description text of the weapon",
            "acq_table": [
                {
                    "text": "Text of the acquisition table",
                    "location": "Location of the acquisition table"
                }
            ],
            "foundry_table": [
                {
                    "resource": "Resource of the foundry table",
                    "amount": "Amount of the resource"
                }
            ],
            "prime_parts": [
                {
                    "name": "Name of the prime part",
                    "location": "Location of the prime part"
                }
            ]
        }
    ]
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License.


