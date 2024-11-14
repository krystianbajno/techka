[![CodeFactor](https://www.codefactor.io/repository/github/krystianbajno/techka/badge)](https://www.codefactor.io/repository/github/krystianbajno/techka)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/282b115765ec479f91259778c0eccdc7)](https://app.codacy.com/gh/krystianbajno/techka/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)

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
