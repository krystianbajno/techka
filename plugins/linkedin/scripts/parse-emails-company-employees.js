const users = document.querySelectorAll('.artdeco-entity-lockup__title');

function replacePolishChars(text) {
  const polishToAscii = {
    'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l', 'ń': 'n',
    'ó': 'o', 'ś': 's', 'ż': 'z', 'ź': 'z',
    'Ą': 'A', 'Ć': 'C', 'Ę': 'E', 'Ł': 'L', 'Ń': 'N',
    'Ó': 'O', 'Ś': 'S', 'Ż': 'Z', 'Ź': 'Z'
  };

  return text.split('').map(char => polishToAscii[char] || char).join('');
}

let outputs = {};
outputs["f.lastname"] = []
outputs["flastname"] = []
outputs["firstname.lastname"] = []
outputs["firstnamelastname"] = []
outputs["lastname"] = []

for (const user of users) {
  let name = replacePolishChars(user.innerText).toLowerCase();
  let firstnameLastname = name.split(" ");
  if (firstnameLastname.length >= 2) {

    outputs["f.lastname"].push(`${firstnameLastname[0][0]}.${firstnameLastname[1]}`);
    outputs["flastname"].push(`${firstnameLastname[0][0]}${firstnameLastname[1]}`);
    outputs["firstname.lastname"].push(`${firstnameLastname[0]}.${firstnameLastname[1]}`);
    outputs["firstnamelastname"].push(`${firstnameLastname[0]}${firstnameLastname[1]}`);
    outputs["lastname"].push(`${firstnameLastname[1]}`);
  }
}

for (const key in outputs) {
    const blob = new Blob([output[key].join('\n')], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `usernames-${key}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

