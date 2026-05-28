# Overview

- Built for passive intelligence gathering across four vectors:
- IP geolocation, phone number analysis, username enumeration across social platforms, and heuristic-based risk scoring.
- It runs entirely offline in its analytical logic no external AI APIs, no data exfiltration, no hidden network calls beyond the ones you explicitly trigger from the menu.

<img width="1029" height="520" alt="frontendosint" src="https://github.com/user-attachments/assets/8f134574-dfd7-40b4-958f-3cbcf63841c6" />



# Requirements

- Python 3.7+
- requests
- phonenumbers

- No other dependencies. All risk scoring, pattern matching, geolocation accuracy estimation, and anomaly detection are implemented in pure Python with stdlib modules ***(re, math, ipaddress, datetime, json)***.

# Installation

        git clone https://github.com/Alb4don/PhantomTrack.git
        
        cd PhantomTrack
        
        pip install requests phonenumbers

- On Windows, use python instead of python3 if your PATH maps the interpreter that way. The tool detects ***os.name == 'nt' and calls cls automatically***; no additional configuration is needed for terminal color support on Windows Terminal or PowerShell with ANSI enabled.

# Usage

        python3 phantom_track.py

- Phone numbers should be entered in international format with ***the + prefix for best accuracy***
- IP addresses are validated via Python's ipaddress module before any network request is made. Malformed input is rejected with an error message rather than forwarded to the API.

# Disclaimer

- Phantom Track is provided for use in authorized security research, digital investigations, fraud analysis, and educational contexts. The author is not responsible for the misuse or illegal use of the tool.
