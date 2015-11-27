# Chatopoly
IRC game based on Monopoly implemented as a Cardinal plugin.

## Installation
First, get Cardinal and follow the associated instructions for setting it up.
Once you have Cardinal working successfully, install the Chatopoly plugin:

    cd plugins
    git clone https://github.com/Derecho/chatopoly.git
    pip install -r chatopoly/requirements.txt

In Cardinal's config.json, you'll need to add `chatopoly` under `plugins`. 
You may also find it handy to remove most of the other plugins to stop them
from being loaded and interfering with the game. `admin` and `help` are useful
plugins to keep.
