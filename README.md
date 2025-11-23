Inkle Multi-Agent Tourism System

This project is a small tourism assistant website that uses a multi-agent architecture to provide weather information and nearby tourist attractions for any searched location.

Agents Used

Parent Tourism Agent – Reads user request and decides which child agent to call.

Weather Agent – Fetches live temperature and rain probability using the Open-Meteo API.

Places Agent – Suggests up to 5 nearby tourist spots using Overpass / OpenStreetMap.

Location Validator (Geocoding) – Uses LocationIQ to avoid fake/non-existent places.

Features

Live weather and rain percentage

Tourist attraction suggestions

Error handling for unknown places

Clean and simple web UI (Flask)

Secure API key using .env
