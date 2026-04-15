Modified version of: https://github.com/fastfingertips/lastfm-rpc

Main objective was to display artist, title and release year within Discord status. <br>
Example: <br>
<img width="313" height="60" alt="image" src="https://github.com/user-attachments/assets/5cd09618-76df-4dd1-9f3f-938ab13f556f" />

### Key Improvements
- **MusicBrainz Integration**: This fork uses the MusicBrainz API to fetch accurate release years for your tracks.
- **Deep Search Engine**: Implemented a recursive search for artists where standard API calls often fail due to regional formatting or specific tags.
- **Advanced Regex Cleaning**: Automatically strips messy track titles (removes "Album Ver.", "(Instrumental)", etc.) before searching, ensuring much higher hit rates.
- **Smart Discord Formatting**: Updates the Discord Presence to a cleaner, professional look: `Artist • Track Title (Year)`.
- **Anti-Ban Cache**: Added an in-memory caching system for MusicBrainz to prevent rate-limiting and protect your IP during long sessions.
    
# Last.fm Discord Rich Presence (RPC)

A modern, localized, and lightweight Discord Rich Presence client for Last.fm. Show off what you're listening to with custom statistics and artwork.

### Features
- **Real-time Sync**: Updates your Discord status as soon as you change tracks on Last.fm.
- **Full Localization**: Support for English, Turkish, and Spanish.
- **Dynamic Configuration**: Change settings (Username, API Keys, Language) on the fly without restarting.
- **Smart Tracking**: Displays scrobble counts, artist stats, and "Loved" status.
- **Auto-Update Checker**: Stay notified when a new version is released.
- **Modern Stack**: Managed with `uv` for lightning-fast environment setup.

### Demo
https://github.com/user-attachments/assets/396ef42b-7929-4dac-b8d2-ce43172470f7

---

### Quick Start (Recommended)

1. **Clone the Repository**
   ```bash
   git clone https://github.com/jqn17/last-fm-rpc-with-realease-year.git
   cd lastfm-rpc
   ```
2. **Configuration & API Setup**

All settings are stored in `config.yaml`.
You have to manually insert your last.fm API data into the file mentioned above:
- **Last.fm API Key/Secret**: [Create them here](https://www.last.fm/api/account/create) or [view existing ones](https://www.last.fm/api/accounts).
- **Last.fm Username**: Your public profile name.

3. **Install with Python**
    ```bash
    pip install .
    python main.py
    ``

### License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
