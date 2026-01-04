# antibars-bot

---

![License](https://img.shields.io/github/license/HammonDDDDD/antibars-bot?style=flat&logo=opensourceinitiative&logoColor=white&color=blue)
[![OSA-improved](https://img.shields.io/badge/improved%20by-OSA-yellow)](https://github.com/aimclub/OSA)

---

## Overview

This Telegram bot provides automated monitoring of Google Sheets data changes, particularly useful for tracking student grades. It notifies subscribed users about updates while also offering additional features like weather information and daily content. The solution helps users stay informed about important data changes through convenient messaging platform integration.

---

## Table of Contents

- [Core Features](#core-features)
- [Installation](#installation)
- [Contributing](#contributing)
- [License](#license)
- [Citation](#citation)

---

## Core Features

1. **Telegram Bot Integration**: Asynchronous Telegram bot that handles multiple command types including weather information, daily quotes, news headlines, and subscription management with real-time message processing
2. **Google Sheets Monitoring**: Automated monitoring of multiple Google Sheets for changes in student grades and data, with configurable polling intervals and change detection capabilities
3. **Subscription Management System**: Database-driven subscription system that allows users to subscribe to specific identifiers (ISU numbers or names) and receive notifications when monitored data changes
4. **Change Detection and Notification**: Advanced change detection algorithm that compares current spreadsheet data with previous state and sends formatted notifications when updates are detected
5. **Asynchronous Background Monitoring**: Concurrent background task that continuously monitors data sources while simultaneously handling user interactions through the Telegram interface

---

## Installation

Install antibars-bot using one of the following methods:

**Build from source:**

1. Clone the antibars-bot repository:
```sh
git clone https://github.com/HammonDDDDD/antibars-bot
```

2. Navigate to the project directory:
```sh
cd antibars-bot
```

3. Install the project dependencies:
```sh
pip install -r requirements.txt
```

---

## Contributing

- **[Report Issues](https://github.com/HammonDDDDD/antibars-bot/issues)**: Submit bugs found or log feature requests for the project.

- **[Submit Pull Requests](https://github.com/HammonDDDDD/antibars-bot/tree/main/.github/CONTRIBUTING.md)**: To learn more about making a contribution to antibars-bot.

---

## License

This project is protected under the MIT License. For more details, refer to the [LICENSE](https://github.com/HammonDDDDD/antibars-bot/tree/main/LICENSE) file.

---

## Citation

If you use this software, please cite it as below.

### APA format:

    HammonDDDDD (2025). antibars-bot repository [Computer software]. https://github.com/HammonDDDDD/antibars-bot

### BibTeX format:

    @misc{antibars-bot,
        author = {HammonDDDDD},
        title = {antibars-bot repository},
        year = {2025},
        publisher = {github.com},
        journal = {github.com repository},
        howpublished = {\url{https://github.com/HammonDDDDD/antibars-bot.git}},
        url = {https://github.com/HammonDDDDD/antibars-bot.git}
    }

---