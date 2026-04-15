import logging
import re
import requests
import time
import pylast  # <-- TEGO BRAKOWAŁO!
import musicbrainzngs
import constants.project as project

YEAR_CACHE = {}

logger = logging.getLogger('lastfm')

# --- KONFIGURACJA MUSICBRAINZ ---
musicbrainzngs.set_useragent("MyDiscordRPC", "1.0", "contact@example.com")

class User:
    def _get_corrected_data_from_lastfm(self, artist, title):
        try:
            # Używamy biblioteki pylast, która już jest w Twoim projekcie
            track = self.network.get_track(artist, title)
            # track.get_correction() zapyta Last.fm o poprawną nazwę
            corrected_track = track.get_correction()
            
            if corrected_track:
                # Pobieramy poprawione dane
                c_artist = corrected_track.get_artist().get_name()
                # Próbujemy wyciągnąć album z poprawionego utworu
                c_album = corrected_track.get_album()
                c_album_name = c_album.get_name() if c_album else None
                return c_artist, c_album_name
        except Exception as e:
            print(f"[LFM-DEBUG] Błąd autokorekty: {e}")
        return artist, None

    def _get_release_year_mb(self, artist, album, title=None):
        # 0. SPRAWDZENIE CACHE (Zanim cokolwiek zrobimy)
        cache_key = f"{artist} - {title}"
        if cache_key in YEAR_CACHE:
            return YEAR_CACHE[cache_key], "Cache"

        if not artist or artist == "Unknown Artist":
            return None, None
        
        import requests
        import re
        import time

        # 1. ANTY-BAN: Czekamy, żeby MB nas nie zablokowało
        time.sleep(1.5)
        
        # 2. PRZYGOTOWANIE DANYCH
        title_no_brackets = re.sub(r'\(.*?\)', '', str(title)).strip()

        def clean_text(text):
            if not text: return ""
            cleaned = re.sub(r'[^a-zA-Z0-9\s\uac00-\ud7a3]', ' ', str(text))
            return ' '.join(cleaned.split()).strip()

        c_artist = re.sub(r'[\uac00-\ud7a3]+', '', str(artist)).strip()
        c_title = clean_text(title_no_brackets)
        
        if not c_title:
            c_title = clean_text(title)

        # 3. KONFIGURACJA ZAPYTANIA (Zmień maila na swój!)
        url_rec = "https://musicbrainz.org/ws/2/recording/"
        headers = {'User-Agent': 'KpopRPC_Jaqn/1.0 (twoj_mail@gmail.com)'}
        params = {
            "query": f'artist:({c_artist}) AND recording:({c_title})',
            "fmt": "json",
            "limit": 5
        }

        try:
            response = requests.get(url_rec, params=params, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('recordings'):
                    for rec in data['recordings']:
                        date = rec.get('first-release-date', '')
                        if not date and rec.get('releases'):
                            for release in rec['releases']:
                                date = release.get('date', '')
                                if date: break

                        match = re.search(r'\d{4}', str(date))
                        if match:
                            found_year = match.group(0)
                            # ZAPISUJEMY DO CACHE przed zwróceniem
                            YEAR_CACHE[cache_key] = found_year
                            return found_year, "MusicBrainz (Deep Search)"

        except Exception as e:
            logger.error(f"[MB-ERROR] Błąd: {e}")

        return None, None

        # --- LOGIKA WYSZUKIWANIA ---
        
        # PRÓBA 1: Po Artyście i tytule Albumu (np. AKMU + 개화)
        print(f"[MB-DEBUG] Szukam albumu: Artysta='{c_artist}', Album='{c_album_query}'")
        year = fetch_from_mb(f'artist:"{c_artist}" AND {c_album_query}')
        
        # PRÓBA 2: RATUNKOWA (Jeśli album ma inną nazwę, szukamy po tytule piosenki)
        if not year and c_title_query:
            print(f"[MB-DEBUG] Nie znaleziono albumu. Próba ratunkowa piosenką: '{c_title_query}'")
            # Szukamy wydania, które zawiera dany utwór
            year = fetch_from_mb(f'artist:"{c_artist}" AND "{c_title_query}"')

        if year:
            return year, "MusicBrainz"
            
        return None, None

    def __init__(self, username, cooldown=None):
        from constants.project import API_KEY, API_SECRET, DEFAULT_COOLDOWN
        self.username = username
        self.cooldown = cooldown if cooldown is not None else DEFAULT_COOLDOWN
        
        # Initialize network with current keys
        self.network = pylast.LastFMNetwork(API_KEY, API_SECRET)
        self.lastfm_user = self.network.get_user(username)
        
        self.last_track = None
        self.last_track_info = None

    def _get_current_track(self):
        try:
            return self.lastfm_user.get_now_playing()
        except pylast.WSError as e:
            if "Invalid API key" in str(e):
                logger.critical("CRITICAL: Invalid API Key. Please update config.yaml with a valid key from Last.fm.")
                import os
                os._exit(1)
            logger.error(f"{project.TRANSLATIONS['pylast_ws_error'].format(self.cooldown)} | Details: {e}")
        except pylast.NetworkError:
            logger.error(project.TRANSLATIONS['pylast_network_error'])
        except pylast.MalformedResponseError:
            logger.error(project.TRANSLATIONS['pylast_malformed_response_error'])
        return None

    def _get_track_info(self, current_track):
        import re
        # Inicjalizacja zmiennych
        title, artist, album, artwork, time_remaining = "Unknown Title", "Unknown Artist", "Unknown Album", None, 0
        release_year = None
        
        try:
            # 1. Pobieranie podstaw (Tytuł i Artysta)
            title = current_track.get_title() or "Unknown Title"
            artist_obj = current_track.get_artist()
            artist = artist_obj.get_name() if artist_obj else "Unknown Artist"
            
            # 2. Pobranie obiektu Albumu
            album_obj = current_track.get_album()
            if album_obj:
                album = album_obj.get_name() or "Unknown Album"
                artwork = album_obj.get_cover_image()

            # --- SZUKANIE ROKU ---
            
            # KROK A: MusicBrainz
            logger.info(f"[DEBUG] Próba pobrania roku dla: {artist} - {album}")
            try:
                # Wywołujemy funkcję przez self.
                release_year, source = self._get_release_year_mb(artist, album, title=title)
                
                if release_year:
                    logger.info(f"[YEAR-FOUND] Sukces! Rok: {release_year} | Źródło: {source}")
                else:
                    logger.warning(f"[YEAR-MISSING] Nie znaleziono roku dla: {artist} - {album}")
            except Exception as e:
                logger.error(f"[YEAR-ERROR] Błąd podczas szukania roku: {e}")
                release_year, source = None, None

            # KROK B: Jeśli MB zawiedzie, szukamy w Wiki (Last.fm)
            if not release_year and album_obj:
                try:
                    wiki = album_obj.get_wiki_published()
                    if wiki:
                        found = re.search(r'\b(19\d{2}|20\d{2})\b', str(wiki))
                        if found:
                            release_year = found.group(1)
                            source = "Last.fm (Wiki)" # Zapamiętujemy skąd mamy rok
                except:
                    pass

            # KROK C: Tagi (Ostatnia deska ratunku)
            if not release_year:
                try:
                    top_tags = current_track.get_top_tags(limit=10)
                    for tag in top_tags:
                        t_name = str(tag.item.get_name())
                        found_tag = re.search(r'\b(19\d{2}|20\d{2})\b', t_name)
                        if found_tag:
                            release_year = found_tag.group(1)
                            source = "Last.fm (Tags)" # Zapamiętujemy skąd mamy rok
                            break
                except:
                    pass
            
            # --- TU WPISUJEMY LOG DO KONSOLI ---
            if release_year:
                logger.info(f"[DEBUG] Rok {release_year} znaleziony przez: {source}")

        except Exception as e:
            logger.debug(f"Błąd w track_info: {e}")
            
        return str(title), str(artist), str(album), artwork, time_remaining, release_year

    def now_playing(self):
        current_track = self._get_current_track()
        
        if current_track:
            if self.last_track and str(current_track) == str(self.last_track):
                return current_track, self.last_track_info
                
            info = self._get_track_info(current_track)
            self.last_track = current_track
            self.last_track_info = info
            return current_track, info
        else:
            self.last_track = None
            self.last_track_info = None
            logger.debug(project.TRANSLATIONS['no_song'].format(self.cooldown))
            return current_track, None