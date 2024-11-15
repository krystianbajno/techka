# T E C H K A
[![CodeFactor](https://www.codefactor.io/repository/github/krystianbajno/techka/badge)](https://www.codefactor.io/repository/github/krystianbajno/techka)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/282b115765ec479f91259778c0eccdc7)](https://app.codacy.com/gh/krystianbajno/techka/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)
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
git clone https://github.com/krystianbajno/techka-secret
```

## License
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Fkrystianbajno%2Ftechka.svg?type=large)](https://app.fossa.com/projects/git%2Bgithub.com%2Fkrystianbajno%2Ftechka?ref=badge_large)

> [Direct -> Collect -> Process -> Analyze -> Disseminate -> Feedback -> Repeat](https://media.defcon.org/DEF%20CON%2032/DEF%20CON%2032%20presentations/DEF%20CON%2032%20-%20Tom%20Cross%20Greg%20Conti%20-%20Deception%20%26%20Counter%20Deception%20-%20Defending%20Yourself%20in%20a%20World%20Full%20of%20Lies.pdf)
