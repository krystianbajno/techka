# T E C H K A
[![CodeFactor](https://www.codefactor.io/repository/github/krystianbajno/techka/badge)](https://www.codefactor.io/repository/github/krystianbajno/techka)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/282b115765ec479f91259778c0eccdc7)](https://app.codacy.com/gh/krystianbajno/teczunia/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)
![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Fkrystianbajno%2Ftechka.svg?type=shield&issueType=security)
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Fkrystianbajno%2Ftechka.svg?type=shield)](https://app.fossa.com/projects/git%2Bgithub.com%2Fkrystianbajno%2Ftechka?ref=badge_shield)

T E C H K A draws from the Polish word "teczka", meaning "briefcase," which traditionally holds important documents. The name reflects the project's focus on organizing and uncovering valuable open-source intelligence (OSINT) to transform the unknown into the known.
 
```
T E C H K A v4.20.69 - 2024

⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⣞⣄⣠⢤⡤⠄⠐⢦⡴⠀⣲⣿⣄⣀⣀⠠⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠠⣀⣴⠾⠞⠻⣿⣿⣈⢤⣤⣦⣡⣷⣷⡿⣿⣷⣾⣟⡥⣿⣲⣠⢄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⡀⠀⠀⣀⣤⡶⠟⠃⠁⣀⣠⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣾⣹⠟⢏⣆⡀⡀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⣼⣯⣿⣎⣀⣠⣴⣿⢟⣯⡿⣿⡟⠉⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣖⡝⢸⣡⡀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢀⣞⡟⠋⢰⣾⣿⣿⣿⣿⡿⠙⠋⠀⢠⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣝⣇⠦⡀⠀⠀⠀
⠀⠀⠀⠀⠰⣾⡏⡀⣶⣿⣿⣿⣿⣿⡏⠀⠀⠀⠀⢸⣿⣿⣿⣿⠇⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣾⣿⣷⣁⠀⠀⠀
⠀⠀⠀⠂⡄⢁⣼⣿⣿⣿⣿⣟⡷⡏⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⠀⠀⣼⣿⣿⡿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣏⠳⡛⣿⣧⠀⠀
⠈⢾⣷⣾⢾⣷⣿⣿⣿⣿⣿⣭⣿⠀⠀⠀⠀⠀⠀⠘⣿⣿⣿⣿⣿⣷⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢎⢧⡼⣧⢻⢾⠀
⠀⠀⠉⠛⠿⣷⣿⣿⣿⠟⠉⠱⣧⣄⠀⠀⠀⠀⠀⠀⠙⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡋⠈⠇⡐⢬⡝⡏⡀
⠀⠀⠀⠈⠄⣒⢷⢶⡫⢮⣚⡯⢙⠫⠡⠀⠀⠀⠀⠀⠀⠈⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⣯⢾⡽⣯⣼⣻⢻⢿⠻
⠀⠀⠀⠀⠈⠋⠀⣾⣵⢬⠱⢈⡁⡅⠇⠐⠃⠂⢖⠄⠀⣀⠀⠈⡙⢿⠿⣿⠿⣿⠿⡿⠿⠫⢹⢉⡠⡀⢍⠀⠈⠈⠀⠈⡈⠀
⠀⠀⠀⠀⠀⣴⡞⣿⣿⣼⢻⠛⡞⠙⢳⢪⣿⣿⢳⠛⡎⠐⡍⠀⠈⠁⡄⠀⠀⠀⠀⠁⠀⠀⠀⠀⠀⠀⡄⠒⠀⠊⠀⠀⠀⠀
⠀⠀⠀⠀⠐⠙⠉⠩⢚⣦⡿⠛⠗⠋⠋⠉⠉⠁⠰⠋⠈⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠚⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀

.45 huh? Incredible.

T E C H K A v4.20.69 - 2024
```

# Installation

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install
cd rust_bindings
maturin build --release
pip install target/wheels/*.whl

cd plugins
git clone https://github.com/krystianbajno/techka-secret # nothing interesting here hahah 😈
```

# Usage
I created this tool for my own use, and I’m not going to explain how it works. However, feel free to explore and use it as you wish.
```bash
python3 techka.py --full-help # display help for every possible module
```

# Plugin development
You are free to develop plugins for this tool as it is extremely modular - recon-ng and metasploit-like. In order to develop a plugin:

1. Create directory in `plugins` directory.
2. Implement all methods extended from `plugins/plugin_base.py` in `handler.py` just like other plugins.
3. It should work automagically out of the box.

## License
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Fkrystianbajno%2Ftechka.svg?type=large)](https://app.fossa.com/projects/git%2Bgithub.com%2Fkrystianbajno%2Ftechka?ref=badge_large)