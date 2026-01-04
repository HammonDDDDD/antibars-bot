# Lab4
## Overview
Lab4 is a Telegram bot module that implements both synchronous and asynchronous functionality for monitoring Google Sheets data changes and providing information services. The module features concurrent processing capabilities for efficient data retrieval and notification delivery, integrating multiple external APIs including Telegram Bot API, OpenWeatherMap, and web scraping services.

## Purpose
The module serves as a notification system that periodically scans configured Google Sheets spreadsheets for data modifications and sends real-time alerts to subscribed Telegram users. It provides additional utility functions including weather information retrieval, news headline fetching, and daily quote services. The system maintains subscription management through a database backend and supports both immediate and scheduled monitoring operations with concurrent processing for optimal performance.